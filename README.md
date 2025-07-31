# 🌟 Dynamic Reddit Lockscreen Wallpaper

## 🚀 Project Overview

`Dynamic Reddit Lockscreen Wallpaper` is a custom Python application designed for Linux users with `betterlockscreen` and `i3lock-color` installed. It dynamically fetches high-resolution image wallpapers from specified Reddit subreddits and updates your lock screen with a fresh, beautifully styled, and blurred/gradiented image whenever you lock your screen or at set intervals.

This project provides a constantly refreshing, visually engaging lock screen.

## ✨ Features

* **Dynamic Wallpapers:** Fetches new images from chosen Reddit subreddits.
* **Fallback to Local Images:** If Reddit API fails or credentials are not provided, it falls back to a local wallpaper directory.
* **Live Lockscreen Update:** Updates the lock screen wallpaper's cached image just before locking.
* **Styled Lock Screen:** Integrates seamlessly with `betterlockscreen` and `i3lock-color` for custom themes, input rings, and fonts.
* **Scheduled Updates:** Designed to be run by `cron` for periodic background updates.
* **On-Demand Updates:** Can be triggered manually via a keybinding.
* **Dunst Notifications:** Provides a notification on successful wallpaper changes.
* **Open Source:** Built and shared with the community.

## 🛠️ Prerequisites

This project assumes you have a functional Linux environment (e.g., Kali Linux, Debian, Ubuntu) with the following **already installed and configured**:

* **Python 3.x** and `venv`
* **`git`**
* **`betterlockscreen`**: This script must be installed and in your system's PATH.
* **`i3lock-color`**: A patched version of `i3lock` (like the one by `Raymo111`). This is essential for advanced lock screen styling (rings, custom fonts).
* **`scrot`**: For taking screenshots.
* **`bc`**: Basic calculator (used by `betterlockscreen`).
* **`dunst`**: Notification daemon (optional, but recommended for update notifications).
* **`xss-lock`**: For automatic screen locking (optional).
* **`imagemagick`**: For image processing (blur, gradient) used by `betterlockscreen`.
* **Your Reddit Account:** Required for Reddit API access.

---

## ⚙️ Installation Guide

Follow these steps to get the `Dynamic Reddit Lockscreen Wallpaper` script running on your system.

