import cv2
import numpy as np
from PIL import Image
import imagehash
from skimage.metrics import structural_similarity as ssim

def preprocess_images(old_path, new_path):
    """Preprocess images to ensure they're comparable"""
    old_img = Image.open(old_path)
    new_img = Image.open(new_path)
    
    # Resize images to match
    size = (max(old_img.size[0], new_img.size[0]), max(old_img.size[1], new_img.size[1]))
    old_img = old_img.resize(size)
    new_img = new_img.resize(size)
    
    return old_img, new_img

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

def highlight_differences(old_img, new_img, diff):
    """Highlight differences between two images"""
    threshold = 0.1
    diff = (diff * 255).astype("uint8")
    thresh = cv2.threshold(diff, int(threshold * 255), 255, cv2.THRESH_BINARY_INV)[1]
    
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    
    mask = np.zeros(old_img.size[::-1], dtype="uint8")
    filled_after = np.array(new_img)
    
    for c in contours:
        area = cv2.contourArea(c)
        if area > 40:
            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), -1)
            cv2.rectangle(filled_after, (x, y), (x + w, y + h), (255, 0, 0), 1)
    
    return Image.fromarray(filled_after)