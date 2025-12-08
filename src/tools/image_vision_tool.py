from typing import Optional, Dict, Any, List
import os
import base64
import json
import requests
import re
import glob
import uuid
import mimetypes
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from smolagents import tool
from .tool_utils import format_tool_logs, dual_stream_tool


# Load .env from repository root if present so tests/README env vars are available.
# Use find_dotenv() so the .env is discovered even if the current working directory
# isn't the repository root when this module is imported.
env_path = find_dotenv()
if env_path:
    load_dotenv(env_path)


def _get_config_from_env():
    """Get image API configuration from environment variables only.
    
    This function reads image API configuration from environment variables (typically set in .env file).
    It uses IMAGE_* prefixed variables to separate image API from language API configuration.
    It does NOT accept function parameters to ensure security and prevent sensitive data
    from being exposed in function calls.
    
    Returns:
        tuple: (api_base, api_key, model) or (None, None, None) if not found
        
    Environment variables (image API specific, in order of preference):
    - IMAGE_API_BASE: Image API base URL (required)
    - IMAGE_API_KEY: Image API key (required)
    - IMAGE_MODEL: Image model identifier (optional)
    """

    # Image API specific configuration (separate from language API)
    api_base = os.environ.get("IMAGE_API_BASE")
    api_key = os.environ.get("IMAGE_API_KEY")
    model = os.environ.get("IMAGE_MODEL")

    return api_base, api_key, model


def _encode_file_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("ascii")


def _detect_mime_type(path: Optional[str], fallback: str = "image/png") -> str:
    if path:
        mime, _ = mimetypes.guess_type(path)
        if mime:
            return mime
    return fallback


def _build_user_content(prompt: str, image_b64: str, mime_type: str) -> List[Dict[str, Any]]:
    data_url = f"data:{mime_type};base64,{image_b64}"
    content = [{"type": "image_url", "image_url": {"url": data_url}}]
    if prompt:
        content.insert(0, {"type": "text", "text": prompt})
    return content


def _get_or_create_output_dir(base: str = "output") -> str:
    """Return the latest timestamped subdir under `base` if present,
    otherwise create a new timestamped subdir and return it.

    Timestamp folder format: YYYYMMDD_HHMMSS
    """
    base_dir = os.path.abspath(base)
    os.makedirs(base_dir, exist_ok=True)

    # find existing timestamped directories like 20241218_143000
    candidates = []
    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        if os.path.isdir(path) and re.match(r"^\d{8}_\d{6}$", name):
            candidates.append(name)

    if candidates:
        latest = sorted(candidates)[-1]
        return os.path.join(base_dir, latest)

    # create a new timestamped directory
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    newdir = os.path.join(base_dir, ts)
    os.makedirs(newdir, exist_ok=True)
    return newdir


def _save_response_to_output(obj: Any, prefix: str = "image_vision_response") -> str:
    """Save a JSON-serializable object to the latest output timestamp directory.

    Returns the full path written to (or raises on write error).
    """
    outdir = _get_or_create_output_dir("output")
    filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.json"
    path = os.path.join(outdir, filename)
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=2)
    except Exception:
        # best-effort: if saving fails, just return an empty string
        return ""
    return path


