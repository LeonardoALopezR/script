import atproto
from atproto import Client
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
import time

def build_prompt(all_posts):
    """all_posts is a list of dicts: {"handle": ..., "text": ...}"""
    source_block = "\n".join(f"- @{p['handle']}: {p['text']}" for p in all_posts)

    prompt = f"""Here are recent posts from Bluesky accounts I follow:

    {source_block}

    Write ONE original post (under 300 characters) that gives a short,
    interesting commentary or roundup of the themes above. Do NOT quote or
    copy any post's exact wording — write it entirely in your own words.
    No hashtag spam, no quotation marks around the whole thing.
    Output ONLY the post text, nothing else."""
    return prompt

def get_feed_posts(client,author):
    feed = client.app.bsky.feed.get_author_feed({
        "actor": author,
        "limit": 2,
        "filter": "posts_no_replies",
        "cursor": None
    })
    return feed.feed

def get_bluesky_client():
    client = Client()
    client.login(os.getenv("APP_USERNAME"), os.getenv("APP_PASSWORD"))
    return client

def get_gemini_client():
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_gemini_response_with_retries(client, prompt, retries=5):
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            )
            return response.text
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                wait = 2 ** attempt  # 1, 2, 4, 8, 16 seconds
                print(f"Model overloaded, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Gemini still unavailable after retries")

def main():
    load_dotenv()
    client = get_bluesky_client()
    print('Successfully logged in to Bluesky!')
    all_posts = []
    for author in os.getenv("AUTHORS_TO_FOLLOW").split(","):
        feed_posts = get_feed_posts(client, author)

        for item in feed_posts:
            if item.reason is not None:
                continue
            handle = item.post.author.handle
            text = item.post.record.text
            if not text:
                continue
            all_posts.append({"handle": handle, "text": text})

    print(f"Collected {len(all_posts)} posts total.")
    prompt = build_prompt(all_posts)
    gemini_client = get_gemini_client()
    gemini_response = get_gemini_response_with_retries(gemini_client, prompt)
    print(gemini_response)
    client.send_post(gemini_response)
    print('Successfully posted to Bluesky!')

if __name__ == "__main__":
    main()