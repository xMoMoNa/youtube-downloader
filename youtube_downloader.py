from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum
import customtkinter as ctk
from tkinter import filedialog
import threading
from pathlib import Path
import pyperclip
import yt_dlp
import requests
from PIL import Image
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MediaType(Enum):
    VIDEO = "video"
    AUDIO = "audio"

@dataclass
class DownloadOptions:
    download_path: Path
    create_subfolder: bool = False
    download_media: bool = True
    download_thumbnail: bool = False
    download_captions: bool = False
    preferred_video_quality: str = "1080p"
    preferred_audio_quality: str = "128kbps"

@dataclass
class MediaStream:
    format_id: str
    type: MediaType
    format: str
    quality: str
    size_mb: float
    progress: float = 0.0

@dataclass
class MediaItem:
    url: str
    title: str
    duration: int
    thumbnail_url: str
    streams: List[MediaStream] = field(default_factory=list)
    selected_stream: Optional[MediaStream] = None
    progress: float = 0.0

class DownloadManager:
    def __init__(self):
        self.download_queue: List[MediaItem] = []
        self.options = DownloadOptions(download_path=Path.home() / "Downloads")
        
    def add_url(self, url: str) -> List[MediaItem]:
        """Add a URL to the download queue. Returns list of MediaItems."""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:  # Playlist
                    return [self._process_video(entry) for entry in info['entries']]
                else:  # Single video
                    return [self._process_video(info)]
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            raise

    def _process_video(self, info: dict) -> MediaItem:
        streams = []
        
        # Process formats
        for f in info['formats']:
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':  # Video with audio
                streams.append(MediaStream(
                    format_id=f['format_id'],
                    type=MediaType.VIDEO,
                    format=f.get('ext', 'unknown'),
                    quality=f"{f.get('height', 'unknown')}p",
                    size_mb=float(f.get('filesize', 0)) / (1024 * 1024)
                ))
            elif f.get('acodec') != 'none' and f.get('vcodec') == 'none':  # Audio only
                streams.append(MediaStream(
                    format_id=f['format_id'],
                    type=MediaType.AUDIO,
                    format=f.get('ext', 'unknown'),
                    quality=f.get('abr', 'unknown'),
                    size_mb=float(f.get('filesize', 0)) / (1024 * 1024)
                ))

        return MediaItem(
            url=info['webpage_url'],
            title=info['title'],
            duration=info['duration'],
            thumbnail_url=info['thumbnail'],
            streams=streams
        )

    def download_media(self, item: MediaItem, stream: MediaStream, progress_callback=None):
        """Download media using yt-dlp"""
        output_template = str(self.options.download_path / '%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': stream.format_id,
            'outtmpl': output_template,
            'progress_hooks': [lambda d: self._progress_hook(d, progress_callback)],
        }
        
        if stream.type == MediaType.AUDIO:
            ydl_opts.update({
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': self.options.preferred_audio_quality.replace('kbps', ''),
                }]
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([item.url])

    def _progress_hook(self, d, callback=None):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 0)
            if total > 0:
                progress = (downloaded / total) * 100
                if callback:
                    callback(progress)

class DownloaderGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("YouTube Downloader")
        self.geometry("1000x600")
        
        self.download_manager = DownloadManager()
        self.setup_ui()
        
    def setup_ui(self):
        # Setup theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Top bar
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="x", padx=10, pady=5)
        
        # URL entry
        self.url_var = ctk.StringVar()
        self.url_entry = ctk.CTkEntry(
            self.top_frame, 
            placeholder_text="Paste YouTube URL here...",
            width=400,
            textvariable=self.url_var
        )
        self.url_entry.pack(side="left", padx=5)
        
        # Paste button
        self.paste_btn = ctk.CTkButton(
            self.top_frame,
            text="Paste",
            command=self.paste_url
        )
        self.paste_btn.pack(side="left", padx=5)
        
        # Add button
        self.add_btn = ctk.CTkButton(
            self.top_frame,
            text="Add to Queue",
            command=self.add_to_queue
        )
        self.add_btn.pack(side="left", padx=5)
        
        # Settings button
        self.settings_btn = ctk.CTkButton(
            self.top_frame,
            text="⚙️ Settings",
            command=self.show_settings
        )
        self.settings_btn.pack(side="right", padx=5)
        
        # Main content area
        self.content_frame = ctk.CTkScrollableFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def start_download(self, item: MediaItem, stream: MediaStream, progress_bar: ctk.CTkProgressBar):
        """Start download in a separate thread"""
        def update_progress(progress):
            self.after(0, lambda: progress_bar.set(progress / 100))

        def download_thread():
            try:
                self.download_manager.download_media(item, stream, update_progress)
            except Exception as e:
                self.after(0, lambda: self.show_error(str(e)))

        threading.Thread(target=download_thread, daemon=True).start()

    def add_media_card(self, item: MediaItem):
        """Add a media card to the UI"""
        card = ctk.CTkFrame(self.content_frame)
        card.pack(fill="x", padx=5, pady=5)
        
        # Title and duration
        title_label = ctk.CTkLabel(
            card,
            text=f"{item.title} ({self.format_duration(item.duration)})"
        )
        title_label.pack(pady=5)
        
        # Stream selection
        stream_options = [
            f"{s.type.value.capitalize()} | {s.quality} | {s.format} | {s.size_mb:.1f} MB"
            for s in item.streams
        ]
        
        stream_var = ctk.StringVar(value=stream_options[0])
        stream_menu = ctk.CTkOptionMenu(
            card,
            values=stream_options,
            variable=stream_var
        )
        stream_menu.pack(pady=5)
        
        # Progress bar
        progress = ctk.CTkProgressBar(card)
        progress.pack(fill="x", padx=5, pady=5)
        progress.set(0)
        
        # Download button
        download_btn = ctk.CTkButton(
            card,
            text="Download",
            command=lambda: self.start_download(
                item,
                item.streams[stream_options.index(stream_var.get())],
                progress
            )
        )
        download_btn.pack(pady=5)

        # Remove button
        remove_btn = ctk.CTkButton(
            card,
            text="Remove",
            command=lambda: self.remove_media_card(card, item)
        )
        remove_btn.pack(pady=5)

    def remove_media_card(self, card, item: MediaItem):
        """Remove a media card from the UI and queue"""
        card.destroy()
        self.download_manager.download_queue.remove(item)

    def paste_url(self):
        """Paste URL from clipboard"""
        self.url_var.set(pyperclip.paste())
        
    def add_to_queue(self):
        """Add URL to download queue"""
        url = self.url_var.get().strip()
        if not url:
            self.show_error("Please enter a URL")
            return
            
        try:
            items = self.download_manager.add_url(url)
            for item in items:
                self.download_manager.download_queue.append(item)
                self.add_media_card(item)
            self.url_var.set("")  # Clear entry
        except Exception as e:
            self.show_error(f"Error adding URL: {str(e)}")
            
    def format_duration(self, seconds: int) -> str:
        """Format duration in seconds to HH:MM:SS"""
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
        
    def show_settings(self):
        """Show settings dialog"""
        settings = ctk.CTkToplevel(self)
        settings.title("Settings")
        settings.geometry("400x300")
        
        # Download path
        path_frame = ctk.CTkFrame(settings)
        path_frame.pack(fill="x", padx=10, pady=5)
        
        path_label = ctk.CTkLabel(path_frame, text="Download Path:")
        path_label.pack(side="left")
        
        path_entry = ctk.CTkEntry(path_frame, width=200)
        path_entry.pack(side="left", padx=5)
        path_entry.insert(0, str(self.download_manager.options.download_path))
        
        browse_btn = ctk.CTkButton(
            path_frame,
            text="Browse",
            command=lambda: self.browse_path(path_entry)
        )
        browse_btn.pack(side="left")
            
    def browse_path(self, entry: ctk.CTkEntry):
        """Browse for download path"""
        path = filedialog.askdirectory()
        if path:
            entry.delete(0, "end")
            entry.insert(0, path)
            self.download_manager.options.download_path = Path(path)
            
    def show_error(self, message: str):
        """Show error dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Error")
        dialog.geometry("300x100")
        
        label = ctk.CTkLabel(dialog, text=message)
        label.pack(pady=20)
        
        ok_btn = ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy
        )
        ok_btn.pack()

if __name__ == "__main__":
    app = DownloaderGUI()
    app.mainloop()
