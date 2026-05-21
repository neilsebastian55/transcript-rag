import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


def extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11})",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
        r"embed\/([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from URL: {url}")


def fetch_youtube_transcript(url: str) -> tuple[str, str]:
    video_id = extract_video_id(url)
    ytt = YouTubeTranscriptApi()
    transcript_list = ytt.fetch(video_id)
    text = " ".join(entry.text for entry in transcript_list)

    title = f"YouTube: {video_id}"
    try:
        import urllib.request, json as _json
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        with urllib.request.urlopen(oembed_url, timeout=5) as r:
            data = _json.loads(r.read())
            title = data.get("title", title)
    except Exception:
        pass

    return text, title