### 1. Project Setup & Python Environment

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YOUR_GITHUB_USERNAME/DynamicRedditLockscreenWallpaper.git](https://github.com/YOUR_GITHUB_USERNAME/DynamicRedditLockscreenWallpaper.git)
    cd DynamicRedditLockscreenWallpaper
    ```
    *(Remember to replace `YOUR_GITHUB_USERNAME` with your actual GitHub username)*

2.  **Create and Activate Python Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    Your terminal prompt should now show `(venv)` indicating the environment is active.

3.  **Install Python Dependencies:**
    Once your virtual environment is active, install all necessary Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

### 2. Obtain & Securely Store Reddit API Credentials

Your script needs permission to interact with Reddit. You'll need to create a "Reddit App" to get the necessary credentials. **Keep these credentials private and NEVER commit them to Git!**

1.  **Go to Reddit's Developer Page:**
    Open your web browser and navigate to: [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
    (You'll need to be logged into your Reddit account).

2.  **Create a New App:**
    Scroll to the bottom and click the "are you a developer? create an app..." button. Choose `script` for the app type, and set `redirect uri` to `http://localhost:8080`.

3.  **Retrieve Your Credentials:**
    After creation, you'll see your app details. You need:
    * Your **Reddit Username**.
    * Your **Reddit Password**.
    * Your **`client ID`**: Found under `personal use script`.
    * Your **`secret`**: Explicitly labeled "secret".

4.  **Create the `.env` file:**
    In your project's root directory, create a new file named `.env`:
    ```bash
    code .env
    ```
    Paste the following content, replacing the placeholders with your actual credentials:
    ```ini
    REDDIT_USERNAME="YOUR_REDDIT_USERNAME"
    REDDIT_PASSWORD="YOUR_REDDIT_PASSWORD"
    REDDIT_CLIENT_ID="YOUR_CLIENT_ID"
    REDDIT_CLIENT_SECRET="YOUR_CLIENT_SECRET"
    REDDIT_USER_AGENT="python:com.yourdomain.DynamicRedditLockscreenWallpaper:v1.0.0 (by /u/YOUR_REDDIT_USERNAME)"
    ```
    *Customize `com.yourdomain` and `YOUR_REDDIT_USERNAME` in the `REDDIT_USER_AGENT` string.*

5.  **Save the `.env` file.**

### 3. Configure `betterlockscreen` & Script Integration

This project modifies your lock screen. Ensure `betterlockscreen` is configured to use `i3lock-color` and your desired styles.

1.  **Customize `betterlockscreenrc`:**
    Copy the example `betterlockscreenrc` into your user config directory, then move it to your dotfiles and symlink it.
    ```bash
    mkdir -p ~/.config/betterlockscreen
    cp /path/to/betterlockscreen/example/betterlockscreenrc ~/.config/betterlockscreen/ # You might find this in ~/build/betterlockscreen/betterlockscreenrc
    # If not found, create it: `code ~/.config/betterlockscreen/betterlockscreenrc` and paste content from your dotfiles history.

    # Move to dotfiles and symlink
    mv ~/.config/betterlockscreen/betterlockscreenrc ~/dotfiles/betterlockscreenrc
    ln -s ~/dotfiles/betterlockscreenrc ~/.config/betterlockscreen/betterlockscreenrc
    ```
    **Edit `~/dotfiles/betterlockscreenrc` to match your theme.** Crucially, ensure:
    * Colors are in 8-digit `RRGGBBAA` format (e.g., `282A2EFF`).
    * `font="JetBrainsMono Nerd Font Regular"` (or your exact working font name).
    * `i3lockcolor_bin="i3lock"` is uncommented and set correctly.
    * `span_image=false` (if you want replication instead of spanning).
    * `blur_level` and `dim_level` are set as desired.

2.  **Generate Initial Cached Images:**
    This is necessary before `betterlockscreen` can lock. Run this once, providing a path to a **local wallpaper image** for initial cache generation.
    ```bash
    betterlockscreen -u "/path/to/your/initial_wallpaper.jpg" --fx
    ```
    *Replace `"/path/to/your/initial_wallpaper.jpg"` with an actual image file on your system.*

3.  **Integrate with i3 (`~/.config/i3/config`):**
    Modify your i3 config to use the script for dynamic locking.

    **Create or update `~/dotfiles/scripts/lock.sh`:**
    ```bash
    code ~/dotfiles/scripts/lock.sh
    ```
    Paste the following content:
    ```bash
    #!/bin/sh
    # Custom lock script for dynamic, styled i3lock-color screen
    # Fetches image from Reddit via wallpaper_updater.py, updates betterlockscreen cache, then locks.

    # Full path to your wallpaper_updater.py script's Python interpreter
    PYTHON_SCRIPT="/home/rbk/Main/Projects/DynamicRedditLockscreenWallpaper/venv/bin/python"
    WALLPAPER_UPDATER_APP="/home/rbk/Main/Projects/DynamicRedditLockscreenWallpaper/wallpaper_updater.py"

    # Run your Python app to fetch a Reddit image and update betterlockscreen's cache
    # Output is redirected to a temporary log file for debugging
    "$PYTHON_SCRIPT" "$WALLPAPER_UPDATER_APP" >> /tmp/lock_reddit_update.log 2>&1

    # Check if the wallpaper update script ran successfully
    if [ $? -eq 0 ]; then
        echo "$(date): Wallpaper updated successfully from Reddit. Proceeding to lock screen." >> /tmp/lock_reddit_update.log
        # Lock the screen with betterlockscreen (which uses the newly cached Reddit image)
        betterlockscreen -l
    else
        echo "$(date): Failed to update wallpaper from Reddit. Locking with last cached image." >> /tmp/lock_reddit_update.log
        # If script fails, fall back to locking with whatever's in cache
        betterlockscreen -l
    fi

    exit 0
    ```
    Make it executable: `chmod +x ~/dotfiles/scripts/lock.sh`

    **Update `~/dotfiles/i3_config` keybindings:**
    ```bash
    # Manual Lock: Dynamic background
    bindsym $mod+l exec --no-startup-id ~/dotfiles/scripts/lock.sh

    # Auto Lock: Dynamic background
    exec_always --no-startup-id xss-lock -- ~/dotfiles/scripts/lock.sh --off 5 --ignore-lid
    ```

### 4. Setup Cron Job for Automatic Updates

For periodic background updates of your lock screen wallpaper, set up a cron job.

1.  **Edit your crontab:**
    ```bash
    crontab -e
    ```

2.  **Add the cron job entry:**
    ```cron
    # Update betterlockscreen wallpaper from Reddit every 2 hours
    0 */2 * * * /home/rbk/Main/Projects/DynamicRedditLockscreenWallpaper/venv/bin/python /home/rbk/Main/Projects/DynamicRedditLockscreenWallpaper/wallpaper_updater.py >> /home/rbk/reddit_wallpaper_cron.log 2>&1
    ```

### 5. Polybar Module & Dunst Notification (Optional)

To get visual feedback, configure these:

1.  **Polybar Module for Last Update Time:**
    **Create `~/dotfiles/polybar_scripts/wallpaper_update_time.sh`:**
    ```bash
    code ~/dotfiles/polybar_scripts/wallpaper_update_time.sh
    ```
    Paste the content (from our previous steps, the one that formats elapsed time). Make it executable: `chmod +x ~/dotfiles/polybar_scripts/wallpaper_update_time.sh`
    **Update `~/dotfiles/config.ini`:**
    Add the module definition:
    ```ini
    [module/wallpaper_update_time]
    type = custom/script
    exec = ~/dotfiles/polybar_scripts/wallpaper_update_time.sh
    interval = 5
    format = <label>
    format-padding = 1
    format-background = ${colors.background}
    format-foreground = ${colors.foreground}
    ```
    Add it to `modules-right` in `[bar/primary]` and `[bar/secondary]`: `modules-right = bluetooth date wallpaper_update_time`.

2.  **Dunst Notifications:** (Already configured in your `dunstrc`)
    Ensure `wallpaper_updater.py` sends the notification (code is already in the script).

---

---

## 🚀 Usage

Once installed and configured, your lock screen wallpaper will update automatically. You can also trigger updates manually.

### Automatic Updates

The lock screen wallpaper will update periodically (e.g., every 2 hours) thanks to the `cron` job you set up. The `dunst` notification daemon will provide a visual confirmation upon successful completion.

### Manual Updates & Locking

You can manually control the lock screen wallpaper update and locking:

* **Update Lock Screen Wallpaper Cache:**
    * **Keybinding:** Press `Super + Shift + W` (`$mod + Shift + w`).
    * **Action:** This runs the `wallpaper_updater.py` script. It fetches a new image from Reddit (or local fallback), updates `betterlockscreen`'s cache, and sends a Dunst notification. Your current desktop wallpaper will *not* change.
    * **From Terminal:** While in your project directory with `(venv)` activated, run:
        ```bash
        python wallpaper_updater.py
        ```

* **Lock Screen (with current cached image):**
    * **Keybinding:** Press `Super + L` (`$mod + l`).
    * **Action:** This runs your `lock.sh` script, which immediately locks your screen using the most recently cached image from `betterlockscreen`. This action is instantaneous.

* **Automatic Locking (Idle/Suspend):**
    * The `xss-lock` service, configured in your `i3_config`, will automatically lock your screen after a period of inactivity or when the system is suspended, using the currently cached `betterlockscreen` image.

---

---

## 🔍 Troubleshooting

Here are solutions to common issues you might encounter during setup or usage.

### Python Script Issues (`wallpaper_updater.py`)

* **`ModuleNotFoundError: No module named 'dotenv'` (or 'praw', 'requests'):**
    * **Problem:** The Python script cannot find its required libraries.
    * **Solution:** Your Python virtual environment (`venv`) is likely not activated. Navigate to your project directory (`cd DynamicRedditLockscreenWallpaper`) and run `source venv/bin/activate`. Ensure `pip install -r requirements.txt` was run successfully while `venv` was active.

* **`ERROR - Missing one or more Reddit API credentials...`:**
    * **Problem:** The script cannot load your Reddit credentials.
    * **Solution:** Double-check your `.env` file (`code .env`). Ensure all variable names (`REDDIT_USERNAME`, `REDDIT_PASSWORD`, `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`) are spelled correctly (case-sensitive) and that their values are accurate (no typos, extra spaces, or missing characters). Also, confirm `REDDIT_CLIENT_SECRET` is correctly named.

* **`An error occurred: invalid_grant error processing request`:**
    * **Problem:** Reddit's API is rejecting your authentication attempt.
    * **Solution:** Your Reddit credentials are incorrect. Meticulously verify your `REDDIT_USERNAME`, `REDDIT_PASSWORD`, `REDDIT_CLIENT_ID`, and `REDDIT_CLIENT_SECRET` against your Reddit app page (`https://www.reddit.com/prefs/apps`). Ensure your Reddit app is of type `script` and `redirect uri` is `http://localhost:8080`.

* **`429 Client Error: Too Many Requests` (or similar HTTP errors like `403`, `500` from image hosts like Imgur):**
    * **Problem:** The script is hitting rate limits or being blocked by the image host during download.
    * **Solution:** The script includes a 1-second delay and custom `User-Agent` headers to mitigate this. If it persists, try increasing the `time.sleep(1)` value in `wallpaper_updater.py` or running the script less frequently. Sometimes, it's a temporary block by the host; try again later.

* **`WARNING - No suitable image URLs found...`:**
    * **Problem:** Reddit is working, but no images are matching your filtering criteria (minimum dimensions, file type) within the fetched posts.
    * **Solution:**
        * Expand your `SUBREDDITS` list in `wallpaper_updater.py`.
        * Loosen `MIN_IMAGE_WIDTH` and `MIN_IMAGE_HEIGHT` (e.g., lower them to `1280` or `720`).
        * Increase `limit` in `subreddit.top('week', limit=X)` (e.g., to `200` or `300`).
        * Consider changing `subreddit.top('week', ...)` to `subreddit.hot(...)` or `subreddit.new(...)` for a different set of posts.

* **`'Submission' object has no attribute 'width'`:**
    * **Problem:** The script tried to access a dimension property (`width` or `height`) on a Reddit post object that doesn't have it (e.g., a text post, video, or external link where PRAW doesn't provide dimensions).
    * **Solution:** (This should be resolved in the current script version). Ensure your `wallpaper_updater.py` is up-to-date with the `hasattr()` checks around `submission.width` and `submission.height`.

