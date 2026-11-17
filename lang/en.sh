# ==============================================================================
# YT-CLI: English Language Pack
# Language code: en
# ==============================================================================

LANG_CODE="en"
LANG_NAME="English"

# --- Main Banner and Prompt ---
MSG_BANNER_CREDITS="YT-CLI v1.3 • Created by Kenny Waddell (@KennyWaddell)"
MSG_BANNER_SUBTITLE="Multimedia Client: YouTube, TikTok, X, Reels and +1000 sites"
MSG_BANNER_FEATURES="Auto HWDEC Acceleration • FZF Queue • MP4/MP3 Downloads"
MSG_BANNER_SEARCHES="Searches:  keyword | @channel | @channel query | direct URLs"
MSG_BANNER_CMD_1="Commands:  [:help] Help       [:h] History     [:c] Cookies"
MSG_BANNER_CMD_2="           [:lang] Language   [:about] Credits [q] Quit"
MSG_SEARCH_PROMPT="Search, link or command [:help | q]: "
MSG_GOODBYE="See you later."

# --- Searches ---
MSG_SEARCHING="Searching YouTube:"
MSG_SEARCHING_CHANNEL="Searching channel"
MSG_FETCHING_CHANNEL="Fetching videos from channel"
MSG_NO_RESULTS="No results found for:"
MSG_EXITING_LIST="Exiting current results list..."
MSG_SELECTED_ITEMS="Selected items:"
MSG_FZF_PROMPT="▶ Select video(s) > "
MSG_FZF_HEADER="[Enter] Play | [Tab] Multi-select | [ESC] Exit | [Arrows] Navigate"

# --- Clipboard ---
MSG_CLIPBOARD_DETECTED="📋 Media link detected in clipboard:"
MSG_CLIPBOARD_CONFIRM="Do you want to open this link? [Y/n] (Enter for Yes): "

# --- Action Menu (Play / Download / Return) ---
MSG_ACTION_TITLE="What would you like to do with"
MSG_ACTION_SINGLE="this video"
MSG_ACTION_MULTI="videos in queue"
MSG_ACTION_STREAM_HEADER="── PLAY (ON-THE-FLY STREAMING) ─────────────────────"
MSG_ACTION_1="Watch in 720p HD at 30fps  (Recommended GPU Auto-Safe) ★ Default"
MSG_ACTION_2="Watch in 1080p Full HD     (30fps hardware accelerated H.264)"
MSG_ACTION_3="Watch in 480p / 360p       (Data and CPU saving)"
MSG_ACTION_4="Listen to audio only       (Radio/podcast mode - ~25MB RAM)"
MSG_ACTION_DOWNLOAD_HEADER="── DOWNLOAD AND SAVE TO DISK ───────────────────────"
MSG_ACTION_5="Download Video(s) 720p     (MP4 H.264 to disk/USB)"
MSG_ACTION_6="Download Video(s) 1080p    (MP4 Full HD to disk/USB)"
MSG_ACTION_7="Download Audio(s) MP3      (With cover art and metadata)"
MSG_ACTION_NAV_HEADER="── NAVIGATION ──────────────────────────────────────"
MSG_ACTION_0="Return to results list / Cancel"
MSG_ACTION_PROMPT="Choose option [1-7 | 0 to go back] (Enter for 720p): "

# --- MPV Player ---
MSG_MPV_AUDIO_START="▶ Audio Only Mode (Compact interactive player - ~25 MB RAM)..."
MSG_MPV_AUDIO_WAIT="⏳ Loading audio/playlist... controls window will open in a few seconds."
MSG_MPV_AUDIO_TIPS="[Audio Shortcuts: 'Space' pause | '←/→' seek | 'l' loop | '>/<' next/prev | '9/0' vol | 'q' quit]"
MSG_MPV_QUEUE_ACTIVE="🎶 Active queue with"
MSG_MPV_QUEUE_TIPS="[MPV Shortcuts: '>' next | '<' previous | 'q' quit | 'Space' pause | 'f' fullscreen]"
MSG_MPV_SINGLE_TIPS="[MPV Shortcuts: 'q' close and return to list | 'Space' pause | '9/0' volume | 'f' fullscreen]"
MSG_MPV_PLAY_360="▶ Playing in 360p (H.264 / 30fps)..."
MSG_MPV_PLAY_480="▶ Playing in 480p (H.264 / 30fps)..."
MSG_MPV_PLAY_720="▶ Playing in 720p (H.264 / auto-safe)..."
MSG_MPV_PLAY_1080="▶ Playing in 1080p at 30fps (H.264 / auto-safe, fallback 720p)..."

