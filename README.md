# Screenshot Comparison Tool

This tool automates the process of capturing and comparing screenshots across different versions of a web application. It supports both offline comparison using image processing techniques and AI-powered analysis using OpenAI's GPT model.

## Features

- Automated screenshot capture using Selenium WebDriver
- Comparison of screenshots using perceptual hashing and structural similarity index (SSIM)
- Optional AI-powered analysis of UI changes using OpenAI's GPT model
- Offline comparison with visual difference highlighting
- Flexible screenshot handling modes (new, existing, clean)

## Prerequisites

- Python 3.7+
- Chrome WebDriver (for Selenium)
- OpenAI API key (for AI-powered analysis)

## Installation

1. Clone the repository:
    ```shell
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Create and activate a Python virtual environment:
    ```shell
    python -m venv venv
    ```

      On Windows:
      ```shell
      .\venv\Scripts\activate
      ```
    
      On macOS and Linux:
      ```shell
      source venv/bin/activate
      ```

  

3. Install the required dependencies:
    ```shell
    pip install -r requirements.txt
    ```

4. Set up environment variables:
Create a `.env` file in the project root and add the following:
    ```
    BASE_URL=<your_base_url>
    OLD_RELEASE=<old_release_path>
    NEW_RELEASE=<new_release_path>
    PORTAL_USERNAME=<your_username>
    PORTAL_PASSWORD=<your_password>
    SCREENSHOT_PATHS=<comma_separated_paths_to_screenshot>
    OPENAI_API_KEY=<your_openai_api_key>
    ```

## Usage

Run the main script with the desired options:
    ```shell
    python main.py [--openai] [--mode {new,existing,clean}]
    ```
Options:
- `--openai`: Use OpenAI for analysis (default is offline comparison)
- `--mode`: Screenshot handling mode
  - `new`: Capture new screenshots
  - `existing`: Use existing screenshots if available, otherwise capture new ones (default)
  - `clean`: Remove existing screenshots and capture new ones

## Project Structure

- `main.py`: Entry point of the application
- `src/`
  - `screenshot_capture.py`: Handles automated screenshot capture
  - `offline_comparison.py`: Performs offline screenshot comparison
  - `openai_comparison.py`: Performs AI-powered screenshot analysis
  - `image_utils.py`: Utility functions for image processing

## How It Works

1. The tool captures screenshots of specified pages for both old and new releases.
2. It then compares the screenshots using perceptual hashing and SSIM.
3. If significant differences are detected:
   - In offline mode, it generates a visual representation of the differences.
   - In OpenAI mode, it uses GPT to analyze and describe the UI inconsistencies.
4. Results are saved in the `screenshots/diff/` directory.