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
SUBREDDITS = ["motorcycles"]
# Minimum image width for posts (to ensure good quality for lockscreen)
MIN_IMAGE_WIDTH = 1920
# Minimum image height for posts
MIN_IMAGE_HEIGHT = 1080 # Adjusted for more flexibility
# Directory to save downloaded wallpapers temporarily
WALLPAPER_DIR = "/tmp/reddit_wallpapers"
# Full path to betterlockscreen executable (usually in /usr/local/bin)
BETTERLOCKSCREEN_BIN = "/usr/local/bin/betterlockscreen"

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

TIMESTAMP_FILE = "/tmp/last_wallpaper_update.txt"
# --- Load Environment Variables ---
# This loads variables from your .env file
load_dotenv()

# Get Reddit API credentials from environment variables
reddit_username = os.getenv("REDDIT_USERNAME")
reddit_password = os.getenv("REDDIT_PASSWORD")
reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
reddit_user_agent = os.getenv("REDDIT_USER_AGENT")

# --- Basic Validation ---
if not all([reddit_username, reddit_password, reddit_client_id, reddit_client_secret, reddit_user_agent]):
    logger.critical("Missing one or more Reddit API credentials in .env file or environment variables.")
    logger.critical("Please check REDDIT_USERNAME, REDDIT_PASSWORD, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT.")
    exit(1)

# --- Initialize PRAW (Reddit API client) ---
reddit = praw.Reddit(
    client_id=reddit_client_id,
    client_secret=reddit_client_secret,
    username=reddit_username,
    password=reddit_password,
    user_agent=reddit_user_agent,
)
logger.info("PRAW initialized successfully.")

