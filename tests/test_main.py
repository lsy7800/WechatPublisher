import os
import pytest
from src.file_manager import FileManager
from src.pdf_processor import PDFProcessor
from src.wechat_uploader import WeChatUploader
from src.main import main
from pathlib import Path
from PIL import Image
import requests_mock
from reportlab.pdfgen import canvas


@pytest.fixture
def temp_dir(tmp_path):
    """创建临时测试目录"""
    return tmp_path


@pytest.fixture
def env_file(temp_dir):
    """创建临时的.env文件"""
    env_path = temp_dir / ".env"
    with open(env_path, "w") as f:
        f.write("WECHAT_APPID=test_appid\nWECHAT_APPSECRET=test_appsecret\n")
        f.write(f"DESKTOP_PATH={temp_dir}/desktop\n")
        f.write(f"OUTPUT_BASE_PATH={temp_dir}/output\n")
        f.write("WATERMARK_IMAGE=resources/watermark.png\n")
        f.write("WATERMARK_ALPHA=0.5\n")
        f.write("COVER_IMAGE_PATH=resources/cover_image.jpg\n")
    return env_path


@pytest.fixture
def setup_files(temp_dir):
    """创建测试文件"""
    desktop_dir = temp_dir / "desktop"
    desktop_dir.mkdir()
    resources_dir = temp_dir / "resources"
    resources_dir.mkdir()

    # 创建测试PDF
    pdf_path = desktop_dir / "test.pdf"
    c = canvas.Canvas(str(pdf_path))
    c.drawString(100, 100, "Test PDF")
    c.save()

    # 创建水印图片
    watermark_path = resources_dir / "watermark.png"
    img = Image.new("RGBA", (150, 100), (255, 0, 0, 128))
    img.save(watermark_path)

    # 创建封面图片
    cover_path = resources_dir / "cover_image.jpg"
    img_rgb = img.convert("RGB")
    img_rgb.save(cover_path, format="JPEG", quality=80)

    return pdf_path, watermark_path, cover_path


def test_main(temp_dir, env_file, setup_files, requests_mock):
    """测试main.py完整流程"""
    pdf_path, _, cover_path = setup_files

    # 模拟微信API
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

    # 运行main
    main()

    # 验证输出
    output_pdf = temp_dir / "output" / "test_watermarked.pdf"
    output_folder = temp_dir / "output" / "test"
    assert output_pdf.exists()
    assert output_folder.exists()
    assert any(output_folder.glob("*.png"))
