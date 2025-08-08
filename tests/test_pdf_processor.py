import os
import pytest
from src.file_manager import FileManager
from src.pdf_processor import PDFProcessor
from PyPDF2 import PdfReader
from pathlib import Path
from PIL import Image


@pytest.fixture
def temp_dir(tmp_path):
    """创建临时测试目录"""
    return tmp_path


@pytest.fixture
def file_manager(temp_dir):
    """初始化FileManager实例"""
    return FileManager(desktop_path=str(temp_dir), output_base_path=str(temp_dir / "output"))


@pytest.fixture
def watermark_image(temp_dir):
    """创建临时水印图片（150x100）"""
    watermark_path = temp_dir / "resources" / "watermark.png"
    os.makedirs(temp_dir / "resources", exist_ok=True)
    img = Image.new("RGBA", (150, 100), (255, 0, 0, 128))  # 红色半透明图片
    img.save(watermark_path)
    return str(watermark_path)


@pytest.fixture
def pdf_processor(file_manager, watermark_image):
    """初始化PDFProcessor实例，设置透明度0.5"""
    return PDFProcessor(file_manager, watermark_image=watermark_image, watermark_alpha=0.5)


def test_add_watermark(temp_dir, pdf_processor):
    """测试添加居中图片水印功能"""
    from reportlab.pdfgen import canvas
    test_pdf = str(temp_dir / "test.pdf")
    c = canvas.Canvas(test_pdf)
    c.drawString(100, 100, "Test PDF")
    c.save()

    output_pdf = str(temp_dir / "output.pdf")
    pdf_processor.add_watermark(test_pdf, output_pdf)

    assert os.path.exists(output_pdf)
    reader = PdfReader(output_pdf)
    assert len(reader.pages) == 1


def test_convert_pdf_to_images(temp_dir, pdf_processor):
    """测试PDF转PNG图片功能"""
    from reportlab.pdfgen import canvas
    test_pdf = str(temp_dir / "test.pdf")
    c = canvas.Canvas(test_pdf)
    c.drawString(100, 100, "Test PDF")
    c.save()

    output_folder = pdf_processor.convert_pdf_to_images(test_pdf)
    assert os.path.exists(output_folder)
    assert os.path.exists(os.path.join(output_folder, "test_page_1.png"))


def test_watermark_transparency(temp_dir, file_manager, watermark_image):
    """测试水印透明度设置"""
    pdf_processor = PDFProcessor(file_manager, watermark_image=watermark_image, watermark_alpha=0.3)

    from reportlab.pdfgen import canvas
    test_pdf = str(temp_dir / "test.pdf")
    c = canvas.Canvas(test_pdf)
    c.drawString(100, 100, "Test PDF")
    c.save()

    output_pdf = str(temp_dir / "output.pdf")
    pdf_processor.add_watermark(test_pdf, output_pdf)

    assert os.path.exists(output_pdf)
    reader = PdfReader(output_pdf)
    assert len(reader.pages) == 1