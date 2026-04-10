

# YouTube-Tik-Tok-another-social-media-downloader
This package required for YouTube Tiktok and other social media downloader 
# 2. Create the main app.py (improved version)
cat > app.py << 'EOF'
from flask import Flask, render_template, request, send_file
import os
import requests
from bs4 import BeautifulSoup
import re
import time

app = Flask(__name__, template_folder='templates')

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if not url or 'youtube.com/post/' not in url:
            return "<h2>❌ Please paste a valid YouTube Community Post URL</h2>", 400

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            r = requests.get(url, headers=headers, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')

            # Find images (YouTube community posts often use specific patterns)
            images = []
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src') or img.get('data-original')
                if src and any(x in src.lower() for x in ['.jpg', '.jpeg', '.png', '.webp', 'ytimg']):
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif not src.startswith('http'):
                        src = 'https://www.youtube.com' + src
                    # Try to get highest resolution
                    src = re.sub(r'=[whs]\d+.*', '=w2048-h2048', src)
                    if src not in images:
                        images.append(src)

            if not images:
                return "<h2>⚠️ No images found. Open the post in Chrome and try again.</h2>", 400

            # Download images
            downloaded = []
            for i, img_url in enumerate(images[:20]):   # limit to 20 images
                try:
                    img_data = requests.get(img_url, headers=headers, timeout=15).content
                    filename = f"post_image_{int(time.time())}_{i+1:03d}.jpg"
                    with open(os.path.join(DOWNLOAD_FOLDER, filename), 'wb') as f:
                        f.write(img_data)
                    downloaded.append(filename)
                except:
                    pass

            if downloaded:
                return render_template('result.html', files=downloaded, count=len(downloaded))
            else:
                return "<h2>❌ Could not download images. Check your internet.</h2>", 400

        except Exception as e:
            return f"<h2>❌ Error: {str(e)}</h2><p>Make sure you have internet and the link is correct.</p>", 500

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    print("\n🚀 Server Started Successfully!")
    print("Open in your phone browser:")
    print("   http://127.0.0.1:5000")
    print("   or http://localhost:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF
