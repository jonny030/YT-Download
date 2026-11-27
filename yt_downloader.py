#!/usr/bin/env python3
"""YouTube 下載器：可選擇下載成 MP4（影片）或 MP3（音訊）。

用法：
    互動模式：  python yt_downloader.py
    指令模式：  python yt_downloader.py <網址> --format mp3
"""

import argparse
import shutil
import sys
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    sys.exit("找不到 yt-dlp，請先執行：pip install -r requirements.txt")

DEFAULT_DIR = Path(__file__).resolve().parent / "downloads"
QUALITIES = ["best", "2160", "1440", "1080", "720", "480", "360"]
# 表情符號等特殊字元：車用音響、舊型播放器常因檔名含這些字元而讀不到檔案
EMOJI = "[\U00010000-\U0010FFFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D]"


def find_ffmpeg():
    """優先使用系統的 ffmpeg，沒有的話改用 imageio-ffmpeg 內附的版本。"""
    path = shutil.which("ffmpeg")
    if path:
        return path
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


class QuietLogger:
    """不顯示 yt-dlp 的原始訊息，錯誤由 download() 統一用中文回報。"""

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


def progress_hook(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "").strip()
        speed = d.get("_speed_str", "").strip()
        eta = d.get("_eta_str", "").strip()
        print(f"\r下載中 {percent}  速度 {speed}  剩餘 {eta}   ", end="", flush=True)
    elif d["status"] == "finished":
        print("\n下載完成，正在轉檔 / 合併…")


def build_options(fmt, quality, out_dir, playlist, ffmpeg):
    opts = {
        # YouTube 需要 JavaScript 執行環境來解析影片，有裝 deno 或 node 都可以
        "js_runtimes": {"deno": {}, "node": {}},
        "outtmpl": str(out_dir / "%(title).60s.%(ext)s"),  # 檔名最多 60 個字
        "noplaylist": not playlist,
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
        "logger": QuietLogger(),
        "ffmpeg_location": ffmpeg,
    }

    if fmt == "mp3":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    else:
        limit = "" if quality == "best" else f"[height<={quality}]"
        # 優先挑 H.264 + AAC，這樣 QuickTime / 手機都能直接播放
        opts["format"] = (
            f"bestvideo{limit}[vcodec^=avc1]+bestaudio[ext=m4a]/"
            f"bestvideo{limit}+bestaudio/"
            f"best{limit}/best"
        )
        opts["merge_output_format"] = "mp4"
        # 來源若不是 mp4（例如 webm），就轉成 mp4；已經是 mp4 則不會重複處理
        opts["postprocessors"] = [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}]

    # 下載前先把標題裡的表情符號拿掉，並整理多餘的空白
    replace = yt_dlp.postprocessor.MetadataParserPP.Actions.REPLACE
    opts["postprocessors"].insert(
        0,
        {
            "key": "MetadataParser",
            "when": "pre_process",
            "actions": [(replace, "title", EMOJI, ""), (replace, "title", r"\s+", " ")],
        },
    )

    return opts


def download(url, fmt="mp4", quality="best", out_dir=DEFAULT_DIR, playlist=False):
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        print("錯誤：找不到 ffmpeg。請執行 pip install imageio-ffmpeg 或 brew install ffmpeg")
        return False

    out_dir = Path(out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        with yt_dlp.YoutubeDL(build_options(fmt, quality, out_dir, playlist, ffmpeg)) as ydl:
            info = ydl.extract_info(url, download=True)
    except yt_dlp.utils.DownloadError as e:
        if "Sign in to confirm" in str(e):
            print("\n下載失敗：YouTube 把目前的網路判定為機器人，拒絕提供影片。")
            print("請關閉 VPN / Proxy 或換一個網路（例如手機熱點）後再試一次。")
            return False
        print(f"\n下載失敗：{e}")
        return False

    title = info.get("title", "") if info else ""
    print(f"完成：{title}\n儲存位置：{out_dir}")
    return True


def ask(prompt, choices, default):
    """顯示選單並回傳使用者選的項目。"""
    for i, (_, label) in enumerate(choices, 1):
        print(f"  {i}. {label}")
    while True:
        answer = input(f"{prompt}（預設 {default}）：").strip() or str(default)
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            return choices[int(answer) - 1][0]
        print("請輸入選單上的數字。")


def interactive():
    print("=== YouTube 下載器 ===（直接按 Enter 或輸入 q 離開）")
    while True:
        url = input("\n請貼上 YouTube 網址：").strip()
        if not url or url.lower() == "q":
            break

        print("\n選擇格式：")
        fmt = ask("請選擇", [("mp4", "MP4（影片）"), ("mp3", "MP3（音訊）")], 1)

        quality = "best"
        if fmt == "mp4":
            print("\n選擇畫質：")
            labels = [(q, "最高畫質" if q == "best" else f"{q}p") for q in QUALITIES]
            quality = ask("請選擇", labels, 1)

        playlist = False
        if "list=" in url:
            playlist = input("\n這是播放清單連結，要下載整個清單嗎？(y/N)：").strip().lower() == "y"

        print()
        download(url, fmt, quality, DEFAULT_DIR, playlist)


def main():
    parser = argparse.ArgumentParser(description="下載 YouTube 影片為 MP4 或 MP3")
    parser.add_argument("url", nargs="?", help="YouTube 網址（不填則進入互動模式）")
    parser.add_argument("-f", "--format", choices=["mp4", "mp3"], default="mp4", help="輸出格式（預設 mp4）")
    parser.add_argument("-q", "--quality", choices=QUALITIES, default="best", help="MP4 最高畫質（預設 best）")
    parser.add_argument("-o", "--output", default=str(DEFAULT_DIR), help="儲存資料夾")
    parser.add_argument("--playlist", action="store_true", help="下載整個播放清單")
    args = parser.parse_args()

    try:
        if args.url:
            ok = download(args.url, args.format, args.quality, args.output, args.playlist)
            sys.exit(0 if ok else 1)
        interactive()
    except (KeyboardInterrupt, EOFError):
        print("\n已取消。")


if __name__ == "__main__":
    main()