def _extract_simplified_json(resp_json: Any) -> Optional[Dict[str, Any]]:
    """Try to extract a simplified/structured JSON object from the API response.

    The remote API may return a full response object or textual content that
    contains a JSON blob. This helper attempts several heuristics:
    - look for common keys that may already contain a dict or JSON string
    - inspect OpenAI-style `choices` / `message.content` fields for JSON
    - extract the first {...} JSON-like substring from text

    Returns a dict when extraction/parsing succeeds, otherwise None.
    """
    try:
        # If response is a dict, check for common keys
        if isinstance(resp_json, dict):
            for key in (
                "simplified_json",
                "simplify_json",
                "structured_json",
                "parsed_json",
                "simplified",
                "result",
                "data",
                "output",
                "json",
            ):
                if key in resp_json:
                    val = resp_json[key]
                    if isinstance(val, dict):
                        return val
                    if isinstance(val, str):
                        try:
                            return json.loads(val)
                        except Exception:
                            m = re.search(r"(\{[\s\S]*\})", val)
                            if m:
                                try:
                                    return json.loads(m.group(1))
                                except Exception:
                                    pass

        # OpenAI-style responses: choices -> message.content or text
        if isinstance(resp_json, dict) and "choices" in resp_json:
            choices = resp_json.get("choices")
            if isinstance(choices, list):
                for ch in choices:
                    content = None
                    if isinstance(ch, dict):
                        # Chat-style
                        if "message" in ch and isinstance(ch["message"], dict):
                            content = ch["message"].get("content")
                        # Completion-style
                        if content is None:
                            content = ch.get("text")
                        # Delta-style streaming
                        if content is None and isinstance(ch.get("delta"), dict):
                            content = ch["delta"].get("content")
                    if isinstance(content, str):
                        # try parse full content
                        try:
                            return json.loads(content)
                        except Exception:
                            m = re.search(r"(\{[\s\S]*\})", content)
                            if m:
                                try:
                                    return json.loads(m.group(1))
                                except Exception:
                                    pass

        # If response is plain text, try to extract a JSON substring
        if isinstance(resp_json, str):
            m = re.search(r"(\{[\s\S]*\})", resp_json)
            if m:
                try:
                    return json.loads(m.group(1))
                except Exception:
                    pass
    except Exception:
        # Best-effort: do not raise on heuristic failures
        return None

    return None


