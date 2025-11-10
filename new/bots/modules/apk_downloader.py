import os
import asyncio
import logging
import aiohttp
from pathlib import Path

logger = logging.getLogger(__name__)


async def download_apk(url, output_path, progress_callback=None):
    try:
        if not url.startswith(('http://', 'https://')):
            return False, "Invalid URL format", None

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        logger.info(f"Downloading APK from: {url}")

        timeout = aiohttp.ClientTimeout(total=600)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return False, f"HTTP {response.status}", None

                total_size = int(response.headers.get('content-length', 0))

                downloaded = 0
                chunk_size = 1024 * 1024

                with open(output_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        f.write(chunk)
                        downloaded += len(chunk)

                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            await progress_callback(progress, downloaded, total_size)

        if not os.path.exists(output_path):
            return False, "Download failed - file not created", None

        file_size = os.path.getsize(output_path)
        if file_size == 0:
            os.remove(output_path)
            return False, "Download failed - empty file", None

        logger.info(f"✅ APK downloaded: {file_size} bytes")
        return True, "Download complete", output_path

    except asyncio.TimeoutError:
        logger.error("Download timeout")
        if os.path.exists(output_path):
            os.remove(output_path)
        return False, "Download timeout (10 minutes)", None

    except aiohttp.ClientError as e:
        logger.error(f"Network error: {str(e)}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return False, f"Network error: {str(e)}", None

    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return False, f"Error: {str(e)}", None


def format_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"
