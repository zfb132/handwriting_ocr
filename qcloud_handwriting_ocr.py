#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: 'zfb'
# time: 2022-04-29 17:22

import os
import re
import requests

import config

from datetime import datetime
from json import loads, dump, dumps
from pathlib import Path
from shutil import rmtree

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ocr.v20181119 import ocr_client, models
from get_images import get_base64_image, get_images_from_dir, get_images_from_pdf, get_asset_from_url


# https://stackoverflow.com/questions/12492810
os.system("color")
COLOR = config.COLOR

def get_OCR_client(id, key):
    try:
        cred = credential.Credential(id, key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "ocr.tencentcloudapi.com"
    
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = ocr_client.OcrClient(cred, "ap-shanghai", clientProfile)
    except TencentCloudSDKException as err:
        print(err)
        exit(-1)
    return client

def run_ocr_single_image_use_auto(client, image_name="", url=""):
    '''
    单张图片的OCR，如果是远程链接，则使用ImageUrl，否则使用ImageBase64

    :param image_name: 本地图片的名称，base64编码后大小不能超过7M
    :param url: 远程图片的链接（PNG、JPG、JPEG），base64编码后大小不能超过7M，下载时间不能超过3秒
    '''
    try:
        req = models.GeneralHandwritingOCRRequest()
        params = {
            "EnableWordPolygon": False,
            "EnableDetectText": True
        }
        if config.ONLY_HW:
            params["Scene"] = "only_hw"
        # 图片的 ImageUrl、ImageBase64 必须提供一个，如果都提供，只使用 ImageUrl
        if url:
            # 图片下载时间不能超过 3 秒
            params["ImageUrl"] = url
            # 获取文件名
            str_time = datetime.now().strftime("%Y%m%d%H%M%S.%f")
            default_name = url.split("/")[-1].split("?")[0] or f"image_{str_time}.jpg"
            response = requests.get(url, stream=True)
            filename = response.headers.get("Content-Disposition", f"filename={default_name}")
            filename = re.findall("filename=\"(.+)\"", filename)[0] or re.findall("filename=(.+)", filename)[0]
            image_name = Path(f"{config.TEMP_FILES_DIR}/{filename}").resolve()
            print(COLOR["GREEN"], f"使用 {url} 进行OCR！", COLOR["END"])
        else:
            # 经Base64编码后不能超过 7M
            params["ImageBase64"] = get_base64_image(image_name)
            print(COLOR["GREEN"], f"使用 {image_name} 进行OCR！", COLOR["END"])
            
        req.from_json_string(dumps(params))
        resp = client.GeneralHandwritingOCR(req)
        json_name = Path(f"{config.TEMP_FILES_DIR}/{image_name.name}.json").resolve()
        with open(json_name, "w", encoding="utf8") as f:
            dump(resp.to_json_string(), f, ensure_ascii=False)
        print(COLOR["GREEN"], f"OCR成功，识别结果保存位置： {json_name}", COLOR["END"])
    except TencentCloudSDKException as err:
        print(err)
        print(COLOR["RED"], f"OCR失败： {json_name}", COLOR["END"])
    # string to json
    result = loads(resp.to_json_string())
    return result["TextDetections"]

def run_ocr_ready(client, image_name="", url=""):
    # true：把远程链接下载到本地，再base64编码
    # false：直接使用远程链接
    use_local_image = True
    detected_text = []
    if url:
        if use_local_image:
            image_name = get_asset_from_url(url)
            if image_name.suffix.lower() == ".pdf":
                pdf_images = get_images_from_pdf(image_name)
                for _image in pdf_images:
                    detected_text += run_ocr_single_image_use_auto(client, _image)
            else:
                detected_text = run_ocr_single_image_use_auto(client, image_name)
        else:
            detected_text = run_ocr_single_image_use_auto(client, url)
    else:
        detected_text =run_ocr_single_image_use_auto(client, image_name, url)
    # 保存文件
    txt_name = Path(f"{config.OCR_RESULTS_DIR}/{image_name.name}.txt").resolve()
    with open(txt_name, "w", encoding="utf8") as f:
        for line_text in detected_text:
            f.write(line_text["DetectedText"] + config.LINE_SEPERATOR)
        # f.write(f'{config.LINE_SEPERATOR}'.join(json.dumps(detected_text, ensure_ascii=False)))
    return detected_text

def merge_in_single_image(text_detections):
    text = []
    for i in text_detections:
        text.append(i["DetectedText"])
    ocr_text = f'{config.LINE_SEPERATOR}'.join(text)
    return ocr_text

def run_ocr(files, dirs, urls):
    client = get_OCR_client(config.SECRETID, config.SECRETKEY)
    for image in files:
        print(f"开始处理： {image}")
        if image.suffix.lower() == ".pdf":
            pdf_images = get_images_from_pdf(image)
            for _image in pdf_images:
                run_ocr_ready(client, _image)
        else:
            run_ocr_ready(client, image)
        print(f"完成处理： {image}")
    for dir in dirs:
        images = get_images_from_dir(dir)
        for image in images:
            print(f"开始处理： {image}")
            if image.suffix.lower() == ".pdf":
                pdf_images = get_images_from_pdf(image)
                for _image in pdf_images:
                    run_ocr_ready(client, _image)
            else:
                run_ocr_ready(client, image)
            print(f"完成处理： {image}")
    for url in urls:
        run_ocr_ready(client, url=url)


def main():
    ocr_files = config.OCR_FILES
    files = []
    dirs = []
    urls = []
    # 清空临时文件的目录
    if os.path.exists(config.TEMP_FILES_DIR):
        rmtree(config.TEMP_FILES_DIR)
    os.makedirs(config.TEMP_FILES_DIR, exist_ok=True)
    if not os.path.exists(config.OCR_RESULTS_DIR):
        os.makedirs(config.OCR_RESULTS_DIR)
    for image in ocr_files:
        if os.path.isfile(image):
            files.append(Path(image).resolve())
        elif os.path.isdir(image):
            dirs.append(Path(image).resolve())
        else:
            urls.append(image)
    run_ocr(files, dirs, urls)


if __name__ == "__main__":
    main()