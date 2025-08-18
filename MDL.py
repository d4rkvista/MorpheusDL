import sys
from PyQt5.QtWidgets import(
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QListWidget, QListWidgetItem, QComboBox,
    QStackedWidget, QMessageBox, QStackedLayout, QDialog, QFileDialog, QFrame, QLayout
)
from PyQt5.QtCore import (Qt, QSize, pyqtSignal, QObject, QRunnable, QTimer,
    QThreadPool, pyqtSlot, QThread, QPropertyAnimation, QPoint, QPropertyAnimation, pyqtProperty
)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QFontDatabase, QTransform
import qtawesome as qta
import json
import csv
import os
from pathlib import Path
import requests
import time
from datetime import timedelta
from Downloader import Download, RealDownload
from io import BytesIO


class GlitchTitle(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.full_text = "MorpheusDL"
        self.sequence = [
            "MorpheusDL",
            "MorpheusDL",
            "MorpheusDL",
            "MorpheusDL",
            "MorpheusDL",
            "MorpheusDL",
            "MorpheusDL",
            "MorpheusDL",
            "MorpheusDL",
            "MorpheuDL",
            "MorpheDL",
            "MorphDL",
            "MorpDL",
            "MorDL",
            "MoDL",
            "MDL",
            "MDL",
            "MDL",
            "MDL",
            "MDL",
            "MDL",
            "MDL",
            "MDL",
            "MDL",
            "MoDL",
            "MorDL",
            "MorpDL",
            "MorphDL",
            "MorpheDL",
            "MorpheuDL",
            "MorpheusDL",
            "MorpheusDL",
            "MorpheusDL",
            "MorpheusDL",
            "MorpheusDL",
            "MorpheusDL",
            "MorpheusDL",
            "MorpheusDL",
            "MorpheusDL"
            ]  # cycle states
        self.index = 0
        self.setText(self.full_text)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("font-size: 40px; font-weight: bold; color: white;")

        # Timer to update text
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_text)
        self.timer.start(500)  # update every 500ms

    def animate_text(self):
        self.index = (self.index + 1) % len(self.sequence)
        self.setText(self.sequence[self.index])


class Download_starter(QRunnable):
    def __init__(self, url, ID, type, signals):
        super().__init__()
        self.signals = signals
        self.url = url
        self.ID = ID
        self.type = type

    def run(self):
        download = RealDownload(self.url, self.ID, self.signals)
        if self.type == "video":
            download.download_video()
        elif self.type == "audio":
            download.download_audio()
        else:
            download.download_both()
            


class Load_Thumbnail(QRunnable):
    
    def __init__(self, url, duration_str, index, signal, thumbnail_container):
        super().__init__()
        self.signals = signal
        self.url = url
        self.duration_str = duration_str
        self.index = index
        self.thumbnail_container = thumbnail_container

    def run(self):
        
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            img_data = BytesIO(response.content)
            pixmap = QPixmap()
            pixmap.loadFromData(img_data.read())
            self.signals.thumbnail_signal.emit(pixmap, self.duration_str, self.index, self.thumbnail_container)
        except Exception as e:
            return None
        
class Signals(QObject):
    #BackgroundOperations
    thumbnail_signal = pyqtSignal(QPixmap, str, int, QWidget)
    #FetchMetadata
    send_results = pyqtSignal(object)
    #HomePage
    #DownloadDialog
    format_selected = pyqtSignal(str, object, object)         #video, audio
    #DownloadPage
    refresh_downloads = pyqtSignal()
    show_downloads = pyqtSignal()
    
class FetchMetadata(QObject):
    def __init__(self, url_or_query, signals):
        super().__init__()
        self.signals = signals
        self.url_or_query = url_or_query
        self.is_running = True
#        self.starter_worker = self.start(self.url_or_query)
#        self.starter_worker.moveToThread(self.thread)
    
    def stop(self):
        if self.thread:
            self.thread.quit()

    def start(self):
        self.thread = QThread()
        self.download_worker = Download(self.url_or_query)
        self.download_worker.moveToThread(self.thread)
        self.download_worker.return_fetch_info.connect(self.receive_info)
        self.download_worker.return_fetch_info_error.connect(self.handle_error)
        self.thread.started.connect(self.download_worker.fetch_info)
        self.thread.start()
        print("fetching thread started...")

    def handle_error(self, err):
        print("Fetch failed:", err)

    def receive_info(self, info):
        print("recieve info started")
        self.info = info



#    downloader = Download(url_or_query)
#    downloader.fetch_info()

        if info and not isinstance(info, str):
            if isinstance(info, list):  # multiple results (playlist or search)
                fetched_info = []
                for i, video in enumerate(info, start=1):
                    try:
                        fetched_info.append({
                            "index" : i,
                            "ID" : video.get("id"),
                            "Title" : video.get("title"),
                            "Uploader" : video.get("uploader"),
                            "Duration" : video.get("duration"),
                            "Duration_str" : video.get("duration_str"),
                            "Thumbnail URL" : video.get("thumbnail"),
                            "Webpage URL" : video.get("url"),
                            "format": video.get("format", []),
                        })
                    except:
                        fetched_info = {}
            else:  # single video
                try:
                    fetched_info = []
                    fetched_info.append({
                        "index" : 1,
                        "ID" : info.get("id"),
                        "Title" : info.get("title"),
                        "Uploader" : info.get("uploader"),
                        "Duration" : info.get("duration"),
                        "Duration_str" : info.get("duration_str"),
                        "Thumbnail URL" : info.get("thumbnail"),
                        "Webpage URL" : info.get("url"),
                        "format": info.get("format", []),
                        })
                except: 
                    fetched_info = {}
            self.signals.send_results.emit(fetched_info)
        else:
            if info:
                print(info)
            else: 
                print("unknown exception")
        
        print("recieve info ended")

        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()


      
