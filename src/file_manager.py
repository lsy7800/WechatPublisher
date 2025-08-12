import os
from pathlib import Path
import shutil


class FileManager:
    def __init__(self, desktop_path=None, output_base_path="output"):
        # 默认使用用户桌面路径
        self.desktop_path = desktop_path or str(Path.home() / "Desktop")
        self.output_base_path = output_base_path
        # 确保输出目录存在
        os.makedirs(self.output_base_path, exist_ok=True)

    def get_pdf_files(self):
        """获取桌面文件夹中的所有PDF文件"""
        pdf_files = []
        for file in os.listdir(self.desktop_path):
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(self.desktop_path, file))
        return pdf_files

    def create_output_folder(self, pdf_path):
        """为PDF文件创建以其命名的输出文件夹"""
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_folder = os.path.join(self.output_base_path, pdf_name)
        os.makedirs(output_folder, exist_ok=True)
        return output_folder

    def get_output_folder(self, pdf_path):
        """获取PDF文件的输出文件夹路径"""
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_folder = os.path.join(self.output_base_path, pdf_name)
        if not os.path.exists(output_folder):
            raise FileNotFoundError(f"输出文件夹未找到：{output_folder}")
        return output_folder

    def delete_folder(self, folder_path):
        """删除指定文件夹及其内容"""
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            return True
        return False
