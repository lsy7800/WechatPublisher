import os
import pytest
from pathlib import Path
from src.file_manager import FileManager


@pytest.fixture
def temp_dir(tmp_path):
    """创建临时测试目录"""
    return tmp_path


@pytest.fixture
def file_manager(temp_dir):
    """初始化FileManager实例"""
    return FileManager(desktop_path=str(temp_dir), output_base_path=str(temp_dir / "output"))


def test_get_pdf_files(temp_dir, file_manager):
    """测试获取PDF文件功能"""
    # 创建测试PDF文件
    pdf1 = temp_dir / "test1.pdf"
    pdf2 = temp_dir / "test2.pdf"
    non_pdf = temp_dir / "test.txt"
    pdf1.write_bytes(b"")  # 创建空PDF文件
    pdf2.write_bytes(b"")
    non_pdf.write_bytes(b"")

    pdf_files = file_manager.get_pdf_files()
    assert len(pdf_files) == 2
    assert str(pdf1) in pdf_files
    assert str(pdf2) in pdf_files
    assert str(non_pdf) not in pdf_files


def test_create_output_folder(temp_dir, file_manager):
    """测试创建输出文件夹功能"""
    pdf_path = str(temp_dir / "test.pdf")
    output_folder = file_manager.create_output_folder(pdf_path)
    expected_folder = str(temp_dir / "output" / "test")
    assert output_folder == expected_folder
    assert os.path.exists(output_folder)


def test_delete_folder(temp_dir, file_manager):
    """测试删除文件夹功能"""
    folder_path = str(temp_dir / "output" / "test_folder")
    os.makedirs(folder_path)
    assert os.path.exists(folder_path)
    result = file_manager.delete_folder(folder_path)
    assert result is True
    assert not os.path.exists(folder_path)


def test_delete_nonexistent_folder(temp_dir, file_manager):
    """测试删除不存在的文件夹"""
    folder_path = str(temp_dir / "nonexistent")
    result = file_manager.delete_folder(folder_path)
    assert result is False
