import sys
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

def save_page_html(url, output_dir="outputs"):
    """دریافت صفحه و ذخیره HTML آن"""
    os.makedirs(output_dir, exist_ok=True)
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        # استخراج نام فایل از آدرس یا استفاده از زمان
        parsed = urlparse(url)
        filename = parsed.netloc + parsed.path.replace("/", "_")
        if not filename or filename.endswith("_"):
            filename = "index"
        filename += ".html"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"✅ صفحه ذخیره شد: {filepath}")
        return response.text, filepath
    except Exception as e:
        print(f"❌ خطا در دریافت صفحه: {e}")
        sys.exit(1)

def extract_download_links(html, base_url, output_dir="outputs"):
    """استخراج لینک‌های دانلود از صفحه و ذخیره در فایل متنی"""
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    # الگوهای معمول لینک دانلود (می‌توانید گسترش دهید)
    download_patterns = re.compile(r'\.(zip|rar|7z|tar|gz|exe|msi|pdf|mp3|mp4|mkv|apk|dmg|iso)$', re.I)
    keyword_pattern = re.compile(r'download|get|file', re.I)

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        full_url = urljoin(base_url, href)
        # بررسی پسوند فایل یا کلمات کلیدی در آدرس
        if download_patterns.search(full_url) or keyword_pattern.search(full_url):
            links.add(full_url)

    # ذخیره لینک‌ها در فایل متنی
    os.makedirs(output_dir, exist_ok=True)
    links_file = os.path.join(output_dir, "download_links.txt")
    with open(links_file, "w", encoding="utf-8") as f:
        for link in sorted(links):
            f.write(link + "\n")

    print(f"✅ تعداد {len(links)} لینک دانلود پیدا شد و در {links_file} ذخیره گردید.")
    return links

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("استفاده: python fetch_and_extract.py <آدرس_وب‌سایت>")
        sys.exit(1)

    site_url = sys.argv[1]
    html_content, saved_page = save_page_html(site_url)
    extract_download_links(html_content, site_url)
