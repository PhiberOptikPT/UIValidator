import anthropic
import base64
import os
import openai
from dotenv import load_dotenv
from src.image_utils import preprocess_images, compare_images_hash, compare_images_ssim

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_openai(prompt, old_path, new_path):
    # Load and encode the images
    old_image_base64 = encode_image(old_path)
    new_image_base64 = encode_image(new_path)

    client = openai.OpenAI()

    response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
                {"role": "system", "content": f"![old_image](data:image/jpeg;base64,{old_image_base64})"},
                {"role": "system", "content": f"![new_image](data:image/jpeg;base64,{new_image_base64})"}
            ],
            max_tokens=300,
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
        system=prompt,
        messages=[
            {
                "role": "user",
                "content": [
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
    print(f"Image hash difference for {os.path.basename(new_path)}: {hash_diff}")
    
    ssim_score, _ = compare_images_ssim(old_img, new_img)
    print(f"SSIM score for {os.path.basename(new_path)}: {ssim_score}")

    prompt = """
    Please analyse the attached images of two screens, one old and one new. 
    Enumerate the UI inconsistencies present in the new image that are not in the old image. 
    List the inconsistencies in bullet points only, with no additional text.
    """
    
    if hash_diff > 0.1 or ssim_score < 1:  # Adjust thresholds as needed
        inconsistencies = ''

        if ai == 'openai':
            inconsistencies = call_openai(prompt, old_path, new_path)
        elif ai == 'claude':
            inconsistencies = call_claude(prompt, old_path, new_path)

        filename = os.path.basename(new_path)

        write_comparison_results(filename, hash_diff, ssim_score, inconsistencies)
        print(f"UI Inconsistencies found for {filename}!")

def write_comparison_results(filename, hash_diff, ssim_score, inconsistencies=None):
    """Write comparison results to a file"""
    with open(f"screenshots/diff/{filename}.txt", 'a') as f:
        f.write(f"Results for {filename}:\n")
        f.write(f"Image hash difference: {hash_diff}\n")
        f.write(f"SSIM score: {ssim_score}\n")
        
        if inconsistencies:
            f.write("UI Inconsistencies:\n")
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