### `betterlockscreen` & `i3lock-color` Issues

* **`betterlockscreen: line X: bc: command not found`:**
    * **Problem:** `betterlockscreen` needs the `bc` utility for calculations.
    * **Solution:** Install `bc`: `sudo apt install -y bc`.

* **Lock screen doesn't have custom styling (rings, custom fonts for text, etc.):**
    * **Problem:** You are likely using the basic system `i3lock`, not `i3lock-color`.
    * **Solution:** Ensure `i3lock-color` has been successfully compiled and installed, and that `which i3lock` points to `/usr/local/bin/i3lock` (or `/usr/bin/i3lock` if it overwrote the system one, verified by `i3lock --version` showing "Raymond Li").

* **`i3lock: unrecognized option '--ring-width'` (or similar fancy options):**
    * **Problem:** Confirms you are using the basic `i3lock` that doesn't support advanced styling.
    * **Solution:** You *must* install `i3lock-color`. Refer to the "System Dependencies" section in the Installation Guide.

* **Lock screen is very slow/has a delay when manually locking (`$mod+l`) or automatically (`xss-lock`):**
    * **Problem:** The `lock.sh` script is running `wallpaper_updater.py` (fetching, downloading, processing) every time you lock.
    * **Solution:** This is intentional for a dynamic lock screen. If you prefer *instant* locks with a potentially older cached image (updated by `cron`), simplify your `~/dotfiles/scripts/lock.sh` to just:
        ```bash
        #!/bin/sh
        betterlockscreen -l
        exit 0
        ```
        Then reload i3.

