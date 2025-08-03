## YT Downloader 'download' module in Python

import yt_dlp
import json
import csv
import os
from urllib.parse import urlparse
import requests
import threading
from pathlib import Path
from PyQt5.QtCore import pyqtSignal, QObject, QThread


class Download(QObject, yt_dlp.YoutubeDL):
    return_fetch_info = pyqtSignal(object)
    return_fetch_info_error = pyqtSignal(object)
    def __init__(self, input):
        QObject.__init__(self)
        self.input = input
        self.is_playlist = False
        self.cookie_file_loaded = False
        self.is_url = False
        self.options = {
            "quiet" : True,
            "skip_download" : True,
            "nocheckcertificate": True, 
        }
        self.read_settings()
        self.load_cookie_file()
        self.is_running = True
        print("Initiated...")

    def read_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as settings:
                    settings_dict = json.load(settings).get("Fetching")
                    self.search_limit = int(settings_dict.get("SearchLimit")) or 5
        except:   self.search_limit = 5 



    def fetch_info(self):                        #Fetch Info Section
        self.is_url = self.is_valid_online_url()
        self.is_playlist = self.is_url and ("list=" in self.input or "playlist" in self.input)
        self.options["extract_flat"] = "in_playlist" if self.is_playlist else False
        self.cookie = self.cookies.get(self.site) if self.site  else None
        if self.cookie:
            self.options["cookiefile"] = self.cookie
            self.options["add_header"] = [
                                        "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                                        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                                        "Accept-Language: en-US,en;q=0.9",
                                        "Referer: https://www.youtube.com/"
                                        ]
            print("proceding  with cookies")
        self.query = self.input if self.is_url else f"ytsearch{self.search_limit}:{self.input}"
        if "youtube.com" in self.site.lower() or "youtu.be" in self.site.lower():
            self.options["extractor_args"] = {"youtube": ["player_client=web"]}
        yt_dlp.YoutubeDL.__init__(self, self.options)
        try:
            info_dict = self.extract_info(self.query, download=False)
            
            print("info  fetched...")
            if "entries" in info_dict:
                results = []
                for entry in info_dict["entries"]:
                    if not entry:
                        continue
                    # Refetch metadata if key info is missing
                    if not entry.get("thumbnail") or not entry.get("webpage_url"):
                        try:
                            entry = self.extract_info(entry["url"], download=False)
                        except Exception as e:
                            self.return_fetch_info_error.emit(f"Failed to refetch entry {entry.get('id')}: {e}")
                    results.append({
                        "id": entry.get("id"),
                        "title": entry.get("title"),
                        "uploader": entry.get("uploader"),
                        "duration": entry.get("duration"),
                        "duration_str": self.format_duration(entry.get("duration")) if entry.get("duration") else entry.get("duration_string"),
                        "thumbnail": entry.get("thumbnail"),
                        "url": entry.get("webpage_url"),
                        "format": entry.get("formats", []),
                    })
#                return results
                
            else:
                results = {
                    "id": info_dict.get("id"),
                    "title": info_dict.get("title"),
                    "uploader": info_dict.get("uploader"),
                    "duration": info_dict.get("duration"),
                    "duration_str": self.format_duration(info_dict.get("duration")) if self.format_duration(info_dict.get("duration")) else info_dict.get("duration_string"),
                    "thumbnail": info_dict.get("thumbnail"),
                    "url": info_dict.get("webpage_url"),
                    "format": info_dict.get("formats", []),
                }
            self.return_fetch_info.emit(results)
            print("results sent...")
        except Exception as e:
            self.return_fetch_info_error.emit(f"Failed to fetch info: {str(e)}")
            return 
    def format_duration(self, seconds):
        if seconds is None:
            return False
        seconds = int(seconds)
        minutes, sec = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{sec:02d}"
        else:
            return f"{minutes}:{sec:02d}"

    def is_probably_url(self, string):
        parsed = urlparse(string)
        self.site = parsed.netloc
        return bool(parsed.scheme) and bool(parsed.netloc) 

    @staticmethod
    def is_url_online(url):
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def is_valid_online_url(self):
        if self.is_probably_url(self.input) and self.is_url_online(self.input):
            return True
        return False


    def load_cookie_file(self):
        if os.path.exists("cookies.json"):
            with open("cookies.json", "r") as f:
                self.cookies = json.load(f)
            self.cookie_file_loaded = True

