import os
import re
import yt_dlp
import subprocess
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

class Downloader:
    def __init__(self, url, output_folder):
        self.output_folder = output_folder
        self.url = url
        self.ydl_opts = {}
        self.info = {}
        self.progress_callback = None
        self.downloaded_files = []  # Track downloaded files

    def set_progress_callback(self, callback):
        """Set a callback function to report download progress"""
        self.progress_callback = callback
        
    def _progress_hook(self, d):
        """Hook to capture download progress"""
        if self.progress_callback and d['status'] == 'downloading':
            try:
                # Handle different progress formats
                if '_percent_str' in d:
                    percent = d['_percent_str'].strip()
                elif 'downloaded_bytes' in d and 'total_bytes' in d:
                    percent_val = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    percent = f"{percent_val:.1f}%"
                elif 'downloaded_bytes' in d and 'total_bytes_estimate' in d:
                    percent_val = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                    percent = f"{percent_val:.1f}%"
                else:
                    percent = "Downloading..."
                    
                self.progress_callback(percent)
            except (KeyError, ZeroDivisionError, TypeError):
                if self.progress_callback:
                    self.progress_callback("Downloading...")

    def sanitize_filename(self, filename):
        """Remove non-valid windows characters and limit length."""
        if not filename:
            return "unknown"
        
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
        # Limit length to prevent path issues
        if len(sanitized) > 200:
            sanitized = sanitized[:200]
        # Remove trailing dots and spaces (Windows issue)
        sanitized = sanitized.rstrip('. ')
        
        return sanitized if sanitized else "unknown"

    def get_expected_filename(self, info_dict, is_audio=False):
        """Get the expected filename for a download"""
        title = self.sanitize_filename(info_dict.get('title', 'unknown'))
        ext = 'mp3' if is_audio else info_dict.get('ext', 'mp4')
        return os.path.join(self.output_folder, f"{title}.{ext}")

    def file_exists_check(self, filepath):
        """Check if file exists and has reasonable size"""
        if not os.path.exists(filepath):
            return False
        
        # Check if file size is reasonable (> 1KB)
        try:
            return os.path.getsize(filepath) > 1024
        except OSError:
            return False

    def download_video(self):
        """Download video/audio with the correct settings."""
        try:
            # Add progress hooks to options
            self.ydl_opts['progress_hooks'] = [self._progress_hook]
            
            # First extract info without downloading to check if files exist
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                try:
                    self.info = ydl.extract_info(self.url, download=False)
                except Exception as e:
                    return f"Error extracting video info: {str(e)}"

            if not self.info:
                return "Error: Could not extract video information"

            # Handle playlists vs single videos
            entries = self.info.get('entries', [self.info])
            is_audio = 'FFmpegExtractAudio' in str(self.ydl_opts.get('postprocessors', []))
            
            # Check for existing files
            existing_files = []
            files_to_download = []
            
            for entry in entries:
                if not entry:
                    continue
                    
                expected_file = self.get_expected_filename(entry, is_audio)
                if self.file_exists_check(expected_file):
                    existing_files.append(os.path.basename(expected_file))
                else:
                    files_to_download.append(entry)

            # Report existing files
            if existing_files:
                existing_msg = f"Skipping {len(existing_files)} existing file(s): {', '.join(existing_files[:3])}"
                if len(existing_files) > 3:
                    existing_msg += f" and {len(existing_files) - 3} more"
                print(existing_msg)

            # If all files exist, return early
            if not files_to_download:
                if self.progress_callback:
                    self.progress_callback("100")
                return f"All files already exist. Skipped {len(existing_files)} file(s)."

            # Proceed with download for remaining files
            results = []
            
            # Download the files
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                try:
                    # Download and get fresh info
                    downloaded_info = ydl.extract_info(self.url, download=True)
                    self.info = downloaded_info  # Update with fresh info
                    
                    # Track what was actually downloaded
                    if 'entries' in downloaded_info:
                        for entry in downloaded_info['entries']:
                            if entry and '_filename' in entry:
                                self.downloaded_files.append(entry['_filename'])
                    elif '_filename' in downloaded_info:
                        self.downloaded_files.append(downloaded_info['_filename'])
                        
                except Exception as e:
                    return f"Download failed: {str(e)}"

            # Handle audio normalization if needed
            if is_audio and hasattr(self, 'normalize_audio_enabled') and self.normalize_audio_enabled:
                normalization_results = []
                entries = self.info.get('entries', [self.info])
                
                for entry in entries:
                    if not entry:
                        continue
                    expected_file = self.get_expected_filename(entry, True)
                    if self.file_exists_check(expected_file):
                        norm_result = self.normalize_audio(expected_file)
                        normalization_results.append(norm_result)
                
                if normalization_results:
                    results.extend(normalization_results)

            download_count = len(files_to_download)
            skip_count = len(existing_files)
            
            result_msg = f"Download completed! Downloaded: {download_count} file(s)"
            if skip_count > 0:
                result_msg += f", Skipped: {skip_count} existing file(s)"
                
            return result_msg

        except Exception as e:
            return f"Unexpected error: {str(e)}"

    def get_audio_opts(self):
        """Configure options for audio download without normalization"""
        postprocessors = [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {'key': 'FFmpegMetadata'},
        ]
        
        # Only add thumbnail embedding if available
        try:
            postprocessors.append({'key': 'EmbedThumbnail'})
        except:
            pass  # Skip if thumbnail embedding fails

        self.ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
            'postprocessors': postprocessors,
            'writethumbnail': True,
            'embedthumbnail': True,
            'addmetadata': True,
            'ignoreerrors': True,  # Continue on errors
            'no_warnings': False,
        }

    def get_video_opts(self):
        """Configure options for downloading video."""
        self.ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
            'ignoreerrors': True,  # Continue on errors
            'no_warnings': False,
        }

    def add_option(self, option_key, option_value=True):
        """Add a custom option to yt-dlp options"""
        if isinstance(option_key, str):
            if option_key.startswith('--'):
                # Handle command line style options
                key = option_key[2:].replace('-', '_')
                self.ydl_opts[key] = option_value
            else:
                self.ydl_opts[option_key] = option_value

    def add_audio_metadata(self):
        """Add ID3 metadata to downloaded audio files."""
        if not self.info:
            return "Error: No file information available."

        entries = self.info.get('entries', [self.info]) 
        results = []
        processed_files = set()  # Prevent duplicate processing

        for entry in entries:
            if not entry:
                continue
                
            try:
                title = self.sanitize_filename(entry.get('title', 'Unknown Title'))
                artist = entry.get('uploader', 'Unknown Artist')
                album = entry.get('playlist_title', entry.get('playlist', 'YouTube Download'))
                
                # Determine the actual filename
                filename = None
                
                # Try to get the actual downloaded filename
                if '_filename' in entry:
                    base_filename = os.path.splitext(entry['_filename'])[0] + ".mp3"
                    if os.path.exists(base_filename):
                        filename = base_filename
                
                # Fallback to expected filename
                if not filename:
                    filename = os.path.join(self.output_folder, f"{title}.mp3")
                
                # Skip if file doesn't exist or already processed
                if not self.file_exists_check(filename) or filename in processed_files:
                    continue
                    
                processed_files.add(filename)
                
                try:
                    # Try to load existing ID3 tags
                    try:
                        audio = EasyID3(filename)
                    except ID3NoHeaderError:
                        # Create new ID3 tag if none exists
                        audio = EasyID3()
                        results.append(f"Created ID3 header for: {os.path.basename(filename)}")
                    
                    # Add metadata
                    audio["title"] = title
                    audio["artist"] = artist
                    audio["album"] = album
                    
                    # Add additional metadata if available
                    if entry.get('upload_date'):
                        audio["date"] = entry['upload_date'][:4]  # Year only
                    
                    audio.save(filename)
                    results.append(f"Metadata updated: {os.path.basename(filename)}")
                    
                except Exception as e:
                    results.append(f"Error updating metadata for {os.path.basename(filename)}: {str(e)}")
                    
            except Exception as e:
                results.append(f"Error processing entry: {str(e)}")
                continue
                
        return "\n".join(results) if results else "No audio files found for metadata update."

    def normalize_audio(self, input_path):
        """Normalize audio using ffmpeg loudnorm filter"""
        if not self.file_exists_check(input_path):
            return f"Error: File not found - {os.path.basename(input_path)}"
            
        temp_path = input_path.replace('.mp3', '_normalized_temp.mp3')
        
        try:
            cmd = [
                'ffmpeg', '-i', input_path,
                '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
                '-y', temp_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and self.file_exists_check(temp_path):
                # Replace original with normalized version
                try:
                    os.replace(temp_path, input_path)
                    return f"Normalized: {os.path.basename(input_path)}"
                except OSError as e:
                    return f"Error replacing file: {str(e)}"
            else:
                # Clean up temp file if it exists
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass
                        
                error_msg = result.stderr if result.stderr else "Unknown ffmpeg error"
                return f"Normalization failed for {os.path.basename(input_path)}: {error_msg}"
                
        except subprocess.TimeoutExpired:
            # Clean up temp file
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            return f"Normalization timeout for {os.path.basename(input_path)}"
            
        except Exception as e:
            return f"Normalization error for {os.path.basename(input_path)}: {str(e)}"

    def set_normalize_audio(self, enable):
        """Enable or disable audio normalization"""
        self.normalize_audio_enabled = enable