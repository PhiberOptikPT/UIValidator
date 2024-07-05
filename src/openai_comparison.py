import os
import openai
from dotenv import load_dotenv
from src.image_utils import preprocess_images, compare_images_hash, compare_images_ssim

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_with_openai(old_path, new_path):
    """Analyze images using OpenAI's GPT-4 with vision"""
    prompt = """
    Please analyse the attached images of two screens, one old and one new. 
    Enumerate the UI inconsistencies present in the new image that are not in the old image. 
    List the inconsistencies in bullet points only, with no additional text.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"file://{old_path}", "detail": "high"}},
                    {"type": "image_url", "image_url": {"url": f"file://{new_path}", "detail": "high"}}
                ],
            }
        ],
        max_tokens=300,
    )
    
    return response.choices[0].message['content']

def compare_screenshot_pair_openai(old_path, new_path):
    """Compare a pair of screenshots and analyze differences using OpenAI"""
    old_img, new_img = preprocess_images(old_path, new_path)
    
    hash_diff = compare_images_hash(old_img, new_img)
    print(f"Image hash difference for {os.path.basename(new_path)}: {hash_diff}")
    
    ssim_score, _ = compare_images_ssim(old_img, new_img)
    print(f"SSIM score for {os.path.basename(new_path)}: {ssim_score}")
    
    if hash_diff > 0.1 or ssim_score < 0.95:  # Adjust thresholds as needed
        inconsistencies = analyze_with_openai(old_path, new_path)
        print(f"UI Inconsistencies for {os.path.basename(new_path)}:")
        print(inconsistencies)
    else:
        print(f"No significant UI changes detected for {os.path.basename(new_path)}.")

def compare_screenshots_openai():
    old_dir = "screenshots/old"
    new_dir = "screenshots/new"
    
    for filename in os.listdir(new_dir):
        old_path = os.path.join(old_dir, filename)
        new_path = os.path.join(new_dir, filename)
        
        if os.path.exists(old_path):
            compare_screenshot_pair_openai(old_path, new_path)
        else:
            print(f"No old version found for {filename}")