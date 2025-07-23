from collections.abc import Generator
from typing import Any
import os
import tempfile
import time
import mimetypes
import imghdr
import requests
import httpx
from requests_oauthlib import OAuth1Session
import json
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class MediaTweetTool(Tool):
    # Set longer timeout values, especially for video uploads
    DOWNLOAD_TIMEOUT = 60  # Download media timeout (seconds)
    INIT_TIMEOUT = 30  # Initialize upload timeout (seconds)
    UPLOAD_TIMEOUT = 180  # Upload media timeout (seconds)
    FINALIZE_TIMEOUT = 60  # Finalize upload timeout (seconds)
    STATUS_TIMEOUT = 30  # Check status timeout (seconds)
    TWEET_TIMEOUT = 30  # Send tweet timeout (seconds)
    
    # Supported media formats
    SUPPORTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    SUPPORTED_VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.wmv']
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Post a tweet with media (image or video) using X API
        """
        # Extract parameters
        text = tool_parameters.get("text")
        media_file = tool_parameters.get("media")
        
        if not text:
            yield self.create_text_message("Error: Tweet text is required")
            return
        
        if len(text) > 280:
            yield self.create_text_message("Error: Tweet text must be 280 characters or less")
            return
        
        if not media_file:
            yield self.create_text_message("Error: Media file is required")
            return
        
        media_path = None
        
        try:
            # Get credentials from runtime
            credentials = self.runtime.credentials
            
            # Create OAuth1 session
            oauth = OAuth1Session(
                credentials["api_key"],
                client_secret=credentials["api_secret"],
                resource_owner_key=credentials["access_token"],
                resource_owner_secret=credentials["access_token_secret"]
            )
            
            # Check Dify provided media parameter format
            if isinstance(media_file, dict):
                # Get media information from Dify dictionary format
                media_url = media_file.get('url')
                file_extension = media_file.get('extension', '')
                mime_type = media_file.get('mime_type', '')
                filename = media_file.get('filename', 'media')
                
                # If URL exists, download media file through URL
                if media_url:
                    yield self.create_text_message(f"Downloading media file from URL...")
                    
                    # Try different timeout settings and disable SSL verification
                    try:
                        # First try using requests instead of httpx, as requests may be more stable in some network environments
                        media_path = self._download_media_from_url_with_requests(
                            media_url, 
                            file_extension, 
                            self.DOWNLOAD_TIMEOUT,
                            verify_ssl=False
                        )
                        
                        if not media_path:
                            # If first attempt fails, try enabling SSL verification
                            yield self.create_text_message("First download attempt failed, retrying with different configuration...")
                            media_path = self._download_media_from_url_with_requests(
                                media_url, 
                                file_extension, 
                                self.DOWNLOAD_TIMEOUT, 
                                verify_ssl=True
                            )
                            
                        if not media_path:
                            # If still fails, try using httpx instead of requests
                            media_path = self._download_media_from_url_with_httpx(
                                media_url, 
                                file_extension, 
                                self.DOWNLOAD_TIMEOUT * 2  # Use longer timeout
                            )
                    except Exception as download_error:
                        yield self.create_text_message(f"Error downloading media: {str(download_error)}")
                        return
                        
                    if not media_path:
                        yield self.create_text_message("Error: Failed to download media from URL after multiple attempts")
                        return
                else:
                    yield self.create_text_message("Error: No media URL provided")
                    return
            else:
                # Process directly uploaded file (blob format)
                try:
                    if hasattr(media_file, 'blob'):
                        file_extension = os.path.splitext(media_file.filename)[1].lower() if hasattr(media_file, 'filename') and media_file.filename else ''
                        if not file_extension:
                            # Try to determine extension from mimetype
                            if hasattr(media_file, 'mimetype') and media_file.mimetype:
                                ext = mimetypes.guess_extension(media_file.mimetype)
                                if ext:
                                    file_extension = ext.lower()
                            else:
                                file_extension = '.tmp'
                        
                        # Write blob to temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                            try:
                                # Try to access blob attribute directly, may cause HTTPS request
                                blob_data = media_file.blob
                                temp_file.write(blob_data)
                                media_path = temp_file.name
                            except Exception as blob_err:
                                # If blob attribute access fails, try checking if there's a URL attribute
                                if hasattr(media_file, 'url') and media_file.url:
                                    # Close temporary file and clean up
                                    temp_file.close()
                                    os.unlink(temp_file.name)
                                    
                                    # Use URL download as alternative
                                    media_path = self._download_media_from_url_with_requests(
                                        media_file.url,
                                        file_extension,
                                        self.DOWNLOAD_TIMEOUT * 2,
                                        verify_ssl=False
                                    )
                                else:
                                    # If no URL attribute, re-raise exception
                                    raise
                    else:
                        yield self.create_text_message("Error: Invalid media file format")
                        return
                except Exception as e:
                    yield self.create_text_message(f"Error processing media file: {str(e)}")
                    return
            
            if not media_path:
                yield self.create_text_message("Error: Failed to prepare media file")
                return
                
            try:
                # Validate media file type
                
                # Check if file exists and is readable
                if not os.path.exists(media_path):
                    yield self.create_text_message("Error: Media file does not exist")
                    return
                    
                file_size = os.path.getsize(media_path)
                
                if file_size == 0:
                    yield self.create_text_message("Error: Media file is empty")
                    return
                    
                media_type = self._validate_media_type(media_path, file_extension)
                
                if not media_type:
                    yield self.create_text_message("Error: Unsupported media format. Please upload JPG, PNG, GIF, WEBP for images or MP4 for videos.")
                    return
                    
                # Determine media type (image or video)
                is_video = media_type == 'video'
                
                # Inform user that media upload may take some time
                if is_video:
                    yield self.create_text_message("Uploading video file to X, this may take some time...")
                else:
                    yield self.create_text_message(f"Uploading {media_type} to X...")
                
                # Upload the media to Twitter
                media_id = self._upload_media(oauth, media_path, is_video)
                
                if media_id:
                    # Post the tweet with media
                    tweet_id = self._post_tweet_with_media(oauth, text, media_id)
                    
                    if tweet_id:
                        # Return success message with tweet ID
                        yield self.create_json_message({
                            "status": "success",
                            "tweet_id": tweet_id,
                            "text": text,
                            "media_id": media_id,
                            "media_type": media_type,
                            "message": f"Tweet with {media_type} published successfully with ID: {tweet_id}"
                        })
                    else:
                        yield self.create_text_message("Error: Failed to post tweet with media")
                else:
                    yield self.create_text_message("Error: Failed to upload media")
            finally:
                # Clean up the temporary file
                if media_path and os.path.exists(media_path):
                    os.unlink(media_path)
                
        except requests.exceptions.Timeout as timeout_err:
            error_message = "Error: Request timed out. The media file may be too large or your network connection is slow."
            yield self.create_text_message(error_message)
        except requests.exceptions.ConnectionError as conn_err:
            error_message = f"Error: Connection error when uploading media. {str(conn_err)}"
            yield self.create_text_message(error_message)
        except Exception as e:
            error_message = f"Error posting media tweet: {str(e)}"
            yield self.create_text_message(error_message)
    
    def _download_media_from_url_with_requests(self, url: str, file_extension: str, timeout: int, verify_ssl: bool = True) -> str:
        """
        Download media file from URL to temporary file using requests library
        
        Args:
            url: Media file URL
            file_extension: File extension
            timeout: Download timeout (seconds)
            verify_ssl: Whether to verify SSL certificate
            
        Returns:
            Temporary file path
        """
        try:
            # Download file with specified timeout, optionally disable SSL verification
            response = requests.get(url, stream=True, timeout=timeout, verify=verify_ssl)
            
            response.raise_for_status()  # Raise exception if request fails
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                # Write in chunks to handle large files
                bytes_downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                        bytes_downloaded += len(chunk)
                
                return temp_file.name
                
        except Exception:
            return None
            
    def _download_media_from_url_with_httpx(self, url: str, file_extension: str, timeout: int) -> str:
        """
        Download media file from URL to temporary file using httpx library
        
        Args:
            url: Media file URL
            file_extension: File extension
            timeout: Download timeout (seconds)
            
        Returns:
            Temporary file path
        """
        try:
            # Create custom SSL context, disable hostname verification
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create httpx client, set SSL context and timeout
            
            # Disable proxy
            client = httpx.Client(
                timeout=timeout,
                verify=False,  # Disable SSL verification
                proxies=None,  # Disable proxy
                http2=False    # Disable HTTP/2, which sometimes causes TLS issues
            )
            
            response = client.get(url)
            response.raise_for_status()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                # Write to file
                temp_file.write(response.content)
                return temp_file.name
                
        except Exception:
            return None
        finally:
            # Ensure httpx client is closed
            if 'client' in locals():
                client.close()
    
    def _validate_media_type(self, file_path: str, file_extension: str) -> str:
        """
        Validate media file type and return type name
        
        Args:
            file_path: File path
            file_extension: File extension
            
        Returns:
            'image', 'video' or None (if not supported)
        """
        # Check if it's an image
        if file_extension.lower() in self.SUPPORTED_IMAGE_EXTENSIONS:
            # Use imghdr to further validate image
            try:
                img_type = imghdr.what(file_path)
                if img_type in ['jpeg', 'jpg', 'png', 'gif'] or img_type is None:  # Some PNG images may not be recognized
                    return 'image'
            except Exception:
                pass
            
        # Check if it's a video
        if file_extension.lower() in self.SUPPORTED_VIDEO_EXTENSIONS:
            # Basic validation of video file (check if file exists and has content)
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                return 'video'
                
        # Try to determine by MIME type
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                if mime_type.startswith('image/'):
                    return 'image'
                elif mime_type.startswith('video/'):
                    return 'video'
        except Exception:
            pass
                
        return None
    
    def _upload_media(self, oauth: OAuth1Session, media_path: str, is_video: bool) -> str:
        """
        Upload media to Twitter
        
        Args:
            oauth: OAuth1Session object
            media_path: Path to the media file
            is_video: Whether the media is a video
            
        Returns:
            Media ID or None if upload failed
        """
        MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'
        
        # For videos, we need to use the chunked upload approach
        if is_video:
            file_size = os.path.getsize(media_path)
            
            # INIT
            init_params = {
                'command': 'INIT',
                'total_bytes': file_size,
                'media_type': 'video/mp4',
                'media_category': 'tweet_video'
            }
            
            init_response = oauth.post(MEDIA_ENDPOINT_URL, data=init_params, timeout=self.INIT_TIMEOUT)
            
            if init_response.status_code != 202 and init_response.status_code != 200:
                return None
            
            media_id = init_response.json().get('media_id_string')
            
            # APPEND
            segment_index = 0
            bytes_sent = 0
            
            with open(media_path, 'rb') as video:
                while bytes_sent < file_size:
                    chunk = video.read(4 * 1024 * 1024)  # 4MB chunks
                    
                    append_params = {
                        'command': 'APPEND',
                        'media_id': media_id,
                        'segment_index': segment_index
                    }
                    
                    files = {
                        'media': chunk
                    }
                    
                    append_response = oauth.post(MEDIA_ENDPOINT_URL, data=append_params, files=files, timeout=self.UPLOAD_TIMEOUT)
                    
                    if append_response.status_code != 204 and append_response.status_code != 200:
                        return None
                    
                    segment_index += 1
                    bytes_sent = video.tell()
            
            # FINALIZE
            finalize_params = {
                'command': 'FINALIZE',
                'media_id': media_id
            }
            
            finalize_response = oauth.post(MEDIA_ENDPOINT_URL, data=finalize_params, timeout=self.FINALIZE_TIMEOUT)
            
            if finalize_response.status_code != 201 and finalize_response.status_code != 200:
                return None
            
            processing_info = finalize_response.json().get('processing_info')
            
            # Check status if processing is needed
            if processing_info:
                self._check_processing_status(oauth, media_id, processing_info)
            
            return media_id
        else:
            # For images, check file size
            file_size = os.path.getsize(media_path)
            
            # X API image upload limit is usually 5MB
            if file_size > 5 * 1024 * 1024:
                return None
                
            # For images, we can use the simple upload approach
            with open(media_path, 'rb') as image:
                files = {
                    'media': image
                }
                
                # Determine image type
                mime_type, _ = mimetypes.guess_type(media_path)
                if not mime_type:
                    # If MIME type cannot be determined, default to jpeg
                    mime_type = 'image/jpeg'
                
                # Add media category parameter to handle GIFs correctly
                if mime_type == 'image/gif':
                    params = {'media_category': 'tweet_gif'}
                else:
                    params = {'media_category': 'tweet_image'}
                
                response = oauth.post(MEDIA_ENDPOINT_URL, files=files, params=params, timeout=self.UPLOAD_TIMEOUT)
                
                if response.status_code != 200:
                    return None
                
                media_id = response.json().get('media_id_string')
                return media_id
    
    def _check_processing_status(self, oauth: OAuth1Session, media_id: str, processing_info: dict) -> None:
        """
        Check the processing status of a media upload
        
        Args:
            oauth: OAuth1Session object
            media_id: Media ID
            processing_info: Processing info dict
        """
        MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'
        
        state = processing_info.get('state')
        
        if state == 'succeeded':
            return
        
        if state == 'failed':
            return
        
        check_after_secs = processing_info.get('check_after_secs', 5)
        time.sleep(check_after_secs)
        
        params = {
            'command': 'STATUS',
            'media_id': media_id
        }
        
        response = oauth.get(MEDIA_ENDPOINT_URL, params=params, timeout=self.STATUS_TIMEOUT)
        
        if response.status_code != 200:
            return
        
        processing_info = response.json().get('processing_info')
        
        if processing_info:
            self._check_processing_status(oauth, media_id, processing_info)
    
    def _post_tweet_with_media(self, oauth: OAuth1Session, text: str, media_id: str) -> str:
        """
        Post a tweet with media
        
        Args:
            oauth: OAuth1Session object
            text: Tweet text
            media_id: Media ID
            
        Returns:
            Tweet ID or None if posting failed
        """
        POST_TWEET_URL = 'https://api.twitter.com/2/tweets'
        
        payload = {
            "text": text,
            "media": {
                "media_ids": [media_id]
            }
        }
        
        response = oauth.post(POST_TWEET_URL, json=payload, timeout=self.TWEET_TIMEOUT)
        
        if response.status_code != 201 and response.status_code != 200:
            return None
        
        tweet_id = response.json().get('data', {}).get('id')
        return tweet_id 