@dual_stream_tool
def analyze_image_path(
    image_path: str,
) -> Dict[str, Any]:
    """
    Analyze a local image by sending it to a remote multimodal API.

    This function encodes the image at `image_path` to base64 and POSTs a JSON payload
    to the configured remote endpoint. API configuration MUST be provided via environment
    variables (typically in .env file) for security reasons.

    Args:
        image_path (str): Local filesystem path to the image file to analyze.

    Returns:
        Dict[str, Any]: A dictionary with keys such as `status` ('ok' or 'error'),
            `tool` and `response` (the parsed JSON returned by the remote API) or
            error details when a failure occurs.
            
    Environment Variables Required (set in .env file):
        - IMAGE_API_BASE: Remote API base URL for image analysis (separate from language API)
        - IMAGE_API_KEY: Bearer token for the image API (separate from language API)
        - IMAGE_MODEL (optional): Model identifier for image analysis, defaults to "deepseek-chat" or "gpt-image-1"
        
    Example .env file:
        # Image API configuration (separate from language API)
        IMAGE_API_BASE=https://api.openai.com/v1
        IMAGE_API_KEY=sk-your-image-api-key-here
        IMAGE_MODEL=gpt-4o
        
        # Language API configuration (for main agent, separate from image API)
        OPENAI_API_BASE=https://api.openai.com/v1
        OPENAI_API_KEY=sk-your-language-api-key-here
    """
    try:
        if not os.path.exists(image_path):
            return format_tool_logs({"status": "error", "error": "file_not_found", "message": f"{image_path} does not exist"})

        api_base, api_key, model = _get_config_from_env()
        if not api_base or not api_key:
            return format_tool_logs({
                "status": "error", 
                "error": "missing_config", 
                "message": "Image API configuration not found in environment variables. Please set IMAGE_API_BASE and IMAGE_API_KEY in your .env file (separate from language API configuration)."
            })

        mime_type = _detect_mime_type(image_path)
        image_b64 = _encode_file_to_base64(image_path)
        # Load instruction content from default file
        instruction_content: Optional[str] = None
        default_instruction_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "image_vision_instruction.md"
        )
        if os.path.exists(default_instruction_path):
            try:
                with open(default_instruction_path, "r", encoding="utf-8") as fh:
                    instruction_content = fh.read()
            except Exception:
                # fail silently and continue without instruction
                instruction_content = None

        # Build URL: if api_base ends with /v1, add /chat/completions (OpenRouter/OpenAI format)
        if api_base.endswith("/v1") or api_base.endswith("/v1/"):
            url = api_base.rstrip("/") + "/chat/completions"
        elif "/chat/completions" in api_base:
            url = api_base
        else:
            # Use api_base directly as provided
            url = api_base
        
        # Determine if we should use chat format (default for OpenRouter/OpenAI)
        use_chat_format = (api_base and ("/chat" in api_base or "chat" in api_base)) or (model and "chat" in model) or True  # Default to chat format
        
        if use_chat_format:
            # build messages list using OpenAI-compatible format (OpenRouter supports this)
            messages = []
            if instruction_content:
                messages.append({"role": "system", "content": instruction_content})
            # Build user content with image in OpenAI format (data URI) - no text prompt needed, instruction is in system message
            user_content = _build_user_content("", image_b64, mime_type)
            messages.append({"role": "user", "content": user_content})
            payload = {
                "model": model or "openai/gpt-4o",
                "messages": messages,
            }
        else:
            # Legacy format (for non-OpenAI compatible APIs)
            final_prompt = instruction_content if instruction_content else ""
            payload = {
                "model": model or "gpt-image-1",
                "prompt": final_prompt,
                "image_b64": image_b64,
                "mime_type": mime_type,
            }
        
        # Build headers - OpenRouter supports optional HTTP-Referer and X-Title headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        # Add optional OpenRouter headers if provided via environment variables
        if os.environ.get("OPENROUTER_HTTP_REFERER"):
            headers["HTTP-Referer"] = os.environ.get("OPENROUTER_HTTP_REFERER")
        if os.environ.get("OPENROUTER_X_TITLE"):
            headers["X-Title"] = os.environ.get("OPENROUTER_X_TITLE")

        # If user selected a Gemini model (or requested via env), use Google GenAI client
        use_gemini = False
        if (model and isinstance(model, str) and model.lower().startswith("gemini")) or os.environ.get("USE_GEMINI") == "1":
            use_gemini = True

        if use_gemini:
            # Try to call Google GenAI per user sample: client.models.generate_content(...)
            try:
                genai_mod = __import__("google.genai", fromlist=["types", "Client", "client"])
            except Exception:
                try:
                    genai_mod = __import__("google.genai", fromlist=["types"])
                except Exception:
                    return format_tool_logs({"status": "error", "error": "missing_dependency", "message": "google.genai library not installed; pip install google-genai or follow provider docs"})

            types_mod = getattr(genai_mod, "types", None)
            ClientCls = getattr(genai_mod, "Client", None) or getattr(genai_mod, "client", None)
            try:
                client = ClientCls() if ClientCls else genai_mod
            except Exception:
                # fall back to using module as client if it exposes models
                client = genai_mod

            # prepare image bytes (decode from provided base64 string)
            try:
                image_bytes = base64.b64decode(image_b64)
            except Exception as e:
                return format_tool_logs({"status": "error", "error": "invalid_base64", "message": str(e)})

            # build contents list using types.Part.from_bytes if available
            contents = []
            if types_mod and hasattr(types_mod, "Part") and hasattr(types_mod.Part, "from_bytes"):
                try:
                    # use provided mime_type if available, otherwise default to image/png
                    mime = mime_type or "image/png"
                    contents.append(types_mod.Part.from_bytes(data=image_bytes, mime_type=mime))
                except Exception:
                    contents.append(image_bytes)
            else:
                contents.append(image_bytes)

            if instruction_content:
                contents.append(instruction_content)
            else:
                contents.append("Please generate a simplified JSON for IO ring based on the image.")

            try:
                response = client.models.generate_content(model=model, contents=contents)
            except Exception as e:
                return format_tool_logs({"status": "error", "error": "gemini_call_failed", "message": str(e)})

            # Try to extract text from response (best-effort)
            resp_text = getattr(response, "text", None) or getattr(response, "output", None) or str(response)
            resp_json = {"model": model, "gemini_raw": str(response), "text": resp_text}
            try:
                _save_response_to_output({"http_status": 200, "response": resp_json}, prefix="image_vision_response")
            except Exception:
                pass

            # Try to extract simplified JSON from response
            simplified = None
            saved_path = ""
            try:
                simplified = _extract_simplified_json(resp_json)
                if simplified:
                    try:
                        saved_path = _save_response_to_output(simplified, prefix="image_vision_simplified")
                    except Exception:
                        pass
            except Exception:
                simplified = None

            extra_fields = {"simplified": simplified}
            if simplified is not None:
                exec_payload = f"Simplified configuration extracted successfully. Saved to: {saved_path}"
            else:
                exec_payload = f"Image analysis completed. Response saved."
            # Return tuple for dual_stream_tool: (execution_log, full_log, extra_fields)
            return exec_payload, resp_json, extra_fields

        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
        try:
            resp_json = resp.json()
        except Exception as e:
            # save raw response text for debugging
            error_info = {
                "http_status": resp.status_code,
                "url": url,
                "headers": dict(resp.headers),
                "text": resp.text[:1000] if resp.text else "",  # Limit text length
                "json_error": str(e)
            }
            _save_response_to_output(error_info, prefix="image_vision_invalid_response")
            return format_tool_logs({
                "status": "error", 
                "error": "invalid_response", 
                "http_status": resp.status_code,
                "url": url,
                "message": f"Failed to parse JSON response: {str(e)}. Response preview: {resp.text[:200] if resp.text else 'Empty response'}"
            })

        # save successful JSON response for auditing/debugging
        try:
            _save_response_to_output({"http_status": resp.status_code, "response": resp_json}, prefix="image_vision_response")
        except Exception:
            pass

        # If response OK, attempt to extract a simplified/structured JSON
        simplified = None
        saved_path = ""
        try:
            if resp.status_code < 400:
                simplified = _extract_simplified_json(resp_json)
                if simplified:
                    try:
                        saved_path = _save_response_to_output(simplified, prefix="image_vision_simplified")
                    except Exception:
                        pass
        except Exception:
            # non-fatal: continue to return the normal response
            simplified = None

        if resp.status_code >= 400:
            return format_tool_logs({"status": "error", "error": "remote_api_error", "http_status": resp.status_code, "response": simplified})

        extra_fields = {"simplified": simplified}
        if simplified is not None:
            exec_payload = f"Simplified configuration extracted successfully. Saved to: {saved_path}"
        else:
            exec_payload = resp_json
        # Return tuple for dual_stream_tool: (execution_log, full_log, extra_fields)
        return exec_payload, resp_json, extra_fields

    except Exception as e:
        return format_tool_logs({"status": "error", "error": "exception", "message": str(e)})


