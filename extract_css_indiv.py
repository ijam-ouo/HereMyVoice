import os
from bs4 import BeautifulSoup
import requests

def generate_page_specific_css():
    # 建立 style 資料夾（如果不存在的話）
    style_dir = 'style'
    os.makedirs(style_dir, exist_ok=True)
    
    # 掃描當前資料夾下的所有 html 檔案
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    
    for filename in html_files:
        print(f"正在處理: {filename}...")
        with open(filename, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        css_links = []
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href and (href.startswith('http') or href.startswith('//')):
                if href.startswith('//'):
                    href = 'https:' + href
                css_links.append((link, href))
        
        if not css_links:
            print(f" -> {filename} 沒有找到遠端 CSS 連結，跳過。")
            continue
        
        merged_css = []
        for link_tag, href in css_links:
            try:
                res = requests.get(href, timeout=10)
                if res.status_code == 200:
                    merged_css.append(f"/* Source: {href} */\n" + res.text)
            except Exception as e:
                print(f"警告：無法下載 {href}: {e}")
        
        base_name = os.path.splitext(filename)[0]
        # 儲存到 style 資料夾內
        css_filename = os.path.join(style_dir, f"{base_name}.css")
        
        with open(css_filename, 'w', encoding='utf-8') as css_file:
            css_file.write('\n\n'.join(merged_css))
        
        # 修改 HTML：將路徑指向 style/檔名.css
        first = True
        for link_tag, href in css_links:
            if first:
                link_tag.attrs.clear()
                link_tag['rel'] = 'stylesheet'
                link_tag['href'] = f"style/{base_name}.css"
                first = False
            else:
                link_tag.decompose()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
        print(f" -> 成功產生 {css_filename} 並已更新 {filename}")

if __name__ == '__main__':
    generate_page_specific_css()