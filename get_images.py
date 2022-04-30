#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: 'zfb'
# time: 2022-04-29 18:12

import re
import requests

import fitz

from base64 import b64encode
from datetime import datetime
from pathlib import Path
from sys import getsizeof
from urllib.parse import unquote

from config import COLOR, TEMP_FILES_DIR


def get_images_from_dir(path):
    """
    获取指定目录下的所有图片(jpg,png,jpeg,tif,tiff,bmp)，递归子文件夹
    """
    path = Path(path)
    files = list(path.glob("**/*"))
    images = [x for x in files if x.suffix.lower() in [".jpg", ".png", ".jpeg", ".tif", ".tiff", ".bmp", "pdf"]]
    return images

def get_asset_from_url(url):
    """
    从url下载内容到本地
    """
    images = []
    try:
        str_time = datetime.now().strftime("%Y%m%d%H%M%S.%f")
        default_name = url.split("/")[-1].split("?")[0]
        # url解码（解决中文乱码问题）
        default_name = unquote(default_name)
        response = requests.get(url, stream=True)
        filename = response.headers.get("Content-Disposition", f"filename={default_name}")
        filename = re.findall("filename=\"(.+)\"", filename) or re.findall("filename=(.+)", filename)
        filename = Path(f"{TEMP_FILES_DIR}/{filename[0]}").resolve()
        with open(filename, "wb") as image:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    image.write(chunk)
        images.append(filename)
        print(f"下载 {url} 成功")
    except Exception as e:
        print(e)
        print(COLOR["RED"], f"下载 {url} 失败！", COLOR["END"])
    return images[0]

def split_pdf(pdf_name):
    """
    将pdf文件分割成单个页面大小的图片
    """
    images = []
    try:
        doc = fitz.open(pdf_name)
        pure_name = pdf_name.stem
        for i in range(doc.page_count):
            page = doc.load_page(i)
            pix = page.get_pixmap()
            img_name = Path(f"{TEMP_FILES_DIR}/{pure_name}_{i}.png").resolve()
            pix.save(img_name)
            images.append(img_name)
            print(f"PDF文件 {pdf_name} 第{i+1}页导出图片成功")
    except Exception as e:
        print(e)
        print(COLOR["RED"], f"PDF文件 {pdf_name} 按页导出图片失败！", COLOR["END"])
    return images

def get_images_from_pdf(pdf_name):
    '''
    从pdf文件中获取图片
    '''
    return split_pdf(pdf_name)

def get_base64_image(image_name):
    """
    将图片转换成base64编码
    """
    with open(image_name, "rb") as f:
        image = b64encode(f.read())
    # 单位是字节，需要转换成MBytes
    image_size = round(getsizeof(image) / 1024 / 1024, 2)
    if image_size > 7:
        print(COLOR["YELLOW"], f"图片BASE64编码后 {image_name} 大小超过7M，无法识别！", COLOR["END"])
    # 把字节转换成utf8编码，否则无法json序列化
    image = image.decode("utf8")
    return image