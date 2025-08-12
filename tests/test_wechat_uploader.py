import os
import pytest
from src.file_manager import FileManager
from src.wechat_uploader import WeChatUploader
from PIL import Image
from pathlib import Path
import requests_mock


@pytest.fixture
def temp_dir(tmp_path):
    """创建临时测试目录"""
    return tmp_path


@pytest.fixture
def file_manager(temp_dir):
    """初始化FileManager实例"""
    return FileManager(desktop_path=str(temp_dir), output_base_path=str(temp_dir / "output"))


@pytest.fixture
def env_file(temp_dir):
    """创建临时的.env文件"""
    env_path = temp_dir / ".env"
    with open(env_path, "w") as f:
        f.write("WECHAT_APPID=test_appid\nWECHAT_APPSECRET=test_appsecret")
    return env_path


@pytest.fixture
def wechat_uploader(file_manager, env_file):
    """初始化WeChatUploader实例"""
    return WeChatUploader(file_manager)


def test_get_access_token(wechat_uploader, requests_mock):
    """测试获取Access Token"""
    requests_mock.get(
        "https://api.weixin.qq.com/cgi-bin/token",
        json={"access_token": "mock_token", "expires_in": 7200}
    )
    access_token = wechat_uploader._get_access_token()
    assert access_token == "mock_token"


def test_upload_image(temp_dir, wechat_uploader, requests_mock):
    """测试图片上传"""
    image_path = temp_dir / "test.png"
    with Image.open("resources/watermark.png") as img:
        img.save(image_path)

    requests_mock.post(
        f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={wechat_uploader.access_token}&type=image",
        json={"media_id": "mock_media_id"}
    )
    media_id = wechat_uploader.upload_image(str(image_path))
    assert media_id == "mock_media_id"


def test_upload_temp_image(temp_dir, wechat_uploader, requests_mock):
    """测试上传临时图片"""
    image_path = temp_dir / "test.png"
    with Image.open("resources/watermark.png") as img:
        img.save(image_path)

    requests_mock.post(
        f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={wechat_uploader.access_token}",
        json={"url": "mock_url"}
    )
    url = wechat_uploader.upload_temp_image(str(image_path))
    assert url == "mock_url"


def test_create_article(temp_dir, file_manager, wechat_uploader, requests_mock):
    """测试创建图文消息"""
    # 创建测试PDF的输出文件夹和PNG图片
    pdf_path = temp_dir / "test.pdf"
    output_folder = file_manager.create_output_folder(str(pdf_path))
    image_path = os.path.join(output_folder, "test_page_1.png")
    with Image.open("resources/watermark.png") as img:
        img.save(image_path)

    cover_image_path = temp_dir / "cover_image.jpg"
    with Image.open("resources/cover_image.jpg") as img:
        img.save(cover_image_path, format="JPEG")

    # 模拟API响应
    requests_mock.get(
        "https://api.weixin.qq.com/cgi-bin/token",
        json={"access_token": "mock_token", "expires_in": 7200}
    )
    requests_mock.post(
        "https://api.weixin.qq.com/cgi-bin/material/add_material",
        json={"media_id": "mock_media_id"}
    )
    requests_mock.post(
        "https://api.weixin.qq.com/cgi-bin/media/uploadimg",
        json={"url": "mock_url"}
    )
    requests_mock.post(
        "https://api.weixin.qq.com/cgi-bin/draft/add",
        json={"media_id": "mock_article_id"}
    )

    article_media_id = wechat_uploader.create_article(str(pdf_path), title="Test Article",
                                                      cover_image_path=str(cover_image_path))
    assert article_media_id == "mock_article_id"
