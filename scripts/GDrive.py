import requests
import argparse
import os
import sys
from tqdm import tqdm
import json

def download_file_from_google_drive(file_id, destination, chunk_size=32768):
    """دانلود فایل از گوگل درایو با نمایش پیشرفت"""
    
    URL = "https://docs.google.com/uc?export=download"
    
    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)
    
    # تشخیص نیاز به تایید امنیتی
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            params = {'id': file_id, 'confirm': value}
            response = session.get(URL, params=params, stream=True)
            break
    
    # دریافت حجم فایل
    total_size = int(response.headers.get('content-length', 0))
    
    # دانلود با نمایش نوار پیشرفت
    with open(destination, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=destination) as pbar:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
    
    return total_size

def download_folder(file_id, destination):
    """دانلود پوشه از گوگل درایو"""
    import io
    import zipfile
    
    URL = "https://drive.google.com/drive/folders/" + file_id
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    session = requests.Session()
    response = session.get(download_url, stream=True)
    
    # اگر فایل فشرده است
    if 'zip' in response.headers.get('content-type', ''):
        zip_content = io.BytesIO()
        total_size = int(response.headers.get('content-length', 0))
        
        with tqdm(total=total_size, unit='B', unit_scale=True, desc="دانلود پوشه") as pbar:
            for chunk in response.iter_content(chunk_size=32768):
                if chunk:
                    zip_content.write(chunk)
                    pbar.update(len(chunk))
        
        # استخراج فایل زیپ
        with zipfile.ZipFile(zip_content, 'r') as zip_ref:
            zip_ref.extractall(destination)
        print(f"پوشه با موفقیت در {destination} استخراج شد")
    else:
        download_file_from_google_drive(file_id, destination)

def list_files_in_folder(folder_id):
    """لیست فایل‌های داخل پوشه (نیاز به API کلید)"""
    print("برای لیست کردن فایل‌های پوشه به Google Drive API نیاز است")
    print(f"شناسه پوشه: {folder_id}")
    return []

def main():
    parser = argparse.ArgumentParser(description='دانلود از گوگل درایو')
    parser.add_argument('file_id', help='شناسه فایل یا پوشه در گوگل درایو')
    parser.add_argument('-o', '--output', default='.', help='مسیر ذخیره فایل')
    parser.add_argument('-f', '--filename', help='نام فایل خروجی')
    parser.add_argument('--folder', action='store_true', help='دانلود پوشه')
    parser.add_argument('--chunk-size', type=int, default=32768, help='سایز بافر دانلود')
    
    args = parser.parse_args()
    
    # ایجاد مسیر خروجی
    os.makedirs(args.output, exist_ok=True)
    
    # تعیین نام فایل
    if not args.filename:
        args.filename = f"downloaded_{args.file_id}"
        if not args.folder:
            args.filename += ".file"
    
    destination = os.path.join(args.output, args.filename)
    
    try:
        if args.folder:
            download_folder(args.file_id, args.output)
        else:
            size = download_file_from_google_drive(args.file_id, destination, args.chunk_size)
            print(f"\n✅ دانلود کامل شد: {destination}")
            print(f"📊 حجم: {size / (1024*1024):.2f} MB")
            
    except Exception as e:
        print(f"❌ خطا در دانلود: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