# --- Main Logic ---
def get_and_set_wallpaper():
    logger.info("Attempting to fetch and set new wallpaper...")
    selected_subreddit_name = random.choice(SUBREDDITS)
    subreddit = reddit.subreddit(selected_subreddit_name)
    logger.info(f"Searching subreddit: r/{selected_subreddit_name}")

    image_urls_raw = [] # Store raw URLs found, before final filtering
    try:
        # Fetch top posts from the last week (adjust limit and method as needed)
        # You can use .hot(), .top('day'), .top('week'), .new(), .rising()
        for submission in subreddit.top('week', limit=150): # Fetch up to 150 top posts from the week
            logger.debug(f"Processing submission: {submission.url} (is_reddit_media: {submission.is_reddit_media_domain}, domain: {submission.domain})")

            # Safely get dimensions if they exist
            submission_width = getattr(submission, 'width', None)
            submission_height = getattr(submission, 'height', None)
            logger.debug(f"  Raw Dimensions from Reddit: {submission_width}x{submission_height}")

            # Skip animated GIFs if you only want static images
            if submission.url.lower().endswith(('.gif', '.gifv', '.mp4')): # Added .mp4
                logger.debug(f"Skipping Animated/Video GIF: {submission.url}")
                continue

            # --- Filtering Logic for Image URLs ---
            candidate_url = None

            # 1. Handle Reddit-hosted media (i.redd.it)
            if submission.is_reddit_media_domain and submission.url.lower().endswith(('.jpg', '.jpeg', '.png')):
                candidate_url = submission.url
                logger.debug(f"  Candidate (Reddit media): {candidate_url}")

            # 2. Handle Imgur links
            elif submission.url.lower().startswith(('https://imgur.com/', 'https://i.imgur.com/')):
                if submission.url.lower().endswith(('.jpg', '.jpeg', '.png')): # Direct image links
                    candidate_url = submission.url
                    logger.debug(f"  Candidate (Imgur direct): {candidate_url}")
                elif 'imgur.com/a/' not in submission.url.lower(): # Avoid Imgur albums
                    # For Imgur links without extensions (e.g., i.imgur.com/XXXXX), check url_overridden_by_dest if it points to an image
                    if hasattr(submission, 'url_overridden_by_dest') and \
                       submission.url_overridden_by_dest and \
                       submission.url_overridden_by_dest.lower().endswith(('.jpg', '.jpeg', '.png')):
                        candidate_url = submission.url_overridden_by_dest
                        logger.debug(f"  Candidate (Imgur via url_overridden_by_dest): {candidate_url}")
                    else:
                        logger.debug(f"  Skipping Imgur non-direct (no suitable url_overridden_by_dest or extension): {submission.url}")
                else:
                    logger.debug(f"  Skipping Imgur album: {submission.url}")

            # 3. Add other trusted direct image hosts if necessary (e.g., flickr, deviantart, etc.)
            # elif submission.url.lower().endswith(('.jpg', '.jpeg', '.png')) and any(domain in submission.url.lower() for domain in ['flickr.com', 'deviantart.com']):
            #    candidate_url = submission.url
            #    logger.debug(f"  Candidate (Other trusted host): {candidate_url}")

            else:
                logger.debug(f"Skipping submission {submission.url} (not a recognized image post type or domain).")

            # --- Apply final quality filters (dimensions) if a candidate URL was found ---
            if candidate_url:
                # If dimensions are available from Reddit API, use them
                if submission_width and submission_height:
                    if submission_width >= MIN_IMAGE_WIDTH and submission_height >= MIN_IMAGE_HEIGHT:
                        image_urls_raw.append(candidate_url)
                        logger.debug(f"  ---> FINAL ADDED: {candidate_url} ({submission_width}x{submission_height})")
                    else:
                        logger.debug(f"  Skipping Candidate {candidate_url} (dimensions {submission_width}x{submission_height} too small).")
                else:
                    # If dimensions are not available from Reddit, we'll trust the URL type and try to download.
                    image_urls_raw.append(candidate_url)
                    logger.debug(f"  ---> FINAL ADDED (No Reddit dimensions, trusting URL type): {candidate_url}")


        if not image_urls_raw:
            logger.warning("No suitable image URLs found from selected subreddits meeting all criteria. Retrying or expanding search parameters might be needed.")
            return False

        # Choose a random image from the collected URLs
        selected_image_url = random.choice(image_urls_raw)
        logger.info(f"Selected image URL: {selected_image_url}")

        # Ensure wallpaper directory exists
        os.makedirs(WALLPAPER_DIR, exist_ok=True)

        # --- Download the image ---
        # Add a short delay before downloading to avoid hitting rate limits
        time.sleep(1) # Added 1-second delay

        # Define custom headers to make the request look more like a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.reddit.com/' # Indicate origin
        }

        # Clean filename from URL, handle query parameters, and ensure extension
        image_filename = os.path.join(WALLPAPER_DIR, os.path.basename(selected_image_url).split('?')[0])
        if '.' not in image_filename.split(os.sep)[-1]: # Check if filename has no extension
            image_filename += ".jpg" # Default to .jpg if no extension

        logger.info(f"Downloading image to: {image_filename}")
        response = requests.get(selected_image_url, stream=True, timeout=10, headers=headers) # Added headers and timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        with open(image_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info("Image downloaded successfully.")

        # --- Update betterlockscreen's cache ---
        try:
            # Command to update betterlockscreen cache with the new image
            # This will apply blur, dim, etc. based on ~/.config/betterlockscreen/betterlockscreenrc
            update_cmd = [BETTERLOCKSCREEN_BIN, "-u", image_filename, "--fx"]
            logger.info(f"Running betterlockscreen update: {' '.join(update_cmd)}")
            subprocess.run(update_cmd, check=True, capture_output=True, text=True)
            logger.info("Betterlockscreen cache updated successfully.")

            # --- Send Dunst notification ---
            try:
                # Path to notify-send (usually in /usr/bin)
                notify_cmd = ["/usr/bin/notify-send", "Wallpaper Updated", "Your lock screen wallpaper has been updated from Reddit!"]
                subprocess.run(notify_cmd, check=True)
                logger.info("Dunst notification sent successfully.")
            except Exception as e:
                logger.warning(f"Failed to send Dunst notification: {e}")
                logger.warning("Ensure notify-send is in PATH or specify its full path.")
            # --- End Dunst notification ---
            
            # --- Write timestamp to file for Polybar module ---
            try:
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

    except Exception as e:
        logger.error(f"An error occurred during wallpaper fetch or set: {e}")
        logger.error(f"Error type: {type(e).__name__}") # More specific error type
        logger.error("Please ensure your Reddit API credentials are correct, you have network access, and the subreddits exist.")
        return False

if __name__ == "__main__":
    if get_and_set_wallpaper():
        logger.info("Wallpaper updated successfully!")
        # The script itself doesn't lock. i3 will call betterlockscreen -l separately.
    else:
        logger.error("Failed to update wallpaper.")
        sys.exit(1) # Exit with an error code if wallpaper update fails