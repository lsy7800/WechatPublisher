import os
import random
import time

import requests
from dotenv import load_dotenv
import json


class WeChatUploader:
    def __init__(self, file_manager):
        self.file_manager = file_manager
        load_dotenv()
        self.appid = os.getenv("WECHAT_APPID")
        self.appsecret = os.getenv("WECHAT_APPSECRET")
        if not self.appid or not self.appsecret:
            raise ValueError("微信公众号的AppID或AppSecret未在.env文件中配置")
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        """获取微信公众号的Access Token"""
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.appsecret
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "access_token" in data:
            return data["access_token"]
        raise ValueError(f"获取Access Token失败：{data.get('errmsg', '未知错误')}")

    def upload_image(self, image_path):
        """上传图片到永久-微信素材管理，返回media_id"""
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={self.access_token}&type=image"
        with open(image_path, "rb") as image_file:
            files = {"media": image_file}
            response = requests.post(url, files=files)
            response.raise_for_status()
            data = response.json()
            if "media_id" in data:
                return data["media_id"]
            raise ValueError(f"图片上传失败：{data.get('errmsg', '未知错误')}")

    def upload_temp_image(self, image_path):
        """上传图片到临时-微信素材管理，返回url"""
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={self.access_token}"
        with open(image_path, "rb") as image_file:
            files = {"media": image_file}
            response = requests.post(url, files=files)
            response.raise_for_status()
            data = response.json()
            if "url" in data:
                print(data)
                return data["url"]
            raise ValueError(f"图片上传失败：{data.get('errmsg', '未知错误')}")

    def create_article(self, pdf_path, title="PDF分享", cover_image_path="../resources/cover_image.jpg"):
        """创建并发布图文消息"""
        # 获取PDF对应的输出文件夹
        output_folder = self.file_manager.get_output_folder(pdf_path)
        if not os.path.exists(output_folder):
            raise FileNotFoundError(f"输出文件夹未找到：{output_folder}")

        # 上传封面图片
        cover_media_id = self.upload_image(cover_image_path)

        # 收集所有PNG图片
        image_files = [f for f in os.listdir(output_folder) if f.endswith(".png")]
        image_files.sort()  # 按页面顺序排序

        # 上传所有PNG图片并收集url
        image_media_urls = []
        for image_file in image_files:
            image_path = os.path.join(output_folder, image_file)
            pic_url = self.upload_temp_image(image_path)
            time.sleep(random.randint(1, 3))
            image_media_urls.append(pic_url)

        # 构建图文消息内容
        articles = [{
            "title": title,
            "thumb_media_id": cover_media_id,
            "author": "羊驼叨叨叨",
            "digest": "自动生成的PDF分享文章",
            "content": "".join(
                [f'<img src="{media_url}" />' for media_url in
                 image_media_urls]),
            "content_source_url": "",
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }]
        print(articles)

        # 发布图文消息
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self.access_token}"
        try:
            payload = {"articles": articles}
            headers = {
                'Content-Type': 'application/json; charset=utf-8'
            }
            response = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), headers=headers)

            response.raise_for_status()
            data = response.json()
            if "media_id" in data:
                return data["media_id"]
            raise ValueError(f"图文消息创建失败：{data.get('errmsg', '未知错误')}")
        except requests.exceptions.RequestException as e:
            print(e)
            raise
