"""MCP server: lets Claude, Cursor, ChatGPT and other MCP clients read YouTube transcripts.

Run with ``yt-transcript-apify-mcp`` (stdio). Needs ``APIFY_TOKEN`` in the environment.
Works with both mcp 1.x (FastMCP) and mcp 2.x (MCPServer).
"""

from __future__ import annotations

from .client import ApifyTranscriptClient, TranscriptError

try:  # mcp >= 2
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server  # type: ignore

server = _Server(
    "youtube-transcript",
    instructions=(
        "Get the transcript (captions) of YouTube videos and Shorts as plain text, timed lines, SRT or VTT. "
        "Pass a link or an 11-character video ID. Videos without captions return an explanation."
    ),
)


def _client() -> ApifyTranscriptClient:
    return ApifyTranscriptClient()


@server.tool()
def get_youtube_transcript(
    video: str, language: str = "", output: str = "text", translate_to: str = ""
) -> str:
    """Get the transcript of one YouTube video or Short.

    video: a YouTube link or 11-character video ID.
    language: preferred caption language code, e.g. "en" or "es"; empty = the video's own language.
    output: "text" (one paragraph), "timestamps" (one [MM:SS] line per caption), "srt" or "vtt".
    translate_to: optional language code to translate the transcript into.
    """
    fmt = {"text": "text", "timestamps": "timestampedText", "srt": "srt", "vtt": "vtt"}.get(output, "text")
    try:
        rows = _client().fetch_many(
            [video], languages=[language] if language else None, formats=[fmt], translate_to=translate_to or None
        )
    except (TranscriptError, ValueError) as e:
        return f"Error: {e}"
    if not rows:
        return "Error: no result"
    row = rows[0]
    if row.get("status") != "success":
        return f"No transcript: {row.get('message') or row.get('status')}"
    head = f"Title: {row.get('title')}\nChannel: {row.get('channelName')}\nLanguage: {row.get('language')}\n\n"
    return head + (row.get(fmt) or "")


@server.tool()
def get_youtube_transcripts(videos: list[str], language: str = "") -> str:
    """Get the plain-text transcripts of several YouTube videos in one call (up to 50).

    videos: YouTube links or 11-character video IDs.
    language: preferred caption language code; empty = each video's own language.
    """
    try:
        rows = _client().fetch_many(videos[:50], languages=[language] if language else None, formats=["text"])
    except (TranscriptError, ValueError) as e:
        return f"Error: {e}"
    parts = []
    for row in rows:
        if row.get("status") == "success":
            parts.append(f"## {row.get('title')} ({row.get('url')})\n\n{row.get('text') or ''}")
        else:
            parts.append(f"## {row.get('input')}\n\nNo transcript: {row.get('message') or row.get('status')}")
    return "\n\n".join(parts)


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
