import anthropic
import base64
import os
import openai
from dotenv import load_dotenv
from src.image_utils import compare_images_hash, compare_images_ssim, preprocess_images
# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

MIN_HASH_DIFF=float(os.getenv("MIN_HASH_DIFF"))
MAX_SSIM_SCORE=float(os.getenv("MAX_SSIM_SCORE"))

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_openai(prompt, old_path, new_path):
    # Load and encode the images
    old_image_base64 = encode_image(old_path)
    new_image_base64 = encode_image(new_path)

    client = openai.OpenAI()

    response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert UI/UX analyst."},
                {"role": "user", "content": prompt},
                {"role": "system", "content": f"![old_image](data:image/jpeg;base64,{old_image_base64})"},
                {"role": "system", "content": f"![new_image](data:image/jpeg;base64,{new_image_base64})"}
            ],
            max_tokens=1000,
        )
    
    return response.choices[0].message['content']

def call_claude(prompt, old_path, new_path):
    # Load and encode the images
    old_image_base64 = encode_image(old_path)
    new_image_base64 = encode_image(new_path)

    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        system="You are an expert UI/UX analyst.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": prompt
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": old_image_base64
                        }
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": new_image_base64
                        }
                    }
                ]
            }
        ]
    )
    
    return message.content

def compare_screenshot_pair(old_path, new_path, ai):
    old_img, new_img = preprocess_images(old_path, new_path)
    
    hash_diff = compare_images_hash(old_img, new_img)
    ssim_score, _ = compare_images_ssim(old_img, new_img)  
    
    filename = os.path.basename(new_path)
    print(f"Comparing {filename}: Hash diff = {hash_diff:.4f}, SSIM score = {ssim_score:.4f}")

    if hash_diff > MIN_HASH_DIFF or ssim_score < MAX_SSIM_SCORE:  # Adjust thresholds as needed
        prompt = """
        Analyze the two attached screenshots: the first is the old version, the second is the new version.
        Focus on identifying UI changes and potential inconsistencies in the modernized version, paying particular attention to:

        1. Component positioning changes
        2. Spacing differences between components
        3. Alignment and spacing of labels relative to their associated elements
        4. Consistency in styling (colors, fonts, sizes) across similar elements
        5. Changes in element sizes or proportions
        6. Alterations in visual hierarchy or emphasis
        7. Modifications to navigation elements or user flow
        8. Consistency of modernized elements across different parts of the interface

        Please provide your analysis in the following format:
        1. List of Changes:
        - [List each significant change or inconsistency, focusing on the aspects mentioned above]
        2. Impact Assessment:
        - [Briefly assess the potential impact on user experience for each change]
        3. Recommendations:
        - [Provide any recommendations for improvement or maintaining consistency]

        Be concise and focus on the most important aspects. Ignore minor pixel-level differences unless they significantly impact the overall design consistency.
        """
    
        inconsistencies = ''

        if ai == 'openai':
            inconsistencies = call_openai(prompt, old_path, new_path)
        elif ai == 'claude':
            inconsistencies = call_claude(prompt, old_path, new_path)

        write_comparison_results(filename, hash_diff, ssim_score, inconsistencies)
        print(f"UI Inconsistencies found for {filename}!")
    else:
        write_comparison_results(filename, hash_diff, ssim_score)

def write_comparison_results(filename, hash_diff, ssim_score, inconsistencies=None):
    """Write comparison results to a file"""
    with open(f"screenshots/diff/{filename}.txt", 'w') as f:
        f.write(f"Analysis for {filename}:\n")
        f.write(f"Image hash difference: {hash_diff}\n")
        f.write(f"SSIM score: {ssim_score}\n")
        
        if inconsistencies:
            f.write("AI Analysis:\n")
            f.write(inconsistencies)
            f.write("\n")
        else:
            f.write("No significant UI changes detected.\n")
        
        f.write("\n")

def compare_screenshots_ai(old_screenshots, new_screenshots, ai):
    old_files = os.listdir(old_screenshots)
    new_files = os.listdir(new_screenshots)

    for old_file, new_file in zip(old_files, new_files):
        old_path = os.path.join(old_screenshots, old_file)
        new_path = os.path.join(new_screenshots, new_file)        
        compare_screenshot_pair(old_path, new_path, ai)