@dual_stream_tool
def analyze_image_b64(
    image_b64: str,
    mime_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze an image provided as a base64 string by forwarding it to a remote API.

    Args:
        image_b64 (str): Base64-encoded image bytes or a data URI (e.g. 'data:image/png;base64,...').
        mime_type (Optional[str]): Optional MIME type hint for the image (e.g. 'image/png').

    Returns:
        Dict[str, Any]: A dictionary with keys such as `status` ('ok' or 'error'),
            `tool` and `response` (the parsed JSON returned by the remote API) or
            error details when a failure occurs.
            
    Environment Variables Required (set in .env file):
        - IMAGE_API_BASE: Remote API base URL for image analysis (separate from language API)
        - IMAGE_API_KEY: Bearer token for the image API (separate from language API)
        - IMAGE_MODEL (optional): Model identifier for image analysis, defaults to "deepseek-chat" or "gpt-image-1"
        
    Example .env file:
        # Image API configuration (separate from language API)
        IMAGE_API_BASE=https://api.openai.com/v1
        IMAGE_API_KEY=sk-your-image-api-key-here
        IMAGE_MODEL=gpt-4o
        
        # Language API configuration (for main agent, separate from image API)
        OPENAI_API_BASE=https://api.openai.com/v1
        OPENAI_API_KEY=sk-your-language-api-key-here
    """
    try:
        # strip data URI prefix if present
        if image_b64.startswith("data:"):
            # data:<mime>;base64,AAAA
            try:
                image_b64 = image_b64.split(",", 1)[1]
            except Exception:
                return format_tool_logs({"status": "error", "error": "invalid_data_uri"})

        mime_type = mime_type or "image/png"

        api_base, api_key, model = _get_config_from_env()
        if not api_base or not api_key:
            return format_tool_logs({
                "status": "error", 
                "error": "missing_config", 
                "message": "Image API configuration not found in environment variables. Please set IMAGE_API_BASE and IMAGE_API_KEY in your .env file (separate from language API configuration)."
            })

        # Load instruction content from default file
        instruction_content: Optional[str] = None
        default_instruction_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "image_vision_instruction.md"
        )
        if os.path.exists(default_instruction_path):
            try:
                with open(default_instruction_path, "r", encoding="utf-8") as fh:
                    instruction_content = fh.read()
            except Exception:
                instruction_content = None

        # Build URL: if api_base ends with /v1, add /chat/completions (OpenRouter/OpenAI format)
        if api_base.endswith("/v1") or api_base.endswith("/v1/"):
            url = api_base.rstrip("/") + "/chat/completions"
        elif "/chat/completions" in api_base:
            url = api_base
        else:
            # Use api_base directly as provided
            url = api_base
        
        # Determine if we should use chat format (default for OpenRouter/OpenAI)
        use_chat_format = (api_base and ("/chat" in api_base or "chat" in api_base)) or (model and "chat" in model) or True  # Default to chat format
        
        if use_chat_format:
            # Build messages using OpenAI-compatible format (OpenRouter supports this)
            messages = []
            if instruction_content:
                messages.append({"role": "system", "content": instruction_content})
            # Build user content with image in OpenAI format (data URI) - no text prompt needed, instruction is in system message
            user_content = _build_user_content("", image_b64, mime_type)
            messages.append({"role": "user", "content": user_content})
            payload = {
                "model": model or "openai/gpt-4o",
                "messages": messages,
            }
        else:
            # Legacy format (for non-OpenAI compatible APIs)
            final_prompt = instruction_content if instruction_content else ""
            payload = {
                "model": model or "gpt-image-1",
                "prompt": final_prompt,
                "image_b64": image_b64,
                "mime_type": mime_type,
            }
        
        # Build headers - OpenRouter supports optional HTTP-Referer and X-Title headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        # Add optional OpenRouter headers if provided via environment variables
        if os.environ.get("OPENROUTER_HTTP_REFERER"):
            headers["HTTP-Referer"] = os.environ.get("OPENROUTER_HTTP_REFERER")
        if os.environ.get("OPENROUTER_X_TITLE"):
            headers["X-Title"] = os.environ.get("OPENROUTER_X_TITLE")

        # If user selected a Gemini model (or requested via env), use Google GenAI client
        use_gemini = False
        if (model and isinstance(model, str) and model.lower().startswith("gemini")) or os.environ.get("USE_GEMINI") == "1":
            use_gemini = True

        if use_gemini:
            # Try to call Google GenAI per user sample: client.models.generate_content(...)
            try:
                genai_mod = __import__("google.genai", fromlist=["types", "Client", "client"])
            except Exception:
                try:
                    genai_mod = __import__("google.genai", fromlist=["types"])
                except Exception:
                    return format_tool_logs({"status": "error", "error": "missing_dependency", "message": "google.genai library not installed; pip install google-genai or follow provider docs"})

            types_mod = getattr(genai_mod, "types", None)
            ClientCls = getattr(genai_mod, "Client", None) or getattr(genai_mod, "client", None)
            try:
                client = ClientCls() if ClientCls else genai_mod
            except Exception:
                # fall back to using module as client if it exposes models
                client = genai_mod

            # prepare image bytes (decode from provided base64 string)
            try:
                image_bytes = base64.b64decode(image_b64)
            except Exception as e:
                return format_tool_logs({"status": "error", "error": "invalid_base64", "message": str(e)})

            # build contents list using types.Part.from_bytes if available
            contents = []
            if types_mod and hasattr(types_mod, "Part") and hasattr(types_mod.Part, "from_bytes"):
                try:
                    mime = mime_type or "image/png"
                    contents.append(types_mod.Part.from_bytes(data=image_bytes, mime_type=mime))
                except Exception:
                    contents.append(image_bytes)
            else:
                contents.append(image_bytes)

            if instruction_content:
                contents.append(instruction_content)
            else:
                contents.append("Please generate a simplified JSON for IO ring based on the image.")

            try:
                response = client.models.generate_content(model=model, contents=contents)
            except Exception as e:
                return format_tool_logs({"status": "error", "error": "gemini_call_failed", "message": str(e)})

            # Try to extract text from response (best-effort)
            resp_text = getattr(response, "text", None) or getattr(response, "output", None) or str(response)
            resp_json = {"model": model, "gemini_raw": str(response), "text": resp_text}
            try:
                _save_response_to_output({"http_status": 200, "response": resp_json}, prefix="image_vision_response")
            except Exception:
                pass

            # Try to extract simplified JSON from response
            simplified = None
            saved_path = ""
            try:
                simplified = _extract_simplified_json(resp_json)
                if simplified:
                    try:
                        saved_path = _save_response_to_output(simplified, prefix="image_vision_simplified")
                    except Exception:
                        pass
            except Exception:
                simplified = None

            extra_fields = {"simplified": simplified}
            if simplified is not None:
                exec_payload = f"Simplified configuration extracted successfully. Saved to: {saved_path}"
            else:
                exec_payload = f"Image analysis completed. Response saved."
            # Return tuple for dual_stream_tool: (execution_log, full_log, extra_fields)
            return exec_payload, resp_json, extra_fields

        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
        try:
            resp_json = resp.json()
        except Exception as e:
            # save raw response text for debugging
            error_info = {
                "http_status": resp.status_code,
                "url": url,
                "request_headers": dict(headers),
                "response_headers": dict(resp.headers),
                "text": resp.text[:2000] if resp.text else "",  # Limit text length
                "json_error": str(e),
                "content_type": resp.headers.get("Content-Type", "unknown")
            }
            _save_response_to_output(error_info, prefix="image_vision_invalid_response")
            
            # Try to extract useful error message from HTML response
            error_message = f"Failed to parse JSON response: {str(e)}"
            if resp.text and len(resp.text) > 0:
                # Check if it's HTML
                if resp.text.strip().startswith("<!DOCTYPE") or resp.text.strip().startswith("<html"):
                    error_message += ". Server returned HTML instead of JSON. This usually means the API endpoint URL is incorrect."
                else:
                    error_message += f". Response preview: {resp.text[:200]}"
            
            return format_tool_logs({
                "status": "error", 
                "error": "invalid_response", 
                "http_status": resp.status_code,
                "url": url,
                "message": error_message
            })

        # save successful JSON response for auditing/debugging
        try:
            _save_response_to_output({"http_status": resp.status_code, "response": resp_json}, prefix="image_vision_response")
        except Exception:
            pass

        # If response OK, attempt to extract a simplified/structured JSON
        simplified = None
        saved_path = ""
        try:
            if resp.status_code < 400:
                simplified = _extract_simplified_json(resp_json)
                if simplified:
                    try:
                        saved_path = _save_response_to_output(simplified, prefix="image_vision_simplified")
                    except Exception:
                        pass
        except Exception:
            simplified = None

        if resp.status_code >= 400:
            return format_tool_logs({"status": "error", "error": "remote_api_error", "http_status": resp.status_code, "response": simplified})
        extra_fields = {"simplified": simplified}
        
        if simplified is not None:
            exec_payload = f"Simplified configuration extracted successfully. Saved to: {saved_path}"
        else:
            exec_payload = resp_json
            
        # Return tuple for dual_stream_tool: (execution_log, full_log, extra_fields)
        return exec_payload, resp_json, extra_fields

    except Exception as e:
        return format_tool_logs({"status": "error", "error": "exception", "message": str(e)})

