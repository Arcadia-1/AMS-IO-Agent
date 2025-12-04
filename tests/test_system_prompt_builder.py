from pathlib import Path
import sys
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.app.utils.system_prompt_builder import load_system_prompt_with_profile

def test_load_system_prompt_with_profile():
    """Test loading system prompt with profile"""
    # Build and display system prompt
    prompt = load_system_prompt_with_profile()
    assert isinstance(prompt, str), "load_system_prompt_with_profile should return a string"
    assert len(prompt) > 0, "System prompt should not be empty"
    print(f"{'=' * 80}\n{prompt}\n{'=' * 80}\nTotal: {len(prompt)} chars")

if __name__ == "__main__":
    test_load_system_prompt_with_profile()
