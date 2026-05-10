import sys
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib3.exceptions import InsecureRequestWarning

# غیرفعال کردن هشدار SSL (اختیاری)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def save_page_html(url, output_dir="outputs"):
    os.makedirs(output_dir, exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, timeout=30, headers=headers, verify=False)
        response.raise_for_status()
        
        parsed = urlparse(url)
        filename = parsed.netloc + parsed.path.replace("/", "_")
        if not filename or filename.endswith("_"):
            filename = "index"
        filename += ".html"
        
        filepath = os.path.join(output_dir, filename)
        
        # ذخیره با encoding خودکار
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(response.text)
            
        print(f"✅ صفحه ذخیره شد: {filepath}")
        return response.text, filepath
    except Exception as e:
        print(f"❌ خطا در دریافت صفحه: {e}")
        return None, None

def extract_download_links(html, base_url, output_dir="outputs"):
    if not html:
        print("❌ HTML وجود ندارد، لینکی استخراج نمی‌شود")
        return set()
        
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    # پسوندهای فایل برای دانلود
    download_patterns = re.compile(r'\.(zip|rar|7z|tar|gz|tgz|bz2|xz|exe|msi|pdf|mp3|mp4|mkv|avi|mov|apk|dmg|iso|bin|sh|deb|rpm)$', re.I)
    keyword_pattern = re.compile(r'download|get-file|file|attachment', re.I)

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue
            
        full_url = urljoin(base_url, href)
        if download_patterns.search(full_url) or keyword_pattern.search(full_url):
            links.add(full_url)

    os.makedirs(output_dir, exist_ok=True)
    links_file = os.path.join(output_dir, "download_links.txt")
    
    with open(links_file, "w", encoding="utf-8") as f:
        for link in sorted(links):
            f.write(link + "\n")

    print(f"✅ {len(links)} لینک دانلود پیدا شد در {links_file}")
    return links

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ استفاده: python fetch_and_extract.py <آدرس_وب‌سایت>")
        sys.exit(1)

    site_url = sys.argv[1]
    print(f"🔍 در حال پردازش: {site_url}")
    
    html_content, saved_page = save_page_html(site_url)
    if not html_content:
        sys.exit(1)
        
    extract_download_links(html_content, site_url)
    print("✅ عملیات با موفقیت پایان یافت.")
