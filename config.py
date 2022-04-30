#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: 'zfb'
# time: 2022-04-29 17:44

# 腾讯云：https://console.cloud.tencent.com/cam/capi
# 腾讯云通用手写体识别，每月免费额度1000次，接口请求频率限制：10次/秒
SECRETID = "AKeee5555512345677777123456788889876"
SECRETKEY = "A71234567890abcdefedcba098765432"

# 待识别文件的本地位置/远程链接：一个或多个
# 支持常见的图片文件格式（如jpg、png等，暂不支持GIF）和PDF文件
# https://cloud.tencent.com/document/api/866/36212
# 每个图片经Base64编码后不超过 7M
# （1）本地位置支持绝对和相对两种
# （2）本地位置包括：本地路径、本地文件名
# （3）本地路径：程序会自动尝试读取该路径下除GIF格式外的所有图片文件（自动递归遍历子文件夹）
# （4）远程链接支持http://、https:// 等协议
# （5）本地路径和远程连接都支持PDF文件
OCR_FILES = [
    "01.jpg",
    r"C:\Users\zfb\Desktop\handwriting-images",
    "https://data.example.com/%E6%89%8B%E5%86%99%E4%BD%93%E8%AF%86%E5%88%AB.pdf",
    "https://coding-pages-bucket-111111.cos.ap-shanghai.myqcloud.com/web-01.jpg"
]

# 行连接符：指定原始手写文本的每一行与下一行之间的连接符，默认为""
LINE_SEPERATOR = ""

# 是否识别印刷体
# only_hw 表示只输出手写体识别结果，过滤印刷体
ONLY_HW = True

# 保存结果的文件夹
# OCR的结果文件命名格式与原始文件相同，例如：1.png -> 1.png.txt
# 支持绝对路径和相对路径
OCR_RESULTS_DIR = "./results"

# 保存中间的过程文件
# 原始识别到的json文件、pdf的每一页图片（如果是pdf的话）、从链接下载到的文件
# 支持绝对路径和相对路径
TEMP_FILES_DIR = "./temp"

# 为终端输出添加色彩：不可删除
COLOR = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "YELLOW": "\033[93m",
    "END": "\033[0m",
}