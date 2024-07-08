import argparse
import os
from pathlib import Path
import sys
from src.screenshot_capture import capture_screenshots
from src.openai_comparison import compare_screenshots_openai
from src.offline_comparison import compare_screenshots_offline
from dotenv import load_dotenv

src_path = Path(__file__).parent / 'src'
sys.path.append(str(src_path))

load_dotenv()

FOLDER_NEW = "screenshots/new"
FOLDER_OLD = "screenshots/old"

def clean_screenshots():
    for file in os.listdir(FOLDER_NEW):
        os.remove(os.path.join(FOLDER_NEW, file))
    for file in os.listdir(FOLDER_OLD):
        os.remove(os.path.join(FOLDER_OLD, file))
    print("All existing screenshots removed.")

def directory_is_empty(path):
    return not os.path.exists(path) or len(os.listdir(path)) == 0

def main():
    parser = argparse.ArgumentParser(description="Compare screenshots with option for OpenAI analysis")
    parser.add_argument("--openai", action="store_true", help="Use OpenAI for analysis")
    parser.add_argument("--mode", choices=['new', 'existing', 'clean'], default='existing', help="Screenshot handling mode")

    args = parser.parse_args()

    base_url = os.getenv("BASE_URL")
    old_release = os.getenv("OLD_RELEASE")
    new_release = os.getenv("NEW_RELEASE")
    
    if args.mode == 'clean':
        clean_screenshots()
        capture_screenshots(base_url, old_release, new_release)
    elif args.mode == 'new':
        capture_screenshots(base_url, old_release, new_release)
    elif args.mode == 'existing':
        if directory_is_empty(FOLDER_NEW) or directory_is_empty(FOLDER_OLD):
            print("Existing screenshots not found. Capturing new screenshots.")
            capture_screenshots(base_url, old_release, new_release)
    try:
        if args.openai:
            compare_screenshots_openai(FOLDER_NEW, FOLDER_OLD)
        else:
            compare_screenshots_offline(FOLDER_NEW, FOLDER_OLD)
    except Exception as e:
        return f"Comparison failed: {e}"

if __name__ == "__main__":
    main()