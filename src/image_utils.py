import cv2
import imagehash
import numpy as np
from skimage.metrics import structural_similarity as ssim
from PIL import Image, ImageDraw

def preprocess_images(old_path, new_path):
    """Preprocess images to ensure they're comparable"""
    old_img = cv2.imread(old_path)
    new_img = cv2.imread(new_path)
    old_gray = cv2.cvtColor(old_img, cv2.COLOR_BGR2GRAY)
    new_gray = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)
    return old_img, new_img, old_gray, new_gray

def compute_image_difference(old_gray, new_gray):
    (score, diff) = ssim(old_gray, new_gray, full=True)
    diff = (diff * 255).astype("uint8")
    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def analyze_difference(w, h):
    area = w * h
    aspect_ratio = w / h

    if area <= 100:  # Ignore very small differences
        return None

    if aspect_ratio > 5 or aspect_ratio < 0.2:
        return "Spacing change"
    elif 0.8 < aspect_ratio < 1.2:
        return "Element size change"
    else:
        return "Layout change"

def draw_difference(draw, x, y, w, h, diff_type):
    draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
    draw.text((x, y-20), diff_type, fill="red")

def create_difference_image(new_img, contours):
    result = Image.fromarray(cv2.cvtColor(new_img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(result)
    
    differences = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        diff_type = analyze_difference(w, h)
        if diff_type:
            differences.append((x, y, w, h, diff_type))
            draw_difference(draw, x, y, w, h, diff_type)
    
    return result, differences

# Bellow are the functions that are used in AI comparison
def compare_images_hash(old_img, new_img):
    """Compare images using perceptual hash"""
    old_hash = imagehash.average_hash(old_img)
    new_hash = imagehash.average_hash(new_img)
    
    return (old_hash - new_hash) / len(old_hash.hash) ** 2

def compare_images_ssim(old_img, new_img):
    """Compare images using Structural Similarity Index (SSIM)"""
    old_gray = cv2.cvtColor(np.array(old_img), cv2.COLOR_RGB2GRAY)
    new_gray = cv2.cvtColor(np.array(new_img), cv2.COLOR_RGB2GRAY)
    
    score, diff = ssim(old_gray, new_gray, full=True)
    return score, diff