import os
from .image_utils import preprocess_images, compute_image_difference, create_difference_image

def compare_screenshots(old_path, new_path):
    old_img, new_img, old_gray, new_gray = preprocess_images(old_path, new_path)
    contours = compute_image_difference(old_gray, new_gray)
    result_image, differences = create_difference_image(new_img, contours)

    # Save the result
    diff_dir = "screenshots/diff"
    os.makedirs(diff_dir, exist_ok=True)
    diff_path = os.path.join(diff_dir, os.path.basename(new_path))
    result_image.save(diff_path)

    return differences

def compare_screenshots_offline(old_screenshots, new_screenshots):
    old_files = os.listdir(old_screenshots)
    new_files = os.listdir(new_screenshots)

    for old_file, new_file in zip(old_files, new_files):
        old_path = os.path.join(old_screenshots, old_file)
        new_path = os.path.join(new_screenshots, new_file)
        differences = compare_screenshots(old_path, new_path)
        
        print(f"Differences found in: {new_file}")
        for diff in differences:
            print(f"Type: {diff[4]}, Location: (x={diff[0]}, y={diff[1]}), Size: {diff[2]}x{diff[3]}")
        print()