class DownloadDialog(QDialog):
    def __init__(self, video_info, signals, parent=None):
        super().__init__(parent) 
        self.setWindowTitle("Download Selection")
        self.signals = signals
        self.video_info = video_info  
        self.webpage_url = self.video_info.get("Webpage URL")
        self.vlayout = QVBoxLayout()
        self.setLayout(self.vlayout)
        self.video_h_layout = QHBoxLayout()
        self.video_v_layout = QVBoxLayout()
        self.combo_grid = QHBoxLayout()
        self.thumbnail_label = QLabel()
        self.audio_dropbox = QComboBox()
        self.video_dropbox = QComboBox()
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.formatting)
        try:
            response = requests.get(self.video_info.get("Thumbnail URL"), timeout=10)
            response.raise_for_status()
            img_data = BytesIO(response.content)
            pixmap = QPixmap()
            pixmap.loadFromData(img_data.read())
            self.thumbnail_label.setPixmap(pixmap.scaled(160*2, 90*2, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            pixmap = e
        self.vlayout.setContentsMargins(10, 10, 10, 10)
        self.vlayout.setSpacing(15)    


        self.thumbnail_label.setStyleSheet("border: 1px solid black;")
        self.title = QLabel(self.video_info.get("Title"))
        self.title.setWordWrap(True)
        self.duration = QLabel(self.video_info.get("Duration_str"))
        self.uploader = QLabel(f"by: {self.video_info.get("Uploader")}")
        self.video_v_layout.addWidget(self.title)
        self.video_v_layout.addWidget(self.duration)
        self.video_v_layout.addWidget(self.uploader)
        self.video_h_layout.addWidget(self.thumbnail_label)
        self.video_h_layout.addLayout(self.video_v_layout)
        self.vlayout.addLayout(self.video_h_layout)

        """

        """

        self.combo_grid.setContentsMargins(10, 10, 10, 10)
        self.combo_grid.setSpacing(15)    

        self.combo_grid.addWidget(self.video_dropbox)
        self.combo_grid.addWidget(self.audio_dropbox)

        self.vlayout.addLayout(self.combo_grid)
        self.vlayout.addWidget(self.download_button)

        self.title.setObjectName("title")
        self.duration.setObjectName("duration")
        self.uploader.setObjectName("uploader")
        self.download_button.setObjectName("download_button")
        self.setStyleSheet("""
                           QDialog{
                                background-color:#202020;
                            }
                           QLabel#title{
                                color: white; 
                                font-size: 14px;
                           }   
                           QLabel#duration, QLabel#uploader{
                                color: gray; 
                                font-size: 12px;
                           }
                           
                            QPushButton#download_button{
                                height : 50px;
                                margin: 3px;               
                                color: white;
                                background-color: hsl(221, 44%, 35%);
                                border: none;
                                border-radius: 8px;
                                font-size: 16px;
                                font-weight: bold;   
                            }
                            QComboBox{
                                padding : 10px;
                                font-size: 18px;
                                background-color : hsl(0, 0%, 67%);
                            }

                            QPushButton#download_button:hover {
                                background-color: hsl(221, 44%, 50%);
                            }

                            QPushButton#download_button:pressed {
                                background-color: hsl(221, 44%, 20%);
                            }
                            """)
    
        self.video_dropbox.addItem("Video-Null", "None")
        self.audio_dropbox.addItem("Audio-Null", "None")
    
        formats = video_info.get("format")
#        print(formats)
        self.video_formats = [f for f in formats if f.get("vcodec") != "none" and f.get("acodec") == "none"]
        self.audio_formats = [f for f in formats if f.get("acodec") != "none" and f.get("vcodec") == "none"]

#        print(self.video_formats)
#        print(self.audio_formats)

        for format in self.video_formats:
            self.video_dropbox.addItem(f"{format.get("height")}p---{format.get("ext")}",format.get("format_id"))
#            print("video",format.get("format_id"))
        for format in self.audio_formats:
            self.audio_dropbox.addItem(f"{format.get("abr")}kbps---{format.get("ext")}",format.get("format_id"))
#            print("audio",format.get("format_id"))
        
        self.video_dropbox.addItem("Best Video---any","bv*")
        self.video_dropbox.addItem("Best Video---MP4","bv*[ext=mp4]")
        self.audio_dropbox.addItem("Best Audio","ba")

        
    def formatting(self):
        video_selection = self.video_dropbox.currentData()
        audio_selection = self.audio_dropbox.currentData()

        video_download_format = video_selection if video_selection != "None" else None
        audio_download_format = audio_selection if audio_selection != "None" else None

        print(video_download_format)
        print(audio_download_format)

        if video_download_format or audio_download_format:
            self.signals.format_selected.emit(self.webpage_url, video_download_format, audio_download_format)
            self.logging()
            self.accept()
    
    def logging(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as s:
                settings = json.load(s)
                settings_dict = settings.get("MainWindow")
                self.log_history_enabled = settings_dict.get("LogHistory", False)
                if not self.log_history_enabled:
                    return
                self.NumberOfHistoryRecords = int(settings_dict.get("NumberOfHistoryRecords", 10))
        Title = self.video_info.get("Title")
        Thumbnail_URL = self.video_info.get("Thumbnail URL") 
        Uploader = self.video_info.get("Uploader")
        Path = str(settings["Downloader"].get("download_path"))

        writing = ["url","title", "Thumbnail URL","Uploader","path","status"]
        writing[5] = "Started---INCOMPLETE"
        writing[0:5] = [self.webpage_url, Title, Thumbnail_URL, Uploader, Path,]
        if os.path.exists("history.json"):
            with open("history.json", "r") as r:
                record = json.load(r)
                
        else:
            record = []
        record.append(writing)
        if len(record) > self.NumberOfHistoryRecords:
            record.pop(0)
        with open("history.json", "w") as history:
            json.dump(record, history, indent=4)

        self.signals.refresh_downloads.emit()

class SettingsDialog(QDialog):
    def __init__(self, parent=None, pool=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(500, 500)
        self.setMinimumSize(450, 450)
        self.setMaximumSize(650, 700)

        self.thread_pool = pool
        self.create_widget()
        self.layout()
        self.connections()
        self.starter()
        self.stylesheets()
    
    def layout(self): 
        container = QWidget()
        self.vlayout = QVBoxLayout(container)
        self.vlayout.setSpacing(10)
        self.vlayout.setContentsMargins(15, 15, 15, 15)


        log_history = QHBoxLayout()
        thread_pool_size = QHBoxLayout()
        history_record_number = QHBoxLayout()
        download_path = QHBoxLayout()
        embed_subs = QHBoxLayout()
        auto_gen_subs = QHBoxLayout()
        external_downloader = QHBoxLayout()
        search_limit = QHBoxLayout()
 
        thread_pool_size_v = QVBoxLayout()
        history_record_number_v = QVBoxLayout()
        download_path_v = QVBoxLayout()
        external_downloader_v = QVBoxLayout()
        search_limit_v = QVBoxLayout()

        thread_pool_size_v.addWidget(self.thread_pool_size_label)
        thread_pool_size_v.addWidget(self.thread_pool_size_add_label)
        history_record_number_v.addWidget(self.history_record_number_label)
        history_record_number_v.addWidget(self.history_record_number_add_label)
        download_path_v.addWidget(self.download_path_label)
        download_path_v.addWidget(self.download_path_add_label)
        external_downloader_v.addWidget(self.external_downloader_label)
        external_downloader_v.addWidget(self.external_downloader_add_label)
        search_limit_v.addWidget(self.search_limit_label)
        search_limit_v.addWidget(self.search_limit_add_label)
        
        log_history.addWidget(self.log_history_label)
        thread_pool_size.addLayout(thread_pool_size_v)
        history_record_number.addLayout(history_record_number_v)
        download_path.addLayout(download_path_v)
        embed_subs.addWidget(self.embed_subs_label)
        auto_gen_subs.addWidget(self.auto_gen_subs_label)
        external_downloader.addLayout(external_downloader_v)
        search_limit.addLayout(search_limit_v)

        log_history.addStretch()
        thread_pool_size.addStretch()
        history_record_number.addStretch()
        download_path.addStretch()
        embed_subs.addStretch()
        auto_gen_subs.addStretch()
        external_downloader.addStretch()
        search_limit.addStretch()

        log_history.addWidget(self.log_history_button)
        thread_pool_size.addWidget(self.thread_pool_size_combo)
        history_record_number.addWidget(self.history_record_number_combo)
        download_path.addWidget(self.download_path_button_rst)
        download_path.addWidget(self.download_path_button)
        embed_subs.addWidget(self.embed_subs_button)
        auto_gen_subs.addWidget(self.auto_gen_subs_button)
        external_downloader.addWidget(self.external_downloader_button)
        search_limit.addWidget(self.search_limit_combo)

        self.vlayout.addLayout(log_history)
        self.vlayout.addLayout(thread_pool_size)
        self.vlayout.addLayout(history_record_number)
        self.vlayout.addLayout(download_path)
        self.vlayout.addLayout(embed_subs)
        self.vlayout.addLayout(auto_gen_subs)
        self.vlayout.addLayout(external_downloader)
        self.vlayout.addLayout(search_limit)


#        self.vlayout.addWidget(card)
        self.vlayout.addStretch()

        main_layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        main_layout.addWidget(scroll)
        pwr_btn_layout = QHBoxLayout(main_layout)
        pwr_btn_layout.addStretch()
        pwr_btn_layout.addWidget(self.rst)
        pwr_btn_layout.addWidget(self.save)
        self.setLayout(main_layout)
       
    def divider(self, height=1, color="#ccc"):
        """Creates a flat divider."""
        line = QWidget()
        line.setFixedHeight(height)
        line.setStyleSheet(f"background-color: {color};")
        return line
    
    def create_widget(self):
        self.rst = QPushButton("Reset To Default")
        self.save = QPushButton("Save Changes")

        self.log_history_label = QLabel("Log History")
        self.log_history_button = QPushButton()
        self.log_history_button.setCheckable(True)

        self.thread_pool_size_label = QLabel(f"Number Of Threads For Downloading") 
        self.thread_pool_size_label.setWordWrap(True) 
        self.thread_pool_size_combo = QComboBox()
        self.thread_pool_size_combo.addItems(["-1"]+[str(i) for i in range(1, self.thread_pool.maxThreadCount() + 1)]) 
        self.thread_pool_size_add_label = QLabel(f"Set '-1' For Default({QThread.idealThreadCount()})") 
        self.thread_pool_size_add_label.setWordWrap(True) 

        self.history_record_number_label = QLabel("Number Of History Records")
        self.history_record_number_label.setWordWrap(True)
        self.history_record_number_combo = QComboBox()
        self.history_record_number_combo.addItems(["-1"]+[str(_) for _ in range(1, 101)])
        self.history_record_number_add_label = QLabel("Set '-1' For Default(10)")
        self.history_record_number_add_label.setWordWrap(True)

        self.download_path_label = QLabel("Select Download Path")
        self.download_path_label.setWordWrap(True)
        self.download_path_button = QPushButton()

        self.download_path_button_rst = QPushButton()
        self.download_path_button_rst.setIcon(qta.icon("fa5s.times", color="red"))
        self.download_path_button_rst.setIconSize(QSize(24, 24))
        self.download_path_button_rst.setFlat(True)

        self.download_path_add_label = QLabel("Leave Empty For Default(User/Downloads/YT-DLP)")
        self.download_path_add_label.setWordWrap(True)

        self.embed_subs_label = QLabel("Embed Subtitles")
        self.embed_subs_label.setWordWrap(True)
        self.embed_subs_button = QPushButton()
        self.embed_subs_button.setCheckable(True)

        self.auto_gen_subs_label = QLabel("Embed Auto Gen Subtitles")
        self.auto_gen_subs_label.setWordWrap(True)
        self.auto_gen_subs_button = QPushButton()
        self.auto_gen_subs_button.setCheckable(True)

        self.external_downloader_label = QLabel("Use External Downloader")
        self.external_downloader_label.setWordWrap(True)
        self.external_downloader_button = QPushButton()
        self.external_downloader_button.setCheckable(True)
        self.external_downloader_add_label = QLabel("Address 'settings.json' to change external downloader and its settings")
        self.external_downloader_add_label.setWordWrap(True)

        self.search_limit_label = QLabel("Number Of Search Results")
        self.search_limit_label.setWordWrap(True)
        self.search_limit_combo = QComboBox()
        self.search_limit_combo.addItems(["-1"]+[str(_) for _ in range(1, 16)])
        self.search_limit_add_label = QLabel("Set '-1' For Default(5)")
        self.search_limit_add_label.setWordWrap(True)

        
    def starter(self):
        self.DEFAULTS = {
    "MainWindow" : {"ThreadPoolSize" : None,
                    "LogHistory" : True,
                    "NumberOfHistoryRecords" : 10
},
    "Downloader" : {"download_path" : str(Path.home() / "Downloads" / "MorpheusDL"),          #None Sets as default in downloader script
                    "EmbedSubtitles" : False,
                    "WriteAutoSub": False,
                    "UseExternalDownloader": True,
                    "ExternalDownloader": "aria2c",
                    "ExternalDownloaderArgs": ["-x", "16", "-k", "1M"] 
},
        "Fetching"  : {
        "SearchLimit" : 5
},       
        "Themes"    : {
            "Default" : "background-color:",
            "Dark"  :   "background-color:"
}
}       
        if not os.path.exists("settings.json"):
            self.reset()
        
        self.read()

        for button in self.findChildren(QPushButton):
            if button not in (self.rst, self.save):
                self.button_default_state(button)


    def stylesheets(self):
        self.embed_subs_label.setObjectName("Label")
        self.log_history_label.setObjectName("Label")
        self.search_limit_label.setObjectName("Label")
        self.auto_gen_subs_label.setObjectName("Label")
        self.download_path_label.setObjectName("Label")
        self.thread_pool_size_label.setObjectName("Label")
        self.external_downloader_label.setObjectName("Label")
        self.history_record_number_label.setObjectName("Label")

        self.thread_pool_size_add_label.setObjectName("addLabel")
        self.history_record_number_add_label.setObjectName("addLabel")
        self.download_path_add_label.setObjectName("addLabel")
        self.external_downloader_add_label.setObjectName("addLabel")
        self.search_limit_add_label.setObjectName("addLabel")

        self.download_path_button_rst.setObjectName("download_path_button_rst")

        self.setStyleSheet("""
                            QFrame {
                                    background: #2c2c2c;
                                    border: 1px solid #444;
                                    border-radius: 8px;
                                    padding: 10px;
                            }
                            QDialog {
                                background: #1e1e1e;
                            }
                            QFrame {
                                background: #2c2c2c;
                                border: 1px solid #444;
                                border-radius: 8px;
                                padding: 10px;
                            }
                            QLabel#Label{
                                font-size : 18px;
                                color : hsl(0, 0%, 67%);
                                font-family : Arial;
                            }
                           
                            QLabel#addLabel{
                                font-size : 12px;
                                font-style: italic;
                                color : hsl(0, 0%, 67%);
                                font-family : Arial;
                            }
                            QPushButton{
                                padding: 10px;
                                height : 50px;
                                margin: 3px;               
                                color: white;
                                background-color: hsl(221, 44%, 35%);
                                border: none;
                                border-radius: 8px;
                                font-size: 16px;
                                font-weight: bold;   
                            }
                            QComboBox {
                                background-color: #3c3c3c;
                                color: white;
                                border: 1px solid #555;
                                border-radius: 6px;
                                padding: 6px 8px;
                                font-size: 14px;
                            }
                            QComboBox::drop-down {
                                subcontrol-origin: padding;
                                subcontrol-position: top right;
                                width: 25px;
                                border-left: 1px solid #555;
                                background-color: #2c2c2c;
                                border-top-right-radius: 6px;
                                border-bottom-right-radius: 6px;
                            }
                            QComboBox::down-arrow {
                                width: 12px;
                                height: 12px;
                            }
                            QComboBox QAbstractItemView {
                                background-color: #2c2c2c;
                                color: white;
                                selection-background-color: #505050;
                                border: 1px solid #555;
                                padding: 4px;
                            }
                            QPushButton:checked, QPushButton:pressed {
                                background-color: #e53935;  /* Red when ON */
                            }
                           QPushButton#download_path_button_rst{
                                border: none; 
                                background: transparent;
                           }
                           """)

    def connections(self):
        self.rst.clicked.connect(self.reset)
        self.save.clicked.connect(self.write)
        self.download_path_button.clicked.connect(self.open_dir)
        self.download_path_button.clicked.connect(lambda: self.download_path_button.setText(str(Path.home() / "Downloads" / "MorpheusDL")))
        for button in self.findChildren(QPushButton):
            if button not in (self.rst, self.save):
                button.clicked.connect(self.on_any_button_clicked)

    def on_any_button_clicked(self):
        sender = self.sender()# Get which button triggered it
        if sender.isChecked():
            sender.setText("ON")  
        else:
            sender.setText("OFF")  

    def button_default_state(self, sender):
        if sender.isChecked():
            sender.setText("ON")  
        else:
            sender.setText("OFF")  



    def open_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.download_path_button = folder


    def read(self):
        with open("settings.json", "r") as s:
            settings = json.load(s)
        
        self.thread_pool_size_combo.setCurrentText(str(settings["MainWindow"]["ThreadPoolSize"]))
        self.log_history_button.setChecked(settings["MainWindow"]["LogHistory"])
        self.history_record_number_combo.setCurrentText(str(settings["MainWindow"]["NumberOfHistoryRecords"]))

        self.embed_subs_button.setChecked(settings["Downloader"]["EmbedSubtitles"])
        self.auto_gen_subs_button.setChecked(settings["Downloader"]["WriteAutoSub"])
        self.external_downloader_button.setChecked(settings["Downloader"]["UseExternalDownloader"])
        self.external_downloader_button.setChecked(settings["Downloader"]["UseExternalDownloader"])

        self.search_limit_combo.setCurrentText(str(settings["Fetching"]["SearchLimit"]))


    def reset(self):
        with open("settings.json", "w") as settings:
            json.dump(self.DEFAULTS, settings, indent=4)
        self.starter()

    def write(self):
        temp = {
    "MainWindow" : {"ThreadPoolSize" : None if self.thread_pool_size_combo.currentText() == "-1" else int(self.thread_pool_size_combo.currentText()),
                    "LogHistory" : self.log_history_button.isChecked(),
                    "NumberOfHistoryRecords" : 10 if self.history_record_number_combo.currentText() == "-1" else int(self.history_record_number_combo.currentText())
                    
},
    "Downloader" : {"download_path" :  self.download_path_button.text(),          #'None' Sets as default in downloader script
                    "EmbedSubtitles" : self.embed_subs_button.isChecked(),
                    "WriteAutoSub": self.auto_gen_subs_button.isChecked(),
                    "UseExternalDownloader": self.external_downloader_button.isChecked(),
                    "ExternalDownloader": "aria2c",
                    "ExternalDownloaderArgs": ["-x", "16", "-k", "1M"] 
},
        "Fetching"  : {
        "SearchLimit" : 5 if self.search_limit_combo.currentText() == "-1" else int(self.search_limit_combo.currentText())
}       
}       
        with open("settings.json", "w") as settings:
            json.dump(temp, settings, indent=4)

        self.accept()

class DownloadPage(QWidget):
    def __init__(self, signals):
        super().__init__()
        self.signals = signals
        self.thread_pool = QThreadPool()
        self.create_widgets()
        self.layouts()
        self.connections()
        self.starter()
        self.stylesheets()

    def starter(self):
        self.update_pending = False
        self.read_history()

    def connections(self):
        self.download_history_list.itemClicked.connect(copy)
        self.clear_all.clicked.connect(clear)
        self.clear_all.clicked.connect(self.read_history)
        self.signals.refresh_downloads.connect(self.schedule_update_downloads)
        self.signals.show_downloads.connect(self.update_downloads)

    def stylesheets(self):
        self.clear_all.setObjectName("clear_all")
        self.switch_to_home_button.setObjectName("home_button")
        self.title.setObjectName("title")
        self.logo.setObjectName("logo")
        

        self.setStyleSheet("""
                        QLabel#logo{
                           padding-right: 10px;
                        }
                        QPushButton#clear_all{
                           padding-right: 0px;
                        }
                        QPushButton#home_button{
                            border: none;
                            padding: 6px;
                            margin-left: 0px;
                            height : 80px;
                            width : 90px;
                        }
                        QLabel#title{
                           font-size : 30px;
                           font-weight : bold;
                           margin : 1px;
                           margin-top : 40px;  
                           padding: -10px;
                        }
                        QPushButton#clear_all{
                            height : 50px;
                            width : 130px;
                            margin-left : 3px;               
                            color: white;
                            background-color: hsl(221, 44%, 35%);
                            border: none;
                            padding: 8px 16px;
                            border-radius: 8px;
                            font-size: 16px;
                            font-weight: bold;
                           }
                        QPushButton#clear_all:hover{
                            background-color: hsl(221, 44%, 50%);
                           }
                        QPushButton#clear_all:pressed{
                                background-color: hsl(221, 44%, 20%);
                           }
                        """)

        self.logo_container.setAlignment(Qt.AlignTop)
        self.title.setAlignment(Qt.AlignLeft)
        self.download_history_list.setItemAlignment(Qt.AlignHCenter)
        
        pixmap = QPixmap("icon(1).png")
        scaled_pixmap = pixmap.scaled(150, 150, aspectRatioMode=Qt.KeepAspectRatio)
        self.logo.setPixmap(scaled_pixmap)

    def layouts(self):
        self.main_v_layout = QVBoxLayout()
        self.setLayout(self.main_v_layout)

        self.logo_container = QHBoxLayout()
        self.logo_container.addWidget(self.switch_to_home_button)
        self.logo_container.addStretch()
        self.logo_container.addWidget(self.logo)
        self.logo_container.addStretch()

        self.main_v_layout.addLayout(self.logo_container)

        self.title_container = QHBoxLayout()
        self.title_container.addWidget(self.title)
        self.title_container.addStretch()
        self.title_container.addWidget(self.clear_all)

        self.main_v_layout.addLayout(self.title_container)
        self.main_v_layout.addWidget(self.download_history_list)        

    def create_widgets(self):
        icon = qta.icon("fa5s.arrow-left", scale_factor=1.0)
        self.switch_to_home_button = QPushButton()
        self.switch_to_home_button.setIcon(icon)
        self.switch_to_home_button.setIconSize(QSize(60,60))
        self.logo = QLabel(self)                 
        self.title = QLabel("Downloads...", self)
        self.clear_all = QPushButton("Clear All", self)
        self.download_history_list = QListWidget(self)

    def read_history(self):
        if os.path.exists("history.json"):
            with open("history.json", "r") as r:
                records = json.load(r)
                records.reverse()
                index = 0
                self.download_history_list.clear()
                for record in records:
                    index += 1
                    url = record[0]
                    title = record[1]
                    Thumbnail_URL = record[2]
                    uploader = record[3]
                    location = record[4]
                    status = record[5]
                    self.update_search_list(index, url, title, Thumbnail_URL, uploader, location, status)

    
    def update_search_list(self, index, url, Title, Thumbnail_URL, Uploader, location, status):

            custom_item_widget = QWidget()
            custom_item_widget.setMinimumHeight(120)
            custom_item_widget.setStyleSheet("background-color: #202020; border: 1px solid #444;")
            hbox = QHBoxLayout(custom_item_widget)
            hbox.setContentsMargins(10, 10, 10, 10)
            hbox.setSpacing(15)
            # Index
            index_label = QLabel(str(index))
            index_label.setStyleSheet("color: white; font-weight: bold; border: none;")
            index_label.setFixedSize(50, 50)
            hbox.addWidget(index_label)
            # Thumbnail
            thumbnail_container = QWidget()
            thumbnail_container.setFixedSize(160, 90)
            thumbnail_container.setStyleSheet("background-color: black;")
            custom_item_widget.thumbnail_container = thumbnail_container
            hbox.addWidget(thumbnail_container)
            # Info container
            info_container = QWidget()
            info_layout = QVBoxLayout(info_container)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(5)
            # Title
            title_label = QLabel(Title or "No Title")
            title_label.setStyleSheet("color: white; font-size: 14px;")
            title_label.setWordWrap(True)
            info_layout.addWidget(title_label)
#           # Duration_str
#           duration_label = QLabel(result.get("Duration_str", "Unknown duration") )
#           duration_label.setStyleSheet("color: gray; font-size: 12px;")
#           title_label.setWordWrap(True)
#           info_layout.addWidget(duration_label)

            # Uploader
            uploader_label = QLabel(f"By: {Uploader or 'Unknown'}       {location}      {status}")
            uploader_label.setStyleSheet("color: gray; font-size: 12px;")
            info_layout.addWidget(uploader_label)
            hbox.addWidget(info_container)
            # Final setup
            item = QListWidgetItem()
            item.setSizeHint(custom_item_widget.sizeHint())
            item.setData(Qt.UserRole, url)
            self.download_history_list.addItem(item)
            self.download_history_list.setItemWidget(item, custom_item_widget)
            # Start thumbnail loader
            duration_str = ""
            worker = Load_Thumbnail(Thumbnail_URL, duration_str, index, self.signals, thumbnail_container)
            self.thread_pool.start(worker)

    def add_thumbnail(self, thumbnail_pixmap, duration_text, index, thumbnail_container):
        if thumbnail_pixmap:
            thumbnail_layout = QVBoxLayout()
            thumbnail_layout.setContentsMargins(0, 0, 0, 0)
            thumbnail_container.setLayout(thumbnail_layout)

            self.thumbnail_label = QLabel()
            widget = QWidget()
            layout = QStackedLayout()
            layout.setContentsMargins(0, 0, 0, 0)

            self.thumbnail_label.setPixmap(thumbnail_pixmap.scaled(160, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.thumbnail_label.setStyleSheet("border: 1px solid black;")


            overlay_container = QWidget()
            overlay_layout = QVBoxLayout(overlay_container)
            overlay_layout.addStretch()
            overlay_layout.addWidget(self.duration_label, alignment=Qt.AlignRight | Qt.AlignBottom)
            overlay_layout.setContentsMargins(5, 5, 5, 5)

            layout.addWidget(self.thumbnail_label)
            layout.addWidget(overlay_container)

            widget.setLayout(layout)
            thumbnail_layout.addWidget(widget)

    def schedule_update_downloads(self):
        self.update_pending = True

    def update_downloads(self):
        if self.update_pending:
            self.read_history()
            self.update_pending = not True

@staticmethod
def clear():
    with open("history.json", "w") as h:
        json.dump([], h)
@staticmethod
def copy(item):
    url = item.data(Qt.UserRole)
    QApplication.clipboard().setText(url)
    
class HomePage(QWidget):
    def __init__(self, scroll, signals):
        super().__init__()
        self.signals = signals
        self.scroll = scroll
        self.create_widgets()
        self.layouts()
        self.stylesheets()
        self.connections()
        self.starter()

    def starter(self):
        self.w.hide()
        self.result_list.hide()
        self.download_button.hide()
        self.thread_pool = QThreadPool()
        self.fetcher = None
        self.format_selected = None
        self.read_settings()


    def connections(self):
        self.submit_button.clicked.connect(self.submit_button_clicked)
        self.signals.send_results.connect(self.update_search_list)
        self.signals.thumbnail_signal.connect(self.add_thumbnail)
        self.result_list.itemClicked.connect(self.open_download_dialog)
        self.signals.format_selected.connect(self.format_selected)
        self.switch_to_downloads_button.clicked.connect(self.show_downloads)
#        self.settings_button.clicked.connect(self.open_settings_dialog)
        self.download_button.clicked.connect(self.download_all)

    def stylesheets(self):
        self.settings_button.setObjectName("settings_button")
        self.logo.setObjectName("logo")
        self.header1.setObjectName("header1")
        self.header2.setObjectName("header2")
        self.header3.setObjectName("header3")
        self.description.setObjectName("description")
        self.submit_button.setObjectName("submit_button")
        self.download_button.setObjectName("download_button")
        self.switch_to_downloads_button.setObjectName("switch_to_download")


        self.setStyleSheet("""
                        QWidget{
                           color : white;
                           background-color : hsl(0, 0%, 12%);
                           }
                        QLabel#logo{
                            padding-left : 30px;
                           }
                        QLabel#header1, QLabel#header2, QLabel#header3{
                            font-size : 80px;
                            color: hsl(0, 100%, 50%);
                            font-weight : bold;
                            margin : 1px;
                            padding: -10px;
                           }
                    
                        QLabel#header2{
                           margin-left: 0px;
                           margin-right: 0px;
                           }
                        QLabel#description{
                            font-size : 18px;
                            color : hsl(0, 0%, 67%);
                            font-family : Arial;
                           }
                        QLineEdit{             
                            border: 1px solid hsl(0, 0%, 25%);
                            padding: 8px;
                            border-radius: 6px;
                            color: white;
                            font-size: 16px;
                            margin-left : 150px ;   
                            margin-bottom : 100px;
                            font-weight : bold;
                            height : 50px;
                            width : 400px;
                           }
                        QPushButton#submit_button, QPushButton#download_button{
                            height : 50px;
                            width : 130px;
                            margin-left : 3px;               
                            color: white;
                            background-color: hsl(221, 44%, 35%);
                            border: none;
                            padding: 8px 16px;
                            border-radius: 8px;
                            font-size: 16px;
                            font-weight: bold;
                           }
                        QPushButton#submit_button{
                            margin-bottom : 100px;
                            margin-right : 150px;    
                        }

                        QPushButton#submit_button:hover, QPushButton#download_button:hover {
                            background-color: hsl(221, 44%, 50%);
                           }

                        QPushButton#submit_button:pressed, QPushButton#download_button:pressed {
                                background-color: hsl(221, 44%, 20%);
                           }
                        QListWidget {
                            background-color: hsl(0, 0%, 15%);
                            color: white;
                            font-size: 16px;
                            border: none;
                            padding: 10px;
                        }
                        QListWidget::item {
                            padding: 10px;
                        }
                        QPushButton#switch_to_download{
                            border: none;
                            padding: 0px;
                            padding-right: 0px;
                            height : 60px;
                            width : 50px;
                        }
                        QPushButton#settings_button{
                            border: none;
                            background-color: transparent;
                        }
""")
        self.logo_container.setAlignment(Qt.AlignTop)
        self.header_container.setAlignment(Qt.AlignCenter)
        self.description.setAlignment(Qt.AlignCenter)
        self.input_box.setAlignment(Qt.AlignCenter)
        self.result_list.setMinimumHeight(500)
        icon = qta.icon("fa5s.download", scale_factor=1.0)
        self.switch_to_downloads_button.setIcon(icon)
        self.switch_to_downloads_button.setIconSize(QSize(40,40))

        pixmap = QPixmap("icon(1).png")
        scaled_pixmap = pixmap.scaled(150, 150, aspectRatioMode=Qt.KeepAspectRatio)
        self.logo.setPixmap(scaled_pixmap)

        self.settings_button.setIcon(qta.icon("fa5s.cog"))
        self.settings_button.setIconSize(QSize(40, 40))   # Adjust size
        self.settings_button.setFixedSize(40, 40) 

        font_id = QFontDatabase.addApplicationFont("fonts/Serpentine-BoldOblique Regular/Serpentine-BoldOblique Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        my_font = QFont(font_family) 
        self.header2.setFont(my_font)


    def layouts(self):
        self.main_v_layout = QVBoxLayout()
        self.setLayout(self.main_v_layout)

        self.w = QWidget()

        self.logo_container = QHBoxLayout()
        self.logo_container.addWidget(self.settings_button)
        self.logo_container.addStretch()
        self.logo_container.addWidget(self.logo)
        self.logo_container.addStretch()
        self.logo_container.addWidget(self.switch_to_downloads_button)

        self.header_container = QHBoxLayout()
        self.header_container.addStretch()
        self.header_container.addWidget(self.header1)
        self.header_container.addWidget(self.header2)
        self.header_container.addWidget(self.header3)
        self.header_container.addStretch()

        self.input_container = QHBoxLayout()
        self.input_container.addStretch()
        self.input_container.addWidget(self.input_box)
        self.input_container.addWidget(self.submit_button)
        self.input_container.addStretch()


        self.main_v_layout.addLayout(self.logo_container)
        self.main_v_layout.addLayout(self.header_container)
        self.main_v_layout.addWidget(self.description)
        self.main_v_layout.addLayout(self.input_container)
        
        self.main_v_layout.addWidget(self.result_list)
        self.main_v_layout.addWidget(self.download_button)
        self.main_v_layout.addWidget(self.w)

        
    def create_widgets(self):
        self.settings_button = QPushButton(self)
        self.logo = QLabel(self)            
        self.switch_to_downloads_button = QPushButton(self)
        self.header1 = QLabel("", self)
        self.header2 = GlitchTitle()
        self.header3 = QLabel("", self)
        self.description = QLabel("Take The Red Pill... \n You Stay In WonderLand And \n I Show You How Deep Your Downloads Go.", self)
        self.input_box = QLineEdit(self)
        self.input_box.setPlaceholderText("Search or Paste URL Here...")
        self.submit_button = QPushButton("Submit",self)
        self.result_list = QListWidget(self)
        self.download_button = QPushButton("Download All", self)
    
    def read_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as settings:
                settings_dict = json.load(settings).get("MainWindow")
                if settings_dict.get("ThreadPoolSize"):
                    thread_count = int(settings_dict.get("ThreadPoolSize"))
                    self.thread_pool.setMaxThreadCount(thread_count)     
    
    def submit_button_clicked(self):      
        if self.input_box.text():  
            self.result_list.clear()

            self.result_list.hide()
            self.download_button.hide()
            self.stop_fetching()
            
        else:
            self.warning_msg()
    
    def stop_fetching(self):
        if self.fetcher is not None and self.fetcher.thread.isRunning():
            print("Stopping previous thread...")
            self.fetcher.thread.finished.connect(self.delete_thread)
            self.fetcher.thread.finished.connect(self.start_fetching)
#            self.fetcher.thread.quit()
            self.fetcher.stop()
#            self.fetcher.thread.finished.connect(self.fetcher.thread.deleteLater)
            print("previous thread stopped...")
#            self.start_fetching(self.input_box.text(),self.signals)
        else:
            self.start_fetching()
    
    def delete_thread(self):
        print("deleting thread...")
        self.fetcher.download_worker.deleteLater()
        self.fetcher = None  # Remove reference
        self.current_thread = None
        print("thread deleted...")
        

    def start_fetching(self):
        text = self.input_box.text()
        signals = self.signals
        print("new thread starting...")
        self.fetcher = FetchMetadata(text, signals)
        self.fetcher.start()
        print("new thread started...")

    def show_downloads(self):
        self.signals.show_downloads.emit()
    @staticmethod
    def warning_msg():
        box = QMessageBox.warning(None, "Invalid Input(Empty)", "Search or Enter URL...")

    def open_download_dialog(self, item):
        video_options = item.data(Qt.UserRole)
        dialog = DownloadDialog(video_options, self.signals, self)
        dialog.exec_()

    def open_settings_dialog(self):
        dialog = SettingsDialog(self, pool=self.thread_pool)
        dialog.exec_()

    def format_selected(self, webpage_url, video_format, audio_format):
        url =  webpage_url
        video_format_selected = video_format
        audio_format_selected = audio_format

        if video_format_selected and audio_format_selected:
            final_format = f"{video_format_selected}+{audio_format_selected}" 
            worker = Download_starter(url, final_format, "both", self.signals)
            self.thread_pool.start(worker)
        else:
            if audio_format_selected:
                worker = Download_starter(url, audio_format_selected, "audio", self.signals)
                self.thread_pool.start(worker)
            if video_format_selected:
                worker = Download_starter(url, video_format_selected, "video", self.signals)
                self.thread_pool.start(worker)

    def download_all(self):
        for row in range(self.result_list.count()):
            item = self.result_list.item(row)
            self.open_download_dialog(item)
    
    def update_search_list(self, fetched_search_results):
        self.fetcher.thread.finished.connect(self.delete_thread)

        if isinstance(fetched_search_results, list):
            for result in fetched_search_results:
                custom_item_widget = QWidget()
                custom_item_widget.setMinimumHeight(120)
                custom_item_widget.setStyleSheet("background-color: #202020; border: 1px solid #444;")

                hbox = QHBoxLayout(custom_item_widget)
                hbox.setContentsMargins(10, 10, 10, 10)
                hbox.setSpacing(15)

                # Index
                index_label = QLabel(str(result.get("index")))
                index_label.setStyleSheet("color: white; font-weight: bold; border: none;")
                index_label.setFixedSize(50, 50)
                hbox.addWidget(index_label)

                # Thumbnail
                thumbnail_container = QWidget()
                thumbnail_container.setFixedSize(160, 90)
                thumbnail_container.setStyleSheet("background-color: black;")
                custom_item_widget.thumbnail_container = thumbnail_container
                hbox.addWidget(thumbnail_container)

                # Info container
                info_container = QWidget()
                info_layout = QVBoxLayout(info_container)
                info_layout.setContentsMargins(0, 0, 0, 0)
                info_layout.setSpacing(5)

                # Title
                title_label = QLabel(result.get("Title", "No Title"))
                title_label.setStyleSheet("color: white; font-size: 14px;")
                title_label.setWordWrap(True)
                info_layout.addWidget(title_label)

#                # Duration_str
#                duration_label = QLabel(result.get("Duration_str", "Unknown duration") )
#                duration_label.setStyleSheet("color: gray; font-size: 12px;")
#                title_label.setWordWrap(True)
#                info_layout.addWidget(duration_label)

                # Uploader
                uploader_label = QLabel(f"By: {result.get('Uploader', 'Unknown')}      [{result.get("Duration_str", "Unknown duration")}]")
                uploader_label.setStyleSheet("color: gray; font-size: 12px;")
                info_layout.addWidget(uploader_label)

                hbox.addWidget(info_container)

                # Final setup
                item = QListWidgetItem()
                item.setSizeHint(custom_item_widget.sizeHint())
                item.setData(Qt.UserRole, result)

                self.result_list.addItem(item)
                self.result_list.setItemWidget(item, custom_item_widget)

                # Start thumbnail loader
                worker = Load_Thumbnail(result.get("Thumbnail URL"), result.get("Duration_str"), result.get("index"), self.signals, thumbnail_container)
                self.thread_pool.start(worker)
        self.w.hide()
        self.result_list.show()
        self.download_button.show()
    def add_thumbnail(self, thumbnail_pixmap, duration_text, index, thumbnail_container):
        if thumbnail_pixmap:
            thumbnail_layout = QVBoxLayout()
            thumbnail_layout.setContentsMargins(0, 0, 0, 0)
            thumbnail_container.setLayout(thumbnail_layout)

            self.thumbnail_label = QLabel()
            widget = QWidget()
            layout = QStackedLayout()
            layout.setContentsMargins(0, 0, 0, 0)

            self.thumbnail_label.setPixmap(thumbnail_pixmap.scaled(160, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.thumbnail_label.setStyleSheet("border: 1px solid black;")

            self.duration_label = QLabel(duration_text)
            self.duration_label.setStyleSheet("""
                background-color: rgba(0, 0, 0, 150);
                color: white;
                font-size: 10px;
                padding: 1px 4px;
            """)
            self.duration_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)

            overlay_container = QWidget()
            overlay_layout = QVBoxLayout(overlay_container)
            overlay_layout.addStretch()
            overlay_layout.addWidget(self.duration_label, alignment=Qt.AlignRight | Qt.AlignBottom)
            overlay_layout.setContentsMargins(5, 5, 5, 5)

            layout.addWidget(self.thumbnail_label)
            layout.addWidget(overlay_container)

            widget.setLayout(layout)
            thumbnail_layout.addWidget(widget)
            self.smooth_scroll_to(self.result_list)

    def smooth_scroll_to(self, widget):
        # Get the vertical scroll position of the widget inside the scroll area
        y = widget.mapTo(self, QPoint(0, 0)).y()
        
        
        scroll_bar = self.scroll.verticalScrollBar()

        # Animate from current position to target
        animation = QPropertyAnimation(scroll_bar, b"value", self)
        animation.setDuration(500)  # ms
        animation.setStartValue(scroll_bar.value())
        animation.setEndValue(y)
        animation.start()
        
        # Keep a reference so animation isn't garbage collected
        self.scroll_animation = animation


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MorpheusDL")
        self.setWindowIcon(QIcon("icon.png"))
        self.setMinimumHeight(500)
        self.setMinimumWidth(1000)
        self.signals = Signals()

        self.scroll = QScrollArea()

        self.stacked_widgets = QStackedWidget()

        self.home_page = HomePage(self.scroll, self.signals) 
        self.download_page = DownloadPage(self.signals) 


        self.stacked_widgets.addWidget(self.home_page)
        self.stacked_widgets.addWidget(self.download_page)

        self.stacked_widgets.setCurrentWidget(self.home_page)

        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.stacked_widgets)
        self.setCentralWidget(self.scroll)

        self.setStyleSheet("""
                        QScrollArea,QStackedWidget, QWidget{
                           color : white;
                           background-color : hsl(0, 0%, 12%);
                           margin : 10px;
                           }""")
        self.home_page.switch_to_downloads_button.clicked.connect(self.apply_download_page)
        self.download_page.switch_to_home_button.clicked.connect(self.apply_home_page)

    def apply_home_page(self):
        self.stacked_widgets.setCurrentWidget(self.home_page)

    def apply_download_page(self):
        self.stacked_widgets.setCurrentWidget(self.download_page)
    
#    def apply_doc_page(self):
#        self.stacked_widgets.setCurrentWidget(self.doc_page)

    def scroll_to_bottom(self):
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
