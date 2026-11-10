import os
import glob
import requests
from bs4 import BeautifulSoup

# ==================== 設定區 ====================
# HTML 檔案所在的根目錄（預設為當前資料夾，會自動搜尋所有子資料夾）
HTML_DIR = "./" 
# 輸出的清單檔名
OUTPUT_TXT = "css_sources.txt"
# 輸出的合併 CSS 檔名
OUTPUT_CSS = "bundle.css"
# ===============================================

def extract_css_from_html(file_path):
    """讀取單個 HTML 檔案並提取所有 CSS 網址"""
    css_urls = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            # 尋找所有帶有 rel 屬性的 link 標籤
            for link in soup.find_all('link', rel=True):
                rel = link.get('rel')
                # 兼容 rel 是字串或列表的情況
                if isinstance(rel, list):
                    is_stylesheet = 'stylesheet' in [r.lower() for r in rel]
                else:
                    is_stylesheet = 'stylesheet' in rel.lower()
                
                if is_stylesheet:
                    href = link.get('href')
                    if href:
                        css_urls.append(href)
    except Exception as e:
        print(f"讀取檔案失敗 {file_path}: {e}")
    return css_urls

def main():
    # 1. 尋找所有 HTML 檔案（包含子資料夾）
    html_files = glob.glob(os.path.join(HTML_DIR, '**', '*.html'), recursive=True)
    print(f"【掃描結果】共找到了 {len(html_files)} 個 HTML 檔案。")

    unique_css_urls = set()

    # 2. 提取與去重
    for html_path in html_files:
        urls = extract_css_from_html(html_path)
        for url in urls:
            # 處理協定相對網址 (Protocol-relative URLs) 例如：//static1.squarespace.com/...
            if url.startswith('//'):
                url = 'https:' + url
            unique_css_urls.add(url)

    # 3. 輸出 css_sources.txt 文字檔
    sorted_urls = sorted(list(unique_css_urls))
    with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
        for url in sorted_urls:
            f.write(url + '\n')
            
    print(f"【清單輸出】已成功輸出不重複的 CSS 網址清單至: {OUTPUT_TXT}")
    print(f"【統計數據】總共找到 {len(sorted_urls)} 個獨特的 CSS 網址。\n")

    # 4. 自動下載並合併 CSS 內容到 bundle.css
    print("【下載中】開始下載並合併所有 CSS 檔案...")
    merged_css_content = []
    
    for url in sorted_urls:
        try:
            # 確保是完整的網址才進行下載
            if not url.startswith('http://') and not url.startswith('https://'):
                print(f"-> 跳過非完整 URL: {url}")
                continue
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # 加上來源註解，方便日後維護與除錯
                header_comment = f"\n\n/* ==========================================\n   Source: {url}\n   ========================================== */\n\n"
                merged_css_content.append(header_comment + response.text)
                print(f"-> 成功下載: {url}")
            else:
                print(f"-> 下載失敗 (Status {response.status_code}): {url}")
        except Exception as e:
            print(f"-> 下載錯誤 {url}: {e}")

    # 寫入合併後的 CSS 檔案
    with open(OUTPUT_CSS, 'w', encoding='utf-8') as f:
        f.write(''.join(merged_css_content))
        
    print(f"\n【完成】所有 CSS 已成功合併並儲存至: {OUTPUT_CSS}！")

if __name__ == "__main__":
    main()