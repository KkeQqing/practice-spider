# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import shutil
import zipfile
import platform
import subprocess
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def get_chrome_version():
    """自动获取本地 Chrome 浏览器版本"""
    system = platform.system()
    try:
        if system == "Windows":
            # Windows: 从注册表或默认路径读取
            try:
                # 方法1：通过命令行
                result = subprocess.run(
                    ["reg", "query", r"HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon", "/v", "version"],
                    capture_output=True, text=True, check=True
                )
                version = re.search(r"version\s+REG_SZ\s+(.*)", result.stdout)
                if version:
                    return version.group(1).strip()
            except:
                pass

            # 方法2：默认安装路径
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            if not os.path.exists(chrome_path):
                chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            if os.path.exists(chrome_path):
                version = subprocess.check_output([chrome_path, "--version"], text=True)
                return version.strip().split()[-1]

    except Exception as e:
        print(f"⚠️ 获取 Chrome 版本失败: {e}")
        return None

    print("❌ 未找到 Chrome 浏览器，请先安装 Google Chrome。")
    return None


def get_matched_chromedriver_version(chrome_version):
    """根据 Chrome 版本，从淘宝镜像获取匹配的 chromedriver 版本列表"""
    major_version = chrome_version.split('.')[0]
    url = f"https://npmmirror.com/mirrors/chromedriver/LATEST_RELEASE_{major_version}"

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
    except Exception as e:
        print(f"⚠️ 获取 LATEST_RELEASE_{major_version} 失败: {e}")

    # 备用：列出所有版本，找最接近的
    print("🔄 尝试从版本列表匹配...")
    all_versions_url = "https://npmmirror.com/mirrors/chromedriver/"
    try:
        resp = session.get(all_versions_url, timeout=10)
        if resp.status_code == 200:
            # 提取所有版本号（如 126.0.6478.126/）
            versions = re.findall(r'href="(\d+\.\d+\.\d+\.\d+)/"', resp.text)
            # 找主版本匹配的最新版
            matched = [v for v in versions if v.startswith(major_version + ".")]
            if matched:
                return sorted(matched, key=lambda x: [int(i) for i in x.split('.')])[-1]
    except Exception as e:
        print(f"⚠️ 从版本列表匹配失败: {e}")
    return None


def download_chromedriver(driver_version, output_dir):
    """从淘宝镜像下载 chromedriver"""
    system = platform.system()
    if system == "Windows":
        filename = "chromedriver_win32.zip"
    elif system == "Darwin":
        if platform.machine() == "arm64":
            filename = "chromedriver_mac64_m1.zip"
        else:
            filename = "chromedriver_mac64.zip"
    elif system == "Linux":
        filename = "chromedriver_linux64.zip"
    else:
        raise OSError("不支持的操作系统")

    download_url = f"https://npmmirror.com/mirrors/chromedriver/{driver_version}/{filename}"
    output_path = Path(output_dir) / filename
    driver_exe = "chromedriver.exe" if system == "Windows" else "chromedriver"

    # 检查是否已存在
    if (Path(output_dir) / driver_exe).exists():
        print(f"✅ chromedriver 已存在: {output_dir}")
        return str(Path(output_dir) / driver_exe)

    print(f"📥 正在下载: {download_url}")
    try:
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # 解压
        with zipfile.ZipFile(output_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)

        # 删除 zip
        output_path.unlink()

        # macOS/Linux 添加执行权限
        if system != "Windows":
            exe_path = Path(output_dir) / driver_exe
            exe_path.chmod(0o755)

        print(f"✅ 下载并解压成功: {output_dir}")
        return str(Path(output_dir) / driver_exe)

    except Exception as e:
        print(f"❌ 下载失败: {e}")
        raise


def main():
    cache_dir = Path.home() / ".auto_chromedriver"
    cache_dir.mkdir(exist_ok=True)

    # 1. 获取 Chrome 版本
    chrome_ver = get_chrome_version()
    if not chrome_ver:
        sys.exit(1)
    print(f"🔍 检测到 Chrome 版本: {chrome_ver}")

    # 2. 获取匹配的 driver 版本
    driver_ver = get_matched_chromedriver_version(chrome_ver)
    if not driver_ver:
        print("❌ 未找到匹配的 chromedriver 版本")
        sys.exit(1)
    print(f"🎯 匹配的 chromedriver 版本: {driver_ver}")

    # 3. 下载并返回路径
    driver_path = download_chromedriver(driver_ver, cache_dir)
    print(f"📌 chromedriver 路径: {driver_path}")

    return driver_path


if __name__ == "__main__":
    driver_path = main()
    # 你可以在这里直接使用 driver_path 启动 Selenium
    # 示例：
    # from selenium import webdriver
    # from selenium.webdriver.chrome.service import Service
    # service = Service(driver_path)
    # driver = webdriver.Chrome(service=service)