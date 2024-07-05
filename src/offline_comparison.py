import os
from .image_utils import preprocess_images, compare_images_hash, compare_images_ssim, highlight_differences

def compare_screenshot_pair_offline(old_path, new_path):
    """Compare a pair of screenshots and analyze differences offline"""
    old_img, new_img = preprocess_images(old_path, new_path)
    
    hash_diff = compare_images_hash(old_img, new_img)
    print(f"Image hash difference for {os.path.basename(new_path)}: {hash_diff}")
    
    ssim_score, ssim_diff = compare_images_ssim(old_img, new_img)
    print(f"SSIM score for {os.path.basename(new_path)}: {ssim_score}")
    
    if hash_diff > 0.1 or ssim_score < 1:  # Adjust thresholds as needed
        diff_img = highlight_differences(old_img, new_img, ssim_diff)
        
        diff_dir = "screenshots/diff"
        os.makedirs(diff_dir, exist_ok=True)
        diff_path = os.path.join(diff_dir, f"diff_{os.path.basename(new_path)}")
        diff_img.save(diff_path)
        
        print(f"Differences detected. Diff image saved to: {diff_path}")
    else:
        print(f"No significant UI changes detected for {os.path.basename(new_path)}.")

def compare_screenshots_offline(old_screenshots, new_screenshots):
    old_files = os.listdir(old_screenshots)
    new_files = os.listdir(new_screenshots)

    for old_file, new_file in zip(old_files, new_files):
        old_path = os.path.join(old_screenshots, old_file)
        new_path = os.path.join(new_screenshots, new_file)
        compare_screenshot_pair_offline(old_path, new_path)