# --- Downloads ---
MSG_DL_DEST_TITLE="Destination folder for download:"
MSG_DL_DEST_DEFAULT="Default:"
MSG_DL_DEST_DRIVE="External USB/Drive:"
MSG_DL_DEST_CUSTOM="Enter custom path..."
MSG_DL_DEST_PROMPT="Choose option (Enter for default): "
MSG_DL_DEST_INPUT="Enter destination directory path: "
MSG_DL_VIDEO_START="⬇ Downloading Video(s) in"
MSG_DL_SAVING_IN="Saving to:"
MSG_DL_SUCCESS_NOTIFY="Download Complete"
MSG_DL_SUCCESS_MSG="Video downloaded successfully to"
MSG_DL_FAILED="Download failed for:"
MSG_DL_ALL_COMPLETE="✔ Download(s) finished."
MSG_DL_MUSIC_QUALITY_HEADER="Select MP3 audio quality:"
MSG_DL_MUSIC_Q1="320 kbps (Maximum audio fidelity) ★ Recommended"
MSG_DL_MUSIC_Q2="192 kbps (Balanced quality / file size)"
MSG_DL_MUSIC_Q3="128 kbps (Lightweight / fast download)"
MSG_DL_MUSIC_Q_PROMPT="Choose quality [1-3] (Enter for 320k): "
MSG_DL_EMBED_COVER_PROMPT="Embed cover art in MP3 files? [Y/n] (Enter for Yes): "
MSG_DL_MUSIC_START="🎵 Downloading MP3"
MSG_DL_MUSIC_NOTIFY_TITLE="Music Downloaded"
MSG_DL_MUSIC_NOTIFY_MSG="Song saved with metadata to"

# --- History ---
MSG_HIST_EMPTY="History is empty."
MSG_HIST_CLEARED="✔ History cleared successfully."
MSG_HIST_CLEAR_OPTION="🗑️  Clear entire history"
MSG_HIST_PROMPT="📜 History (max. 50) > "
MSG_HIST_HEADER="[Enter] Play video/playlist or Delete | [ESC] Go back"

# --- Cookies ---
MSG_COOKIE_PROMPT="Enter browser name or path to cookies.txt (e.g. brave, firefox, cookies.txt): "
MSG_COOKIE_SUCCESS="✔ Cookies configured for:"
MSG_COOKIE_ERROR_NOT_FOUND="[ERROR] Cookies file does not exist:"
MSG_COOKIE_BROWSER_EMPTY="[ERROR] You must specify a browser or cookies path (e.g. -c brave, -c firefox, -c cookies.txt)"

# --- Language ---
MSG_LANG_CURRENT="Current language:"
MSG_LANG_CHOOSE="Select language:"
MSG_LANG_SAVED="✔ Language changed successfully to:"

# --- Interactive Help ---
MSG_HELP_TITLE="QUICK COMMAND GUIDE (YT-CLI)"
MSG_HELP_SEARCH_HEADER="Searches and Links:"
MSG_HELP_SEARCH_KW="General search on YouTube (e.g. tech news)"
MSG_HELP_SEARCH_CH="View latest videos from a creator (e.g. @ElCuriosoBen)"
MSG_HELP_SEARCH_CH_TERM="Search inside a channel (e.g. @DrossRotzank mystery)"
MSG_HELP_SEARCH_URL="Paste URLs from YouTube, TikTok, X, Reels, etc."
MSG_HELP_CMD_HEADER="Interactive console commands:"
MSG_HELP_CMD_HELP="Display this quick help guide"
MSG_HELP_CMD_HIST="Open interactive playback history"
MSG_HELP_CMD_CLEAR="Clear all saved local history"
MSG_HELP_CMD_COOKIE="Load browser cookies (Brave, Firefox, etc.)"
MSG_HELP_CMD_LANG="Change interface language (Español / English)"
MSG_HELP_CMD_ABOUT="Display credits and about YT-CLI"
MSG_HELP_CMD_QUIT="Exit YT-CLI"
MSG_HELP_CLI_HEADER="Command line flags (external terminal launch):"
MSG_HELP_CLI_AUDIO="Podcast mode (Audio only, ~25 MB RAM)"
MSG_HELP_CLI_DOWN="Direct video download in MP4 (720p H.264)"
MSG_HELP_CLI_MUSIC="Direct song download in MP3 (320k)"
MSG_HELP_CLI_HIST="Open history directly"
MSG_HELP_CLI_HELP="Show all available command-line flags"
MSG_HELP_PRESS_ENTER="Press [Enter] to return to main menu..."
MSG_PRESS_ENTER_RETRY="Press [Enter] for another search or [q] to exit: "

# --- Credits / About ---
MSG_ABOUT_TITLE="ABOUT YT-CLI / CREDITS"
MSG_ABOUT_VERSION="Version:"
MSG_ABOUT_AUTHOR="Author:"
MSG_ABOUT_COLLAB="Collaboration:"
MSG_ABOUT_LICENSE="License:"
MSG_ABOUT_REPO="Repository:"
MSG_ABOUT_TAGLINE="Dedicated to the Linux community and budget hardware enthusiasts."
