from urllib.parse import urlparse, parse_qs
import requests
from datetime import datetime
import re
from typing import Optional
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from config import Config

logger = logging.getLogger(__name__)

def _get_youtube_api() -> YouTubeTranscriptApi:
    config = Config.from_env()
    if config.proxy_username and config.proxy_password:
        proxy_config = WebshareProxyConfig(
            proxy_username=config.proxy_username,
            proxy_password=config.proxy_password
        )
        return YouTubeTranscriptApi(proxy_config=proxy_config)
    return YouTubeTranscriptApi()

def extract_youtube_url(text: str) -> Optional[str]:
    url_patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'https?://(?:www\.)?youtu\.be/[\w-]+',
        r'https?://(?:www\.)?youtube\.com/embed/[\w-]+'
    ]
    
    for pattern in url_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

def extract_video_id(url: str) -> str:
    parsed = urlparse(url)
    if parsed.hostname in ('youtu.be', 'www.youtu.be'):
        return parsed.path.lstrip('/')
    if parsed.hostname in ('www.youtube.com', 'youtube.com'):
        qs = parse_qs(parsed.query)
        if 'v' in qs:
            return qs['v'][0]
        path_parts = parsed.path.split('/')
        if 'embed' in path_parts:
            return path_parts[path_parts.index('embed') + 1]
    raise ValueError("Invalid YouTube URL")

def fetch_html_content(video_id: str) -> Optional[str]:
    try:
        response = requests.get(f"https://www.youtube.com/watch?v={video_id}")
        if response.status_code == 200:
            return response.text
        else:
            logger.error(f"Failed to fetch HTML content for video_id={video_id}. Status code: {response.status_code}")
    except Exception as e:
        logger.exception(f"Exception while fetching HTML content for video_id={video_id}: {e}")
    return None

def get_video_metadata(video_id: str) -> tuple[str, str]:
    html_content = fetch_html_content(video_id)
    if not html_content:
        return "Unknown Title", "Unknown Date"
    
    title_match = re.search(r'"title":"([^"]+)"', html_content)
    title = title_match.group(1) if title_match else "Unknown Title"
    
    date_match = re.search(r'"uploadDate":"([^"]+)"', html_content)
    if date_match:
        upload_date = date_match.group(1)
        try:
            parsed_date = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
            formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
        except:
            formatted_date = upload_date if len(upload_date) >= 10 else "Unknown Date"
    else:
        formatted_date = "Unknown Date"
    
    return title, formatted_date

def get_channel_metadata(video_id: str) -> tuple[str, str]:
    html_content = fetch_html_content(video_id)
    if not html_content:
        return "Unknown Channel", "Unknown Channel URL"
    
    channel_match = re.search(r'"ownerChannelName":"([^"]+)"', html_content)
    channel_name = channel_match.group(1) if channel_match else "Unknown Channel"
    
    channel_url = "Unknown Channel URL"
    
    channel_id_match = re.search(r'"ownerChannelId":"([^"]+)"', html_content)
    if channel_id_match:
        channel_id = channel_id_match.group(1)
        channel_url = f"https://www.youtube.com/channel/{channel_id}"
    else:
        channel_id_match = re.search(r'"channelId":"([^"]+)"', html_content)
        if channel_id_match:
            channel_id = channel_id_match.group(1)
            channel_url = f"https://www.youtube.com/channel/{channel_id}"
        else:
            custom_url_match = re.search(r'"customUrl":"@?([^"]+)"', html_content)
            if custom_url_match:
                custom_url = custom_url_match.group(1).lstrip('@')
                channel_url = f"https://www.youtube.com/@{custom_url}"
            else:
                channel_link_match = re.search(r'"(https://www\.youtube\.com/(?:channel/|@)([^"/]+))"', html_content)
                if channel_link_match:
                    channel_url = channel_link_match.group(1)
    
    return channel_name, channel_url

def fetch_transcription(video_url: str, language: str = 'pl') -> str:
    video_id = extract_video_id(video_url)
    ytt_api = _get_youtube_api()
    try:
        transcript = ytt_api.fetch(video_id, languages=[language])
    except Exception as e:
        logger.warning(f"No transcript found for video_id={video_id} with language '{language}'. Error: {e}. Attempting to fetch Polish transcript as fallback...")
        try:
            transcript = ytt_api.fetch(video_id, languages=['pl'])
        except Exception as fallback_error:
            logger.exception(f"Failed to fetch transcript for video_id={video_id} with both language '{language}' and fallback 'pl'. Original error: {e}, Fallback error: {fallback_error}")
            raise
    
    return '\n'.join([snippet.text for snippet in transcript.snippets if snippet.text.strip()])

