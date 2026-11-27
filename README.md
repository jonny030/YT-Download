# YT-Download

把 YouTube 影片下載成 **MP4（影片）** 或 **MP3（音訊）** 的 Python 小工具，以 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 為核心，提供中文互動選單與指令列兩種用法。

## 功能

- 自行選擇輸出格式：MP4 或 MP3（192 kbps）
- MP4 可選畫質：最高畫質、2160p、1440p、1080p、720p、480p、360p
- MP4 優先採用 H.264 + AAC，電腦、手機、車用主機大多能直接播放
- 支援單支影片與整個播放清單
- 檔名自動去除表情符號並限制在 60 個字以內，避免車用音響或舊型播放器讀不到檔案
- 不需另外安裝 ffmpeg（系統沒有時，會改用 `imageio-ffmpeg` 內附的版本）
- 不需登入帳號，也不會讀取瀏覽器資料

## 環境需求

| 項目 | 說明 |
|---|---|
| Python | 3.10 以上 |
| JavaScript 執行環境 | [Node.js](https://nodejs.org/) 或 [Deno](https://deno.com/) 擇一，yt-dlp 解析 YouTube 時需要 |
| ffmpeg | 選用。系統有安裝就用系統的，沒有則用套件內附的版本 |

## 安裝

```bash
git clone https://github.com/jonny030/YT-Download.git
cd YT-Download

python3 -m venv .venv
source .venv/bin/activate        # Windows：.venv\Scripts\activate
pip install -r requirements.txt
```

## 使用方式

### 互動模式

```bash
python yt_downloader.py
```

依畫面提示操作：貼上網址 → 選擇 MP4 或 MP3 → 選擇畫質（僅 MP4）。
下載完成後可以繼續貼下一個網址，直接按 Enter 或輸入 `q` 離開。

```text
=== YouTube 下載器 ===（直接按 Enter 或輸入 q 離開）

請貼上 YouTube 網址：https://www.youtube.com/watch?v=xxxxxxxxxxx

選擇格式：
  1. MP4（影片）
  2. MP3（音訊）
請選擇（預設 1）：
```

### 指令模式

```bash
# 下載成 MP3
python yt_downloader.py "https://www.youtube.com/watch?v=xxxxxxxxxxx" -f mp3

# 下載成 MP4，畫質最高 1080p
python yt_downloader.py "https://www.youtube.com/watch?v=xxxxxxxxxxx" -f mp4 -q 1080

# 下載整個播放清單，存到指定資料夾
python yt_downloader.py "https://www.youtube.com/playlist?list=xxxxxxxx" -f mp3 --playlist -o ~/Music
```

| 參數 | 說明 | 預設值 |
|---|---|---|
| `url` | YouTube 網址，不填則進入互動模式 | — |
| `-f`, `--format` | 輸出格式：`mp4` 或 `mp3` | `mp4` |
| `-q`, `--quality` | MP4 的畫質上限：`best`、`2160`、`1440`、`1080`、`720`、`480`、`360` | `best` |
| `-o`, `--output` | 儲存資料夾 | 程式所在位置的 `downloads/` |
| `--playlist` | 下載整個播放清單（不加則只下載單支影片） | 關閉 |

## 常見問題

### 出現「YouTube 把目前的網路判定為機器人」

YouTube 會擋掉部分 VPN、Proxy 或機房的 IP。請關閉 VPN / Proxy，或換一個網路（例如手機熱點）後再試一次。

### 下載失敗或突然不能用

YouTube 經常改版，請先把 yt-dlp 更新到最新版：

```bash
pip install -U "yt-dlp[default]"
```

### 找不到 JavaScript 執行環境

請安裝 Node.js 或 Deno，並確認在終端機輸入 `node --version` 或 `deno --version` 有顯示版本號。

### 檔案在車上或播放器讀不到

先檢查檔名：過長或含特殊符號的檔名是常見原因。本工具已自動去除表情符號並限制檔名長度，若仍讀不到，可試著把檔名改成簡短的文字。

## 免責聲明

本工具僅供個人學習與合法用途使用。請遵守 [YouTube 服務條款](https://www.youtube.com/t/terms) 及所在地的著作權法規，只下載您擁有權利或已取得授權的內容。使用本工具所產生的任何責任由使用者自行承擔。

## 授權

本專案採用 [MIT License](LICENSE) 授權。
