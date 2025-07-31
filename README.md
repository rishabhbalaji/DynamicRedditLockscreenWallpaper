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