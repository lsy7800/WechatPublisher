# 微信公众号PDF发布工具 (WeChat Publisher)

一个自动化工具，用于将本地PDF文件添加水印、转换为图片并上传到微信公众号作为图文消息发布。

## 功能特性

- 🔍 **自动扫描PDF文件**：从指定文件夹（默认桌面）自动获取所有PDF文件
- 🎨 **智能水印添加**：为PDF文件添加可自定义透明度的居中图片水印
- 📷 **高质量图片转换**：将PDF页面转换为300 DPI的PNG图片
- 📱 **微信公众号集成**：自动上传图片并创建图文消息草稿
- 🧹 **临时文件清理**：处理完成后自动清理临时生成的文件
- ⚙️ **灵活配置**：支持通过环境变量自定义各种参数

## 项目结构

```
wechatpublisher/
├── src/
│   ├── __init__.py
│   ├── config.py           # 配置文件（预留）
│   ├── file_manager.py     # 文件管理模块
│   ├── pdf_processor.py    # PDF处理模块
│   ├── wechat_uploader.py  # 微信上传模块
│   └── main.py             # 主程序入口
├── resources/
│   ├── watermark.png       # 水印图片
│   └── cover_image.jpg     # 封面图片
├── .env                    # 环境变量配置
├── pyproject.toml          # 项目依赖配置
└── README.md
```

## 安装要求

- Python >= 3.13
- uv 包管理器（推荐）

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd wechatpublisher
```

### 2. 安装依赖

使用 uv 包管理器：

```bash
uv sync
```

或使用 pip：

```bash
pip install -e .
```

### 3. 配置环境变量

复制 `.env.example` 文件并重命名为 `.env`，然后填写以下配置：

```env
# 微信公众号配置（必填）
WECHAT_APPID=your_app_id
WECHAT_APPSECRET=your_app_secret

# 路径配置（可选）
DESKTOP_PATH=C:\Users\YourName\Desktop
OUTPUT_BASE_PATH=output

# 水印配置（可选）
WATERMARK_IMAGE=resources/watermark.png
WATERMARK_ALPHA=0.5

# 封面图片配置（可选）
COVER_IMAGE_PATH=resources/cover_image.jpg
```

### 4. 准备资源文件

- 将水印图片放置在 `resources/watermark.png`
- 将封面图片放置在 `resources/cover_image.jpg`

### 5. 运行程序

处理桌面上的PDF文件：

```bash
cd src
python main.py
```

处理指定文件夹中的PDF文件：

```bash
python src/main.py --folder /path/to/pdf/folder
```

## 详细配置说明

### 环境变量配置

| 变量名 | 描述 | 默认值 | 必填 |
|--------|------|--------|------|
| `WECHAT_APPID` | 微信公众号的AppID | - | ✅ |
| `WECHAT_APPSECRET` | 微信公众号的AppSecret | - | ✅ |
| `DESKTOP_PATH` | PDF文件扫描路径 | 用户桌面 | ❌ |
| `OUTPUT_BASE_PATH` | 输出文件基础路径 | `output` | ❌ |
| `WATERMARK_IMAGE` | 水印图片路径 | `resources/watermark.png` | ❌ |
| `WATERMARK_ALPHA` | 水印透明度 (0.0-1.0) | `0.5` | ❌ |
| `COVER_IMAGE_PATH` | 封面图片路径 | `resources/cover_image.jpg` | ❌ |

### 微信公众号配置

1. 登录微信公众平台
2. 进入开发者工具 > 公众号设置 > 功能设置
3. 获取 `AppID` 和 `AppSecret`
4. 将获取的信息填入 `.env` 文件
5. 将自己的ip地址填入微信公众号后台白名单

## 工作流程

1. **扫描PDF文件**：程序会扫描指定文件夹中的所有PDF文件
2. **添加水印**：为每个PDF文件添加居中的图片水印
3. **转换为图片**：将带水印的PDF页面转换为高质量PNG图片
4. **上传到微信**：
   - 上传封面图片到微信素材库
   - 上传PNG图片到微信临时素材
   - 创建图文消息草稿
5. **清理临时文件**：删除处理过程中生成的临时文件

## 模块说明

### FileManager (file_manager.py)
- 管理文件和文件夹操作
- 扫描PDF文件
- 创建和管理输出目录

### PDFProcessor (pdf_processor.py)
- PDF水印添加功能
- PDF到图片的转换
- 支持自定义水印位置和透明度

### WeChatUploader (wechat_uploader.py)
- 微信公众号API集成
- 图片上传和管理
- 图文消息创建

## 注意事项

⚠️ **重要提醒**：

1. 确保微信公众号已获得相应的接口权限
2. 水印图片建议使用PNG格式以支持透明背景
3. 程序会自动清理临时文件，但建议定期检查输出目录
4. 图文消息将保存为草稿，需要手动发布
5. 请遵守微信公众平台的使用规范和内容政策
6. 封面首图需要自行调整达到最好效果

## 故障排除

### 常见问题

**Q: 程序报错"获取Access Token失败"**  
A: 请检查微信公众号的AppID和AppSecret是否正确配置

**Q: 水印图片未显示**  
A: 请确认水印图片路径正确，且图片格式支持

**Q: PDF转换失败**  
A: 请确认PDF文件未损坏且具有读取权限

**Q: 上传图片失败**  
A: 请检查网络连接和微信公众号接口权限

### 日志查看

程序运行时会输出详细的日志信息，包括：
- 文件处理进度
- 上传状态
- 错误信息

## 开发

### 运行测试

```bash
pytest tests/ -v
```

### 代码结构

项目采用模块化设计，各模块职责清晰：
- 文件管理与PDF处理分离
- 微信API调用独立封装
- 配置管理统一处理

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目！

## 更新日志

### v0.1.0
- 初始版本发布
- 支持PDF水印添加
- 支持图片转换和微信上传
- 支持自动化工作流程