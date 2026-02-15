# plugins/ghost_dl_plugin.py
import os
import re
import threading

try:
    import yt_dlp
    PLUGIN_ACTIVE = True
except ImportError:
    PLUGIN_ACTIVE = False

class GhostDownloader:
    def __init__(self):
        self.is_downloading = False

    def is_active(self):
        return PLUGIN_ACTIVE

    def start_download(self, url, output_folder, progress_callback, finish_callback, error_callback):
        if not self.is_active():
            error_callback("yt-dlp kütüphanesi eksik!")
            return

        self.is_downloading = True
        threading.Thread(target=self._download_thread, args=(url, output_folder, progress_callback, finish_callback, error_callback), daemon=True).start()

    def _download_thread(self, url, output_folder, progress_callback, finish_callback, error_callback):
        def hook(d):
            if d['status'] == 'downloading':
                try:
                    p_raw = d.get('_percent_str', '0%')
                    p_clean = re.sub(r'\x1b\[[0-9;]*m', '', p_raw).strip()
                    val = float(p_clean.replace('%', '')) / 100
                    progress_callback(val, p_clean)
                except: pass
            elif d['status'] == 'finished':
                progress_callback(1.0, "Dönüştürülüyor...")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'progress_hooks': [hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'nocheckcertificate': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.is_downloading = False
            finish_callback()
        except Exception as e:
            self.is_downloading = False
            error_callback(str(e))