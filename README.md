# youtube-transcript-apify

<!-- mcp-name: io.github.nokia2k2/youtube-transcript-apify -->

**YouTube transcripts that keep working on AWS, Google Cloud, Azure, Vercel, Render and every other cloud server.**

If your code works on your laptop but fails in production with `RequestBlocked`, `IpBlocked`, `TooManyRequests` or HTTP 429, YouTube is blocking your server's IP address. Most cloud IP ranges are blocked. This package sends the request to a hosted scraper on [Apify](https://apify.com/nokia2k/youtube-transcript-scraper) that handles proxies and retries, and gives you back plain Python data.

- Same shape as the classic `youtube-transcript-api` call: a list of `{"text", "start", "duration"}`.
- Plain text, timestamped text, SRT and VTT, in 70+ languages, or translated.
- Videos without captions are reported, not charged.
- The client uses only the standard library. Includes a CLI and an MCP server for Claude, Cursor and other AI agents.

> Disclosure: this package is a thin client for the [YouTube Transcript Scraper](https://apify.com/nokia2k/youtube-transcript-scraper) Actor, which is made by the same author (nokia2k). Runs are billed by Apify: about $2.99 per 1,000 transcripts at the time of writing, and Apify's free plan includes $5 of credit every month, no card needed.

## Install

```bash
pip install youtube-transcript-apify   # client, CLI and MCP server
```

Get a free API token at <https://console.apify.com/settings/integrations> and set it:

```bash
export APIFY_TOKEN=apify_api_...
```

## Use it in Python

Replace the call that gets blocked:

```python
# before
# from youtube_transcript_api import YouTubeTranscriptApi
# segments = YouTubeTranscriptApi.get_transcript("arj7oStGLkU", languages=["en"])

# after
from yt_transcript_apify import get_transcript
segments = get_transcript("arj7oStGLkU", languages=["en"])
print(segments[0])   # {'text': 'So in college,', 'start': 1.2, 'duration': 2.16}
```

More control:

```python
from yt_transcript_apify import ApifyTranscriptClient

client = ApifyTranscriptClient()                  # reads APIFY_TOKEN
t = client.fetch("https://youtu.be/arj7oStGLkU", formats=["text", "srt"])
print(t.title, t.language, t.is_generated)
print(t.text[:200])
open("talk.srt", "w").write(t.srt)

rows = client.fetch_many(["arj7oStGLkU", "iG9CE55wbtY"], translate_to="es")
for row in rows:
    print(row["status"], row.get("title"))       # failed videos keep a plain message
```

`fetch` raises `TranscriptError` (with `.status`, e.g. `no_captions`, `private`, `not_found`) when a video has no transcript. `fetch_many` never raises for single videos: each row carries its own `status` and `message`.

## Command line

```bash
yt-transcript-apify arj7oStGLkU                   # plain text
yt-transcript-apify https://youtu.be/arj7oStGLkU --format srt > talk.srt
yt-transcript-apify arj7oStGLkU --lang es --translate en
```

## MCP server (Claude Desktop, Claude Code, Cursor)

Add this to your MCP client configuration:

```json
{
  "mcpServers": {
    "youtube-transcript": {
      "command": "uvx",
      "args": ["youtube-transcript-apify"],
      "env": { "APIFY_TOKEN": "apify_api_..." }
    }
  }
}
```

Tools:

| Tool | What it does |
| --- | --- |
| `get_youtube_transcript` | One video or Short: `text`, `timestamps`, `srt` or `vtt`, optional language and translation |
| `get_youtube_transcripts` | Up to 50 videos at once, plain text, one section per video |

Then ask: *"Summarize this video: https://www.youtube.com/watch?v=arj7oStGLkU"*.

## Other ways to call the same scraper

- **No code:** run it from the [Apify Store page](https://apify.com/nokia2k/youtube-transcript-scraper) and download JSON, CSV or Excel.
- **n8n, Make, Zapier:** use the Apify integration and pick `nokia2k/youtube-transcript-scraper`.
- **Thousands of videos as plain text:** [YouTube Video to Text](https://apify.com/nokia2k/youtube-video-to-text) is cheaper per video.
- **Whole channels, playlists, search results, likes and comments:** [YouTube Scraper](https://apify.com/nokia2k/youtube-all-in-one-scraper).

## FAQ

**Why does youtube-transcript-api work locally but not on my server?** YouTube blocks most requests from cloud provider IP ranges. Rotating residential proxies fix it; this package uses a hosted service that already has them, so you do not manage proxies yourself.

**Is it free?** The package is free and open source (MIT). The Apify runs it calls are paid per transcript; the monthly free credit covers roughly 1,600 transcripts.

**Which data does it return?** Only what YouTube shows publicly: captions, title, channel, language. It does not download video or audio.

## License

MIT
