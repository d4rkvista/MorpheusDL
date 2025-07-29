import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal, QObject, QThread
from Downloader import Download


class testing(QMainWindow):
    def __init__(self):
        super().__init__()
        self.url_or_query = input("Enter a YouTube URL or search query: ")
        self.start_fetch_thread()

    def cleanup_thread(self):
        print("stopping thread")
        self.thread.quit()
        self.thread.wait()
        self.fetch_info.deleteLater()
        self.thread.deleteLater()
        print("thread stopped")
        return

    def start_fetch_thread(self):
        self.thread = QThread()
        self.fetch_info = Download(self.url_or_query)
        self.fetch_info.moveToThread(self.thread)

        self.thread.started.connect(self.fetch_info.fetch_info)
        print("thread started")

        self.fetch_info.return_fetch_info.connect(self.receive_info)
        self.fetch_info.return_fetch_info_error.connect(self.receive_info)

        self.thread.start()


    def receive_info(self, info):
        print("recieve info started")
        self.info = info



#    downloader = Download(url_or_query)
#    downloader.fetch_info()

        if info and not isinstance(info, str):
            if isinstance(info, list):  # multiple results (playlist or search)
                for i, video in enumerate(info, start=1):
                    print(f"\nResult #{i}")
                    print("ID:", video.get("id"))
                    print("Title:", video.get("title"))
                    print("Uploader:", video.get("uploader"))
                    print("Duration:", video.get("duration"))
                    print("Duration_str:", video.get("duration_str"))
                    print("Thumbnail URL:", video.get("thumbnail"))
                    print("Webpage URL:", video.get("url"))
            else:  # single video
                print("ID:", info.get("id"))
                print("Title:", info.get("title"))
                print("Uploader:", info.get("uploader"))
                print("Duration:", info.get("duration"))
                print("Duration_str:", info.get("duration_str"))
                print("Thumbnail URL:", info.get("thumbnail"))
                print("Webpage URL:", info.get("url"))
        else:
            if info:
                print(info)
            else: 
                print("unknown exception")
        
        self.cleanup_thread()
        print("recieve info ended")


    def download(self):
        entries = self.info

        if isinstance(entries, list):
            Download.download_all(entries, audio_only=True)
        else:
            Download.download_video(entries)
    


def main():
    app = QApplication(sys.argv)
    window = testing()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