class RealDownload(QObject, yt_dlp.YoutubeDL):
    def __init__(self, url, format, signals, ext=None):
        QObject.__init__(self)
#        self.load_cookie_file()            # for now
        self.cookie = None
        self.url = url
        self.format = format
        self.ext = None
        self.ext = ext
        self.signals = signals
        self.read_settings()
        
        
        
    def read_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as settings:
                settings_dict = json.load(settings).get("Downloader")
        

        self.DEFAULT_DOWNLOAD_PATH = Path(settings_dict.get("download_path")) or Path.home() / "Downloads" / "MorpheusDL"
        self.DEFAULT_DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)
        self.embed_subtitles = True if settings_dict.get("EmbedSubtitles") else False
            
        self.auto_gen_subs = True if settings_dict.get("WriteAutoSub") else False
        
        if settings_dict.get("UseExternalDownloader"):
            self.external_downloader_enabled = True
            self.external_downloader = settings_dict.get("ExternalDownloader", "aria2c")
            self.external_downloader_args = settings_dict.get("ExternalDownloaderArgs", ["-x", "16", "-k", "1M"])

    

#    def load_cookie_file(self):
#        if os.path.exists("cookies.json"):
#            with open("cookies.json", "r") as f:
#                self.cookies = json.load(f)
#            self.cookie_file_loaded = True

    def download_video(self):     # download section


        opts = {
            "format": self.format,
            "writethumbnail": True,
            "cookiefile": self.cookie if self.cookie else None,
            "outtmpl": str(self.DEFAULT_DOWNLOAD_PATH / "%(title).50s [%(id)s].%(ext)s"),
            "noplaylist": True,
            "quiet": False,
            "progress_hooks": [self.hook_progress],
            "postprocessors": [
        {
            "key": "FFmpegMetadata"
        },
        {
            "key": "EmbedThumbnail"
        }
        ],
            "embed-thumbnail": True,
            "add-metadata": True,
            # "ffmpeg_location": "C:/path/to/ffmpeg"  # Uncomment if ffmpeg not in PATH
        }
        if self.embed_subtitles:
            opts["writesubtitles"] = True
            opts["embedsubtitles"] = True
            opts["subtitleslangs"] = ["en"]
            opts.setdefault("postprocessors", []).append({"key": "FFmpegEmbedSubtitle"})

        if self.auto_gen_subs:
            opts["writeautomaticsub"] = True
    
        if self.cookie:
            opts["cookiefile"] = self.cookie
            opts["add_header"] = [
                                        "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                                        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                                        "Accept-Language: en-US,en;q=0.9",
                                        "Referer: https://www.youtube.com/"
                                        ]
            
        if self.external_downloader_enabled:
            opts["external_downloader"] = self.external_downloader
            opts["external_downloader_args"] = {
                "aria2c": self.external_downloader_args
            }

        with yt_dlp.YoutubeDL({k: v for k, v in opts.items() if v is not None}) as ydl:
            ydl.download([self.url])

        self.logging()


    def download_both(self):     # download section


        opts = {
            "format": self.format,
            "writethumbnail": True,
            "cookiefile": self.cookie if self.cookie else None,
            "outtmpl": str(self.DEFAULT_DOWNLOAD_PATH / "%(title).50s [%(id)s].%(ext)s"),
            "noplaylist": True,
            "quiet": False,
            "merge_output_format": self.ext or "mp4",
            "progress_hooks": [self.hook_progress],
            "postprocessors": [
        {
            "key": "FFmpegMetadata"
        },
        {
            "key": "EmbedThumbnail"
        }
        ],
            "embed-thumbnail": True,
            "add-metadata": True,
            # "ffmpeg_location": "C:/path/to/ffmpeg"  # Uncomment if ffmpeg not in PATH
} 
        
        if self.embed_subtitles:
            opts["writesubtitles"] = True
            opts["embedsubtitles"] = True
            opts["subtitleslangs"] = ["en"]
            opts.setdefault("postprocessors", []).append({"key": "FFmpegEmbedSubtitle"})

        if self.auto_gen_subs:
            opts["writeautomaticsub"] = True
    
        
        if self.cookie:
            opts["cookiefile"] = self.cookie
            opts["add_header"] = [
                                        "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                                        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                                        "Accept-Language: en-US,en;q=0.9",
                                        "Referer: https://www.youtube.com/"
                                        ]
        if self.external_downloader_enabled:
            opts["external_downloader"] = self.external_downloader
            opts["external_downloader_args"] = {
                "aria2c": self.external_downloader_args
            }


        with yt_dlp.YoutubeDL({k: v for k, v in opts.items() if v is not None}) as ydl:
            ydl.download([self.url])

        self.logging()

    def download_audio(self):     # download section
        


        opts = {
            "format": self.format,
            "writethumbnail": True,
            "cookiefile": self.cookie if self.cookie else None,
            "outtmpl": str(self.DEFAULT_DOWNLOAD_PATH / "%(title).50s [%(id)s].%(ext)s"),
            "noplaylist": True,
            "quiet": False,
            "progress_hooks": [self.hook_progress],
            "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3"
        },
        {
            "key": "FFmpegMetadata"
        },
        {
            "key": "EmbedThumbnail"
        }
        ],
            "embed-thumbnail": True,
            "add-metadata": True,
            # "ffmpeg_location": "C:/path/to/ffmpeg"  # Uncomment if ffmpeg not in PATH
        }

        if self.embed_subtitles:
            opts["writesubtitles"] = True
            opts["embedsubtitles"] = True
            opts["subtitleslangs"] = ["en"]
            opts.setdefault("postprocessors", []).append({"key": "FFmpegEmbedSubtitle"})
    
        if self.auto_gen_subs:
            opts["writeautomaticsub"] = True
    
        if self.cookie:
            opts["cookiefile"] = self.cookie
            opts["add_header"] = [
                                        "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                                        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                                        "Accept-Language: en-US,en;q=0.9",
                                        "Referer: https://www.youtube.com/"
                                        ]
        if self.external_downloader_enabled:
            opts["external_downloader"] = self.external_downloader
            opts["external_downloader_args"] = {
                self.external_downloader: self.external_downloader_args
            }


        with yt_dlp.YoutubeDL({k: v for k, v in opts.items() if v is not None}) as ydl:
            ydl.download([self.url])
        
        self.logging()


