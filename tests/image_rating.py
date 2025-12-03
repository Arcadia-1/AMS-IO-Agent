"""
IC Design I/O Ring Layout Image Rating Tool

This tool uses GPT-4o multimodal interface to rate IC design I/O ring layout images.
It can evaluate the correctness of ring formation, routing accuracy, and provide scores.

Usage Examples:
1. Rate a single image:
   python image_rating.py single test2.png
   
2. Rate the latest image in a folder:
   python image_rating.py latest /path/to/images
   
3. Batch rate all images in a folder:
   python image_rating.py batch /path/to/images output_results.txt
   
4. List all image files in a folder:
   python image_rating.py list /path/to/images
   
5. Default mode (rate test2.png if exists):
   python image_rating.py

Features:
- Supports multiple image formats: jpg, jpeg, png, gif, bmp, webp
- Provides detailed scoring (1-10 points) with explanations
- Generates comprehensive summary reports
- Handles batch processing with error handling
- Saves results to text files for analysis

Requirements:
- OpenAI API key (configured in the script)
- Valid internet connection for API calls
- Image files in supported formats

"""

import openai
import base64
import os
import glob
from pathlib import Path

# Set your OpenAI API key
# Method 1: Use third-party relay interface (recommended)
client = openai.OpenAI(
    api_key="sk-6pQ2rVvRxbdLDG0YYGI7A18eSjxn3AzhLYZvRVSsB6p8rWlL",
    base_url="https://api3.xhub.chat/v1"
)

def rate_image(image_path, prompt="This image is a simulated I/O ring layout in IC design. Please check if it forms a complete ring, whether the routing is correct, etc. Give a correctness score (1-10 points) and briefly explain the reason."):
    # Read image and convert to base64
    with open(image_path, "rb") as img_file:
        img_bytes = img_file.read()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    # Call GPT-4o multimodal interface
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional image rating assistant."},
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=500
    )

    # Output rating result
    return response.choices[0].message.content

def get_image_files(folder_path=".", extensions=None):
    """
    Get all image files in the folder
    
    Args:
        folder_path: Folder path, defaults to current directory
        extensions: List of supported image extensions, defaults to common formats
    
    Returns:
        List of image file paths
    """
    if extensions is None:
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp']
    
    image_files = set()  # Use set to avoid duplicates
    for ext in extensions:
        pattern = os.path.join(folder_path, ext)
        image_files.update(glob.glob(pattern))
        # Also search for uppercase extensions
        pattern_upper = os.path.join(folder_path, ext.upper())
        image_files.update(glob.glob(pattern_upper))
    
    return sorted(list(image_files))  # Convert to list and sort

def get_latest_image(folder_path=".", extensions=None):
    """
    Get the latest image file in the folder
    
    Args:
        folder_path: Folder path, defaults to current directory
        extensions: List of supported image extensions
    
    Returns:
        Latest image file path, returns None if not found
    """
    image_files = get_image_files(folder_path, extensions)
    if not image_files:
        return None
    
    # Sort by modification time, return the latest
    latest_file = max(image_files, key=os.path.getmtime)
    return latest_file

def batch_rate_images(folder_path=".", prompt=None, extensions=None):
    """
    Batch rate all images in the folder
    
    Args:
        folder_path: Folder path, defaults to current directory
        prompt: Rating prompt, uses default prompt if None
        extensions: List of supported image extensions
    
    Returns:
        List of rating results
    """
    if prompt is None:
        prompt = "This image is a simulated I/O ring layout in IC design. Please check if it forms a complete ring, whether the routing is correct, etc. Give a correctness score (1-10 points) and briefly explain the reason."
    
    image_files = get_image_files(folder_path, extensions)
    results = []
    
    print(f"Found {len(image_files)} image files, starting batch rating...")
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] Rating: {image_path}")
        try:
            result = rate_image(image_path, prompt)
            results.append({
                "file": image_path,
                "success": True,
                "result": result
            })
            print(f"Rating completed: {result}")  # Display full content
        except Exception as e:
            results.append({
                "file": image_path,
                "success": False,
                "error": str(e)
            })
            print(f"Rating failed: {str(e)}")
    
    return results

def extract_scores_from_results(results):
    """
    Extract scores from rating results
    
    Args:
        results: List of rating results
    
    Returns:
        List of scores
    """
    scores = []
    for result in results:
        if result['success']:
            # Try to extract numeric scores from results
            import re
            text = result['result']
            # Find numbers between 1-10
            score_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:points?|out of 10|/10)', text)
            if score_matches:
                try:
                    score = float(score_matches[0])
                    if 1 <= score <= 10:
                        scores.append(score)
                except ValueError:
                    pass
    return scores