* **Lock screen image is stretched/incorrect on multi-monitor setup:**
    * **Problem:** `betterlockscreen` is configured to span the image across monitors.
    * **Solution:** Edit `~/dotfiles/betterlockscreenrc` and set `span_image=false`. Then regenerate cached images with `betterlockscreen -u "/path/to/image.jpg" --fx`.

### Font & Icon Issues

* **Icons (like Polybar workspace numbers, CAVA, etc.) show as boxes or are missing:**
    * **Problem:** The application (Polybar, Alacritty, Dunst, i3lock-color) isn't loading your Nerd Font or Font Awesome correctly.
    * **Solution:**
        * Ensure `JetBrainsMono Nerd Font` and `Font Awesome 6 Free/Brands` are correctly installed in `~/.local/share/fonts/` and `fc-cache -r -v` has been run.
        * Verify `fc-match "JetBrainsMono Nerd Font"` points to the correct font file.
        * Check `~/dotfiles/config.ini` (Polybar), `~/dotfiles/alacritty_config` (Alacritty), `~/dotfiles/dunstrc` (Dunst), and `~/dotfiles/scripts/lock.sh` (i3lock-color) use the *exact* font name (e.g., `"JetBrainsMono Nerd Font"`, `"Font Awesome 6 Free"`).
        * Ensure `~/.config/fontconfig/fonts.conf` is correctly set up to prioritize JetBrainsMono for generic `monospace` fonts.

* **Dunst notifications not appearing or not themed:**
    * **Problem:** Dunst might not be running, or another notification daemon is interfering, or it can't find its icon theme.
    * **Solution:**
        * Verify Dunst is running: `ps aux | grep dunst | grep -v grep`. If not, check `exec_always --no-startup-id dunst` in `i3_config` and `sudo apt install -y dunst`.
        * Ensure `icon_theme = Adwaita` (or `Flat-Remix-Blue` etc.) is correctly set in `~/dotfiles/dunstrc` to an installed theme (check `lxappearance`).

---

---

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements, new features, or find a bug, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'feat: Add new feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.

Please ensure your code adheres to a clean, readable style and include relevant logging for debugging.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---