import os
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A3, A4
from reportlab.pdfgen import canvas
import fitz
from io import BytesIO
from PIL import Image


class PDFProcessor:
    def __init__(self, file_manager, watermark_image="resources/watermark.png", watermark_alpha=0.5):
        self.file_manager = file_manager
        # 使用绝对路径
        self.watermark_image = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", watermark_image))
        if not os.path.exists(self.watermark_image):
            raise FileNotFoundError(f"水印图片未找到：{self.watermark_image}")
        self.watermark_alpha = max(0.0, min(1.0, watermark_alpha))  # 限制透明度在0.0到1.0之间

    def add_watermark(self, input_pdf, output_pdf):
        """为PDF文件添加居中图片水印"""
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        watermark_pdf = self._create_image_watermark_pdf()
        for page in reader.pages:
            page.merge_page(watermark_pdf.pages[0])
            writer.add_page(page)
        with open(output_pdf, "wb") as output_file:
            writer.write(output_file)

    def _create_image_watermark_pdf(self):
        """创建包含居中图片水印的PDF"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        page_width, page_height = A4  # 612x792 pt

        # 动态获取水印图片尺寸
        with Image.open(self.watermark_image) as img:
            watermark_width, watermark_height = img.size
            # 按比例缩放，限制最大宽度为200 pt
            max_width = 450
            if watermark_width > max_width:
                scale = max_width / watermark_width
                watermark_width = max_width
                watermark_height = watermark_height * scale

        # 计算居中位置
        x_position = (page_width - watermark_width) / 2
        y_position = 0

        # 设置透明度并绘制水印图片
        c.setFillAlpha(self.watermark_alpha)  # 设置透明度
        c.drawImage(self.watermark_image, x_position, y_position,
                    width=watermark_width, height=watermark_height, mask="auto")
        c.save()
        buffer.seek(0)
        watermark_reader = PdfReader(buffer)
        return watermark_reader

    def convert_pdf_to_images(self, pdf_path):
        """将PDF转换为PNG图片并保存到输出文件夹"""
        output_folder = self.file_manager.create_output_folder(pdf_path)
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

        # 使用PyMuPDF打开PDF
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))  # 300 DPI
            image_path = os.path.join(output_folder, f"{pdf_name}_page_{page_num+1}.png")
            pix.save(image_path, "png")
        doc.close()
        return output_folder
