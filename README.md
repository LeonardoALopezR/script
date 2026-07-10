# autoTwitt

Automatically generates and posts original Bluesky commentary based on recent posts from accounts you follow. It collects the latest posts from configured authors, sends them to Google Gemini for a short roundup, and publishes the result to your Bluesky account.

## How it works

1. Logs into Bluesky using your app credentials.
2. Fetches the 2 most recent posts (excluding replies) from each author in `AUTHORS_TO_FOLLOW`.
3. Builds a prompt asking Gemini to write one original post (under 300 characters) summarizing or commenting on the themes.
4. Posts the generated text to your Bluesky feed.

## Requirements

- Python 3.10+
- A Bluesky account with an [app password](https://bsky.app/settings/app-passwords)
- A [Google Gemini API key](https://aistudio.google.com/apikey)

## Setup

1. Clone this repo and enter the directory:

   ```bash
   cd script
   ```

2. Install dependencies:

   ```bash
   pip install atproto python-dotenv google-genai
   ```

3. Create a `.env` file in the project root (see `.gitignore` — it is not committed):

   ```env
   APP_USERNAME=your-handle.bsky.social
   APP_PASSWORD=your-app-password
   GEMINI_API_KEY=your-gemini-api-key
   AUTHORS_TO_FOLLOW=author1.bsky.social,author2.bsky.social
   ```

   `AUTHORS_TO_FOLLOW` is a comma-separated list of Bluesky handles or DIDs to pull posts from.

## Usage

Run the script manually:

```bash
python autoTwitt.py
```

On success you will see the generated post printed to the terminal before it is published to Bluesky.

To run on a schedule, use cron, launchd, or another scheduler to invoke the script at your desired interval.

## Notes

- Gemini requests retry automatically with exponential backoff if the model is temporarily unavailable (503).
- Generated posts are written in original wording — the prompt instructs the model not to copy source posts verbatim.
- Keep your `.env` file private; it contains credentials for both Bluesky and Gemini.
