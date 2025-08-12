# 测试
from file_manager import FileManager
from pdf_processor import PDFProcessor
from pathlib import Path
from wechat_uploader import WeChatUploader


def main():
    file_manager = FileManager(desktop_path=str(Path.home() / "Desktop"))
    # pdf_processor = PDFProcessor(file_manager)
    #
    # pdf_processor.add_watermark(file_manager.get_pdf_files()[0], "test_pdf.pdf")
    #
    # pdf_processor.convert_pdf_to_images("test_pdf.pdf")

    # 测试上传功能
    wechat_uploader = WeChatUploader(file_manager)

    wechat_uploader.create_article(
        "./test_pdf.pdf",
    )


if __name__ == "__main__":
    main()
