# 基于腾讯云API的通用手写字体识别软件
## 配置环境和运行
```bash
# 在腾讯云控制台开通OCR功能，每月有免费额度
# https://console.cloud.tencent.com/ocr/

# 安装依赖（以下命令都在当前目录执行）
# 推荐在自己新建的python虚拟环境里执行
pip install -r requirements.txt

# 修改配置文件
# 至少需要修改SECRETID和SECRETKEY

python qcloud_handwriting_ocr.py
```

## 手写图片的信息
* 手写扫描图片或PDF推荐使用`扫描全能王CamScanner`生成，可以很大程度保证手写图片质量
* 支持常用图片格式，`*.jpg`、`*.png`、`*.jpeg`等
* 支持PDF格式（软件自动将PDF每一页导出为图片）
* 支持本地手写图片文件名，例如`r"C:\Users\zfb\Desktop\handwriting-images\1.jpg"`、`"2.pdf"`
* 支持本地手写图片文件夹名称，例如`r"C:\Users\zfb\Desktop\handwriting-images"`、`r"C:/Users/zfb/Desktop/handwriting-images"`、`"./handwriting-images"`。（程序会自动读取该目录及子目录下的所有`jpg,png,jpeg,tif,tiff,bmp,pdf`格式的文件）
* 支持使用手写图片或PDF文件的web链接（程序会自动下载到本地并进行识别）

## 注意事项
* 由于使用了`f-string`，因此该程序运行版本不能低于`python3.6`
* 本程序开发环境为`Win11 x64`、`python 3.10 amd64`，但是对于其他linux系统和其他python版本应当都可用
* 腾讯云通用手写体识别，每月免费额度1000次，接口请求频率限制：10次/秒
* 每个图片经Base64编码后不能超过7M
