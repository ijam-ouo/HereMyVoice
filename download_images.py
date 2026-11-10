import os
import re
import urllib.request
from urllib.parse import urlparse

# 設定圖片儲存目錄
IMAGE_DIR = "images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# 正則表達式：匹配所有 Squarespace 圖片/CDN URL
# 包含 https://images.squarespace-cdn.com/... 及 https://static1.squarespace.com/... 中的圖片副檔名
url_pattern = re.compile(
    r'https?://(?:images|static1)\.squarespace-cdn\.com/[^\s"\'<>?#]+\.(?:png|jpg|jpeg|gif|webp|svg|ico)',
    re.IGNORECASE
)

# 追蹤下載過的圖片，避免重複下載
downloaded_files = {}

# 取得當前目錄下所有的 HTML 檔案
html_files = [f for f in os.listdir('.') if f.endswith('.html')]

print(f"找到 {len(html_files)} 個 HTML 檔案: {html_files}\n")

for html_file in html_files:
    print(f"正在處理: {html_file}...")
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找出目前 HTML 中所有匹配的圖片 URL
    matches = set(url_pattern.findall(content))
    
    for url in matches:
        if url not in downloaded_files:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # 若檔名衝突或不具體，確保檔名唯一
            local_path = os.path.join(IMAGE_DIR, filename)
            
            print(f"  正在下載: {url}")
            try:
                # 設定 User-Agent 避免被擋
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(req) as response, open(local_path, 'wb') as out_file:
                    out_file.write(response.read())
                
                downloaded_files[url] = f"{IMAGE_DIR}/{filename}"
                print(f"  -> 已儲存至: {local_path}")
            except Exception as e:
                print(f"  [!] 下載失敗 ({url}): {e}")
                continue
        
        # 替換 HTML 內容中的遠端網址為本地路徑
        local_relative_path = downloaded_files[url]
        content = content.replace(url, local_relative_path)

    # 寫回更新後的 HTML 檔案
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)

print("\n所有圖片下載與 HTML 路徑替換完成！")