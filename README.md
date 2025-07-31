# 🌟 Dynamic Reddit Lockscreen Wallpaper

## 🚀 Project Overview

`Dynamic Reddit Lockscreen Wallpaper` is a custom Python application designed for Linux users running `i3-wm` with `betterlockscreen` and `i3lock-color`. It dynamically fetches high-resolution image wallpapers from specified Reddit subreddits and updates your lock screen with a fresh, beautifully styled, and blurred image whenever you lock your screen or at set intervals.

This project aims to provide a constantly refreshing, visually engaging lock screen while demonstrating practical Python scripting, API interaction, and Linux desktop automation.

## ✨ Features

* **Dynamic Wallpapers:** Fetches new images from chosen Reddit subreddits.
* **Live Lockscreen Update:** Automatically updates the lock screen wallpaper when triggered.
* **Styled Lock Screen:** Leverages `betterlockscreen` and `i3lock-color` for a customizable, aesthetic lock screen (gradient overlay, input rings, custom fonts).
* **Scheduled Updates:** Integrates with `cron` for periodic background updates.
* **On-Demand Updates:** Manual keybinding in i3 to refresh the wallpaper cache.
* **Real-time Polybar Feedback:** A Polybar module shows the elapsed time since the last successful wallpaper update.
* **Dunst Notifications:** Provides a notification on successful wallpaper changes.
* **Open Source:** Built and shared with the community.

## 🛠️ Prerequisites

This setup is specifically tailored for **Linux** with the **i3 Window Manager**, but the core concepts can be adapted to other distros and window managers.

Ensure you have the following system components and tools installed:

* **i3 Window Manager:** (specifically `i3-gaps` for the aesthetic)
* **Polybar:** For the status bar and update indicator.
* **Alacritty:** Your terminal emulator (ensure it's configured with a Nerd Font).
* **Zsh & Oh My Zsh with Powerlevel10k:** For a powerful and aesthetic shell.
* **Picom:** Compositor for transparency, blur, and rounded corners.
* **betterlockscreen:** Manages lock screen images and effects.
* **i3lock-color:** The patched `i3lock` binary required for advanced lock screen styling.
* **`scrot`:** Screenshot utility.
* **`xclip`:** Clipboard utility.
* **`bc`:** Basic calculator utility (used by `betterlockscreen`).
* **`feh`:** Wallpaper setter (used by Variety, or can be used directly).
* **`dunst`:** Notification daemon.
* **`xss-lock`:** For automatic screen locking.
* **Python 3 & `venv`:** For running the application.
* **`git`:** For cloning repositories.
* **Your Reddit Account:** Required for API access.

---

## ⚙️ Installation Guide

Follow these steps to get the project running on your system.

### 1. Project Setup & Python Environment

### 1. Project Setup & Python Environment

First, clone the repository and set up your Python virtual environment.

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

### 2. Obtain Reddit API Credentials

Your script needs permission to interact with Reddit. You'll need to create a "Reddit App" to get the necessary credentials. **Keep these credentials private and NEVER commit them to Git!**

1.  **Go to Reddit's Developer Page:**
    Open your web browser and navigate to: [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
    (You'll need to be logged into your Reddit account).

2.  **Create a New App:**
    Scroll to the bottom and click the "are you a developer? create an app..." button.

3.  **Fill in App Details:**
    * **Name:** Give it a descriptive name (e.g., `MyKaliWallpaperScript`).
    * **Choose `script` for the app type.** This is crucial.
    * **description:** (Optional) `Python script for dynamic lockscreen wallpapers.`
    * **about url:** (Optional) You can leave this blank or put your GitHub profile URL.
    * **redirect uri:** Put `http://localhost:8080`. This is a placeholder for `script` apps and doesn't need to be live.

4.  **Save the App:** Click "create app".

5.  **Retrieve Your Credentials:**
    After creation, you'll see your app details. You need:
    * Your **Reddit Username**.
    * Your **Reddit Password**.
    * Your **`client ID`**: This is the long string of characters usually displayed directly under `personal use script`.
    * Your **`secret`**: Another long string of characters listed explicitly as "secret".

### 3. Securely Store Credentials (`.env` file)

To keep your credentials secure and out of your public repository, we'll store them in a local `.env` file. This file is already ignored by Git.

1.  **Create the `.env` file:**
    In your project's root directory (`DynamicRedditLockscreenWallpaper`), create a new file named `.env`:
    ```bash
    code .env
    ```

2.  **Add your credentials to `.env`:**
    Paste the following content into the `.env` file, and **replace the placeholder values with your actual Reddit credentials**:

    ```ini
    REDDIT_USERNAME="YOUR_REDDIT_USERNAME"
    REDDIT_PASSWORD="YOUR_REDDIT_PASSWORD"
    REDDIT_CLIENT_ID="YOUR_CLIENT_ID"
    REDDIT_CLIENT_SECRET="YOUR_CLIENT_SECRET"
    # User agent is a unique identifier for your script, required by Reddit
    REDDIT_USER_AGENT="python:com.yourdomain.DynamicRedditLockscreenWallpaper:v1.0.0 (by /u/YOUR_REDDIT_USERNAME)"
    ```
    * **Replace all `YOUR_...` placeholders** with your actual credentials.
    * For `REDDIT_USER_AGENT`, change `com.yourdomain` to something unique to you (e.g., `com.yourgithubusername.DynaWall`) and `YOUR_REDDIT_USERNAME` to your actual Reddit username.

3.  **Save the `.env` file.**
