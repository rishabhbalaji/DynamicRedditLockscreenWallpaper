# ~/Main/Projects/DynamicRedditLockscreenWallpaper/wallpaper_updater.py

import os
from dotenv import load_dotenv
import praw
import requests
import random
import subprocess
import logging
import time
import sys

# --- Configuration ---
# Subreddits to pull images from (e.g., wallpapers, EarthPorn, CityPorn)
# You can add more subreddits here.
SUBREDDITS = [
    "wallpapers",
    "EarthPorn",
    "CityPorn",
    "NatureIsFuckingLit",
    "ImaginaryLandscapes",
    "SkyPorn",
    "SpacePorn",
    "WallpaperEngine",
    "wallpaper",
    "wallpaperhub",
    "wallpaperengine",
    "wallpaperart",
    "wallpaperaddicts",
    "wallpapercollection",
    "wallpaperhd",
    "wallpaperlovers",
    "wallpaperpics",
    "wallpaperporn",
    "wallpaperworld",
    "wallpaperzone",
    "wallpaper4k",
    "wallpaper4khd",
    "wallpaper4khdwallpapers",
    "wallpaper4khdwallpaper"]
# Minimum image width for posts (to ensure good quality for lockscreen)
MIN_IMAGE_WIDTH = 1920
# Minimum image height for posts
MIN_IMAGE_HEIGHT = 720 # Adjusted for more flexibility
# Directory to save downloaded wallpapers temporarily
WALLPAPER_DIR = "/tmp/reddit_wallpapers"
# Full path to betterlockscreen executable (usually in /usr/local/bin)
BETTERLOCKSCREEN_BIN = "/usr/local/bin/betterlockscreen"
# Path to a local directory for fallback wallpapers (optional)
# Ensure this directory exists and contains .jpg, .jpeg, or .png images.
LOCAL_FALLBACK_WALLPAPER_DIR = os.path.expanduser("~/Main/Pictures/Wallpapers")

TIMESTAMP_FILE = "/tmp/last_wallpaper_update.txt"

# --- Logging Setup ---
# Configure logging to see script's actions and debug issues
# Change level=logging.INFO to level=logging.DEBUG for more verbose output
logging.basicConfig(
    level=logging.DEBUG, # Set to DEBUG for verbose output during testing
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout) # Log to console
    ]
)
logger = logging.getLogger(__name__)

# --- Load Environment Variables ---
# This loads variables from your .env file
load_dotenv()

# Get Reddit API credentials from environment variables
reddit_username = os.getenv("REDDIT_USERNAME")
reddit_password = os.getenv("REDDIT_PASSWORD")
reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
reddit_user_agent = os.getenv("REDDIT_USER_AGENT")

# --- Basic Validation & PRAW Initialization ---
# Check if Reddit credentials are fully provided
reddit_credentials_provided = all([reddit_username, reddit_password, reddit_client_id, reddit_client_secret, reddit_user_agent])
reddit = None # Initialize reddit object as None

if not reddit_credentials_provided:
    logger.warning("Reddit API credentials not fully provided. Script will attempt local fallback only.")
else:
    try:
        reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            username=reddit_username,
            password=reddit_password,
            user_agent=reddit_user_agent,
        )
        logger.info("PRAW initialized successfully with Reddit credentials.")
    except Exception as e:
        logger.error(f"Failed to initialize PRAW with provided credentials: {e}. Will attempt local fallback.")
        reddit_credentials_provided = False # Force fallback if PRAW init fails
        reddit = None # Ensure reddit object is None

