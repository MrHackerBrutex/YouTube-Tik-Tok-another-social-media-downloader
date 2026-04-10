
from flask import Flask, request, render_template_string
import os
import yt_dlp
import threading

app = Flask(__name__)
DOWNLOAD_FOLDER = '/storage/emulated/0/SocialDownloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Social Media Downloader</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; background: #f0f0f0; margin: 0; padding: 20px; }
        .container { max-width: 700px; margin: auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #333; }
        input[type=text] { width: 100%; padding: 12px; margin: 10px 0; font-size: 16px; border: 1px solid #ccc; border-radius: 6px; }
        select, button { width: 100%; padding: 12px; margin: 10px 0; font-size: 16px; border-radius: 6px; }
        button { background: #007bff; color: white; border: none; cursor: pointer; font-weight: bold; }
        button:hover { background: #0056b3; }
        .status { margin-top: 20px; padding: 15px; background: #d4edda; color: #155724; border-radius: 6px; }
    </style>
</head>
<body>
<div class="container">
    <h1>📥 Social Media Downloader</h1>
    <p style="text-align:center;">YouTube • Instagram • TikTok • Facebook + more</p>
    
    <form method="POST">
        <label><strong>Paste Link:</strong></label><br>
        <input type="text" name="url" placeholder="https://www.instagram.com/reel/..." required><br>
        
        <label><strong>Download Type:</strong></label>
        <select name="type">
            <option value="video">Video (MP4)</option>
            <option value="audio">Audio Only (MP3)</option>
            <option value="image">Image(s) / Photos</option>
        </select>
        
        <label><strong>Quality (for Video only):</strong></label>
        <select name="quality">
            <option value="1080">1080p</option>
            <option value="720">720p</option>
            <option value="480">480p</option>
            <option value="best">Best Available</option>
        </select>
        
        <button type="submit">🚀 Start Download</button>
    </form>
    
    {% if message %}<div class="status">{{ message | safe }}</div>{% endif %}
    
    <p style="text-align:center; margin-top:30px; font-size:14px;">
        All files saved in: <strong>SocialDownloads</strong> folder (main storage)
    </p>
</div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        dtype = request.form.get('type', 'video')
        quality = request.form.get('quality', '1080')

        if not url.startswith('http'):
            message = "❌ Please paste a valid link!"
            return render_template_string(HTML, message=message)

        def download_thread():
            try:
                if dtype == 'audio':
                    opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title).150s.%(ext)s',
                        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
                        'restrictfilenames': True,
                    }
                elif dtype == 'image':
                    # For images / photos / carousels
                    opts = {
                        'format': 'best',
                        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title).150s.%(ext)s',
                        'restrictfilenames': True,
                        'writethumbnail': True,      # Download thumbnail if available
                        'write_all_thumbnails': True,
                    }
                else:  # video
                    if quality == 'best':
                        fmt = 'bestvideo+bestaudio/best'
                    else:
                        fmt = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]'
                    opts = {
                        'format': fmt,
                        'merge_output_format': 'mp4',
                        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title).150s [%(height)sp].%(ext)s',
                        'restrictfilenames': True,
                    }

                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                print(f"✅ Downloaded {dtype}: {url}")
            except Exception as e:
                print(f"❌ Error: {e}")

        threading.Thread(target=download_thread, daemon=True).start()
        message = f"✅ Download started for <strong>{url}</strong><br>Type: {dtype} | Check <b>SocialDownloads</b> folder."

    return render_template_string(HTML, message=message)

if __name__ == '__main__':
    print("\n🚀 Social Media Downloader is starting...")
    print(f"📁 Downloads saved in: {DOWNLOAD_FOLDER}")
    print("\nOpen in browser → http://127.0.0.1:5040")
    print("Keep this Termux window open!\n")
    app.run(host='0.0.0.0', port=5040)
EOF
