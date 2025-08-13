import os
import logging
import argparse
from file_manager import FileManager
from pdf_processor import PDFProcessor
from wechat_uploader import WeChatUploader
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)


def main():
    """主程序：处理桌面PDF，添加水印，转换为PNG，上传到微信并发布图文消息"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Process PDFs and upload to WeChat as articles")
    parser.add_argument(
        "--folder",
        type=str,
        help="Folder containing PDF files to process (default: desktop)",
        default=None
    )
    args = parser.parse_args()

    # 加载环境变量
    load_dotenv()

    # 设置PDF扫描路径
    default_desktop = os.path.expanduser("~/Desktop")
    desktop_path = os.getenv("DESKTOP_PATH", default_desktop)
    pdf_folder = args.folder if args.folder else desktop_path

    # 验证文件夹路径
    if not os.path.exists(pdf_folder):
        logger.error(f"指定的PDF文件夹不存在：{pdf_folder}")
        raise FileNotFoundError(f"指定的PDF文件夹不存在：{pdf_folder}")

    # 初始化FileManager
    # desktop_path = os.getenv("DESKTOP_PATH", os.path.expanduser("~/Desktop"))
    output_base_path = os.getenv("OUTPUT_BASE_PATH", os.path.join(os.path.dirname(__file__), "output"))
    file_manager = FileManager(desktop_path=pdf_folder, output_base_path=output_base_path)
    logger.info(f"Desktop path: {desktop_path}, Output base path: {output_base_path}")

    # 初始化PDFProcessor
    watermark_image = os.getenv("WATERMARK_IMAGE", os.path.join(os.path.dirname(__file__), "resources/watermark.png"))
    watermark_alpha = float(os.getenv("WATERMARK_ALPHA", 0.5))
    pdf_processor = PDFProcessor(file_manager, watermark_image=watermark_image, watermark_alpha=watermark_alpha)
    logger.info(f"Watermark image: {watermark_image}, Alpha: {watermark_alpha}")

    # 初始化WeChatUploader
    wechat_uploader = WeChatUploader(file_manager)
    cover_image_path = os.getenv("COVER_IMAGE_PATH", os.path.join(os.path.dirname(__file__), "resources/cover_image.jpg"))
    logger.info(f"Cover image: {cover_image_path}")

    # 获取桌面上的PDF文件
    pdf_files = file_manager.get_pdf_files()
    if not pdf_files:
        logger.warning("未在桌面上找到PDF文件")
        return

    output_pdfs = []
    titles = []
    output_folders = []

    # 处理每个PDF文件
    for pdf_path in pdf_files:
        try:
            logger.info(f"处理PDF文件：{pdf_path}")

            # 添加水印
            output_pdf = os.path.join(file_manager.output_base_path,
                                      f"{os.path.splitext(os.path.basename(pdf_path))[0]}_watermarked.pdf")
            pdf_processor.add_watermark(pdf_path, output_pdf)
            logger.info(f"水印PDF生成：{output_pdf}")

            # 转换为PNG图片
            output_folder = pdf_processor.convert_pdf_to_images(output_pdf)
            logger.info(f"PNG图片生成在：{output_folder}")

            # 收集
            output_pdfs.append(output_pdf)
            title = f"试卷分享-{os.path.splitext(os.path.basename(pdf_path))[0]}"
            titles.append(title)
            output_folders.append(output_folder)

        except Exception as e:
            logger.error(f"处理PDF文件失败：{pdf_path}, 错误：{e}")
            continue

        if not output_pdfs:
            logger.warning("没有成功处理PDF文件, 无法创建图文消息")
            return

    # 创建图文消息
    try:
        article_media_id = wechat_uploader.create_article(output_pdfs, titles, cover_image_path=cover_image_path)
        logger.info(f"多篇文章草稿创建成功, media_id: {article_media_id}")

    except Exception as e:
        logger.error(f"创建多文章图文消息失败，错误：{e}")
        return

    finally:
        # 删除临时文件
        for output_pdf, output_folder in zip(output_pdfs, output_folders):
            try:
                if os.path.exists(output_pdf):
                    os.remove(output_pdf)
                    logger.info(f"删除临时水印PDF：{output_pdf}")
                file_manager.delete_folder(output_folder)
                logger.info(f"删除临时PNG文件夹：{output_folder}")
            except Exception as e:
                logger.error(f"删除临时文件失败：{output_pdf} 或 {output_folder}, 错误：{e}")


if __name__ == "__main__":
    main()