def generate_summary(results):
    """
    Generate rating summary
    
    Args:
        results: List of rating results
    
    Returns:
        Summary string
    """
    summary = f"\n=== Batch Rating Summary ===\n"
    
    # List rating for each file
    summary += f"=== File Ratings ===\n"
    for result in results:
        if result['success']:
            scores = extract_scores_from_results([result])
            if scores:
                summary += f"- {result['file']}: {scores[0]} points\n"
            else:
                summary += f"- {result['file']}: Unable to extract score\n"
        else:
            summary += f"- {result['file']}: Rating failed\n"
    summary += "\n"
    
    # Score statistics
    scores = extract_scores_from_results(results)
    if scores:
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        
        summary += f"=== Score Statistics ===\n"
        summary += f"Average score: {avg_score:.2f}\n"
        summary += f"Highest score: {max_score}\n"
        summary += f"Lowest score: {min_score}\n"
        summary += f"Valid ratings: {len(scores)}\n"
    
    return summary

def save_results_to_file(results, output_file="rating_results.txt", folder_path="."):
    """
    Save rating results to file
    
    Args:
        results: List of rating results
        output_file: Output filename
        folder_path: Folder path where images are located
    """
    # Save to the same folder as the images
    if folder_path != ".":
        output_path = os.path.join(folder_path, output_file)
    else:
        output_path = output_file
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=== IC Design I/O Ring Layout Rating Results ===\n\n")
        
        # Write detailed results
        for result in results:
            f.write(f"File: {result['file']}\n")
            if result['success']:
                f.write(f"Rating result: {result['result']}\n")
            else:
                f.write(f"Error: {result['error']}\n")
            f.write("-" * 50 + "\n\n")
        
        # Write summary
        summary = generate_summary(results)
        f.write(summary)
    
    print(f"Results saved to: {output_path}")
    return summary

if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "single":
            # Single image rating mode
            if len(sys.argv) > 2:
                image_path = sys.argv[2]
            else:
                image_path = "test2.png"  # Default image
            
            print(f"Rating single image: {image_path}")
            result = rate_image(image_path)
            print("Rating result:", result)
            
        elif mode == "latest":
            # Latest image rating mode
            folder_path = sys.argv[2] if len(sys.argv) > 2 else "."
            latest_image = get_latest_image(folder_path)
            
            if latest_image:
                print(f"Found latest image: {latest_image}")
                result = rate_image(latest_image)
                print("Rating result:", result)
            else:
                print(f"No image files found in folder {folder_path}")
                
        elif mode == "batch":
            # Batch rating mode
            folder_path = sys.argv[2] if len(sys.argv) > 2 else "."
            output_file = sys.argv[3] if len(sys.argv) > 3 else "rating_results.txt"
            
            results = batch_rate_images(folder_path)
            summary = save_results_to_file(results, output_file, folder_path)
            
            # Display summary information
            print(summary)
            
        elif mode == "list":
            # List all image files
            folder_path = sys.argv[2] if len(sys.argv) > 2 else "."
            image_files = get_image_files(folder_path)
            
            print(f"Image files in folder {folder_path}:")
            for i, img in enumerate(image_files, 1):
                mod_time = os.path.getmtime(img)
                mod_time_str = os.path.getctime(img)
                print(f"{i}. {img} (Modification time: {mod_time_str})")
                
        else:
            print("Unknown mode, please use one of the following modes:")
            print("  single [image_path]     - Rate single image")
            print("  latest [folder_path]   - Rate latest image")
            print("  batch [folder_path] [output_file] - Batch rate all images")
            print("  list [folder_path]     - List all image files")
    else:
        # Default mode: rate single image
        print("=== IC Design I/O Ring Layout Rating Tool ===")
        print("Usage:")
        print("  python image_rating_gpt4o.py single [image_path]     - Rate single image")
        print("  python image_rating_gpt4o.py latest [folder_path]   - Rate latest image")
        print("  python image_rating_gpt4o.py batch [folder_path]    - Batch rate all images")
        print("  python image_rating_gpt4o.py list [folder_path]     - List all image files")
        print()
        
        # Default rating for test2.png
        image_path = "test2.png"
        if os.path.exists(image_path):
            print(f"Default rating image: {image_path}")
            result = rate_image(image_path)
            print("Rating result:", result)
        else:
            print(f"Default image {image_path} does not exist, please specify image path or use other mode")
    