# --- Main Logic ---
def get_and_set_wallpaper():
    logger.info("Attempting to fetch and set new wallpaper...")
    selected_image_path = None # Stores the final path of the image to set

    # --- Try to get wallpaper from Reddit if credentials are provided and PRAW initialized ---
    if reddit_credentials_provided and reddit:
        logger.info("Attempting to fetch wallpaper from Reddit...")
        image_urls_raw = []
        try:
            selected_subreddit_name = random.choice(SUBREDDITS)
            subreddit = reddit.subreddit(selected_subreddit_name)
            logger.info(f"Searching subreddit: r/{selected_subreddit_name}")

            for submission in subreddit.top('week', limit=150):
                logger.debug(f"Processing submission: {submission.url} (is_reddit_media: {submission.is_reddit_media_domain}, domain: {submission.domain})")

                submission_width = getattr(submission, 'width', None)
                submission_height = getattr(submission, 'height', None)
                logger.debug(f"  Raw Dimensions from Reddit: {submission_width}x{submission_height}")

                if submission.url.lower().endswith(('.gif', '.gifv', '.mp4')):
                    logger.debug(f"Skipping Animated/Video GIF: {submission.url}")
                    continue

                candidate_url = None
                if submission.is_reddit_media_domain and submission.url.lower().endswith(('.jpg', '.jpeg', '.png')):
                    candidate_url = submission.url
                    logger.debug(f"  Candidate (Reddit media): {candidate_url}")
                elif submission.url.lower().startswith(('https://imgur.com/', 'https://i.imgur.com/')):
                    if submission.url.lower().endswith(('.jpg', '.jpeg', '.png')):
                        candidate_url = submission.url
                        logger.debug(f"  Candidate (Imgur direct): {candidate_url}")
                    elif 'imgur.com/a/' not in submission.url.lower():
                        if hasattr(submission, 'url_overridden_by_dest') and \
                           submission.url_overridden_by_dest and \
                           submission.url_overridden_by_dest.lower().endswith(('.jpg', '.jpeg', '.png')):
                            candidate_url = submission.url_overridden_by_dest
                            logger.debug(f"  Candidate (Imgur via url_overridden_by_dest): {candidate_url}")
                        else:
                            logger.debug(f"  Skipping Imgur non-direct (no suitable url_overridden_by_dest or extension): {submission.url}")
                    else:
                        logger.debug(f"  Skipping Imgur album: {submission.url}")
                else:
                    logger.debug(f"Skipping submission {submission.url} (not a recognized image post type or domain).")

                if candidate_url:
                    if submission_width and submission_height:
                        if submission_width >= MIN_IMAGE_WIDTH and submission_height >= MIN_IMAGE_HEIGHT:
                            image_urls_raw.append(candidate_url)
                            logger.debug(f"  ---> FINAL ADDED: {candidate_url} ({submission_width}x{submission_height})")
                        else:
                            logger.debug(f"  Skipping Candidate {candidate_url} (dimensions {submission_width}x{submission_height} too small).")
                    else:
                        image_urls_raw.append(candidate_url)
                        logger.debug(f"  ---> FINAL ADDED (No Reddit dimensions, trusting URL type): {candidate_url}")

            if not image_urls_raw:
                logger.warning("No suitable image URLs found from selected subreddits meeting all criteria via Reddit API.")
            else: # If Reddit found images, proceed with download
                selected_image_url = random.choice(image_urls_raw)
                logger.info(f"Selected image URL from Reddit: {selected_image_url}")

                os.makedirs(WALLPAPER_DIR, exist_ok=True)
                image_filename = os.path.join(WALLPAPER_DIR, os.path.basename(selected_image_url).split('?')[0])
                if '.' not in image_filename.split(os.sep)[-1]:
                    image_filename += ".jpg"

                logger.info(f"Downloading image to: {image_filename}")
                time.sleep(1) # Added 1-second delay for politeness

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': 'https://www.reddit.com/'
                }
                response = requests.get(selected_image_url, stream=True, timeout=10, headers=headers)
                response.raise_for_status()

                with open(image_filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info("Image downloaded successfully from Reddit.")
                selected_image_path = image_filename # This is the path to the downloaded image

        except Exception as e:
            logger.error(f"An error occurred during Reddit fetch or download: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.warning("Falling back to local wallpapers due to Reddit API issues or no suitable images found.")

    # --- Fallback to local wallpapers if no image was selected from Reddit ---
    if not selected_image_path:
        logger.info(f"Attempting to use local wallpaper from: {LOCAL_FALLBACK_WALLPAPER_DIR}")
        if os.path.isdir(LOCAL_FALLBACK_WALLPAPER_DIR):
            local_images = [
                os.path.join(LOCAL_FALLBACK_WALLPAPER_DIR, f)
                for f in os.listdir(LOCAL_FALLBACK_WALLPAPER_DIR)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ]
            if local_images:
                selected_image_path = random.choice(local_images)
                logger.info(f"Selected local image: {selected_image_path}")
            else:
                logger.error(f"No suitable images found in local fallback directory: {LOCAL_FALLBACK_WALLPAPER_DIR}")
                return False
        else:
            logger.error(f"Local fallback directory does not exist: {LOCAL_FALLBACK_WALLPAPER_DIR}")
            return False

    # --- Update betterlockscreen's cache with the selected image (from Reddit or local) ---
    try:
        update_cmd = [BETTERLOCKSCREEN_BIN, "-u", selected_image_path, "--fx"]
        logger.info(f"Running betterlockscreen update: {' '.join(update_cmd)}")
        subprocess.run(update_cmd, check=True, capture_output=True, text=True)
        logger.info("Betterlockscreen cache updated successfully.")

        # --- Send Dunst notification ---
        try:
            notify_cmd = ["/usr/bin/notify-send", "Wallpaper Updated", "Your lock screen wallpaper has been updated (from Reddit or local fallback)!"]
            subprocess.run(notify_cmd, check=True)
            logger.info("Dunst notification sent successfully.")
        except Exception as e:
            logger.warning(f"Failed to send Dunst notification: {e}")
        # --- Write timestamp to file for Polybar module ---  <--- THIS BLOCK
        try:
            # Ensure TIMESTAMP_FILE is defined at the top of your script
            # e.g., TIMESTAMP_FILE = "/tmp/last_wallpaper_update.txt"
            with open(TIMESTAMP_FILE, "w") as f:
                f.write(str(int(time.time()))) # Write Unix timestamp
            logger.info(f"Timestamp written to {TIMESTAMP_FILE}")
        except Exception as e:
            logger.warning(f"Failed to write timestamp file: {e}")
        # --- End timestamp writing ---

        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Betterlockscreen command failed: {e}")
        logger.error(f"STDOUT: {e.stdout}")
        logger.error(f"STDERR: {e.stderr}")
        return False

    except Exception as e: # Catch any other errors during final steps
        logger.error(f"An unexpected error occurred during final wallpaper set process: {e}")
        return False

if __name__ == "__main__":
    if get_and_set_wallpaper():
        logger.info("Wallpaper update process completed successfully.")
    else:
        logger.error("Failed to complete wallpaper update process.")
        sys.exit(1) # Exit with an error code if wallpaper update fails