#    def download_all(self, entries, format="best", audio_only=False):
#        if os.path.exists("download_path.json"):
#            with open("download_path.json", "r") as dp:
#                download_path = json.load(dp).get("download_path")
#                if download_path:
#                    self.DEFAULT_DOWNLOAD_PATH = download_path
#                else:
#                    self.DEFAULT_DOWNLOAD_PATH = Path.home() / "Downloads" / "YT-DLP"
#                    self.DEFAULT_DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)
#
#
#        opts = {
#            "format": "bestaudio/best" if audio_only else format,
#            "cookiefile": self.cookie if self.cookie else None,
#            "outtmpl": str(self.DEFAULT_DOWNLOAD_PATH / "%(title).50s [%(id)s].%(ext)s"),
#            "noplaylist": False,
#            "quiet": False,
#            "progress_hooks": [self.hook_progress],
#            "merge_output_format": "mp3" if audio_only else "mp4",
#            "postprocessors": [{
#                "key": "FFmpegExtractAudio",
#                "preferredcodec": "mp3",
#            }] if audio_only else []
#        }
#        for entry in entries:
#            if not entry or not entry.get("url"):
#                continue
#            print(f"Downloading: {entry['title']} ({entry['id']})")
#            with yt_dlp.YoutubeDL({k: v for k, v in opts.items() if v is not None}) as ydl:
#                ydl.download(entry, audio_only=audio_only)


    def hook_progress(self, d):
        if d["status"] == "downloading":
            print(f"{d['_percent_str']} of {d['_total_bytes_str']} at {d['_speed_str']}")
        elif d["status"] == "finished":
            print(f"✅ Done: {d['filename']}")
    
    def logging(self):
        if os.path.exists("history.json"):
            with open("history.json", "r") as r:
                record = json.load(r)
            for i in range(len(record)):
                if record[i][0] == self.url:
                    logger = record[i]
                    logger[4] = str(self.DEFAULT_DOWNLOAD_PATH)
                    logger[5] = "Completed"
                    with open("history.json", "w") as history:
                        json.dump(record, history, indent=4)
                    
                    self.signals.refresh_downloads.emit()

