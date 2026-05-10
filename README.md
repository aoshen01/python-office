# python-office

python-office 是一个强大的开源 Python 工具库，旨在帮助开发者轻松实现日常办公中的各种自动化操作。通过简单的代码调用，你可以高效完成从文件处理到数据分析的多种任务。

## 项目特点

- **社区支持**：开源项目，开发者可自由贡献代码或提需求。
- **开箱即用**：功能全面且简单易用，无需复杂配置。
- **持续更新**：项目维护者定期更新，添加更多实用功能。

## 安装

```bash
pip install python-office
```

或从源码安装：

```bash
git clone https://github.com/aoshen01/python-office.git
cd python-office
pip install -e .
```

## 主要功能

### 1. 文档处理

支持 Word、Excel、PDF 等多种格式的文件操作，例如内容提取、格式转换、自动生成等。

```python
from office import Word, Excel, PDF

# Word
Word.create("report.docx", title="Monthly Report", paragraphs=["Hello World"])
text = Word.extract_text("report.docx")
Word.to_txt("report.docx", "report.txt")

# Excel
Excel.create("data.xlsx", [["Alice", 30], ["Bob", 25]], header=["Name", "Age"])
rows = Excel.read("data.xlsx")
Excel.to_csv("data.xlsx", "data.csv")

# PDF
PDF.create("doc.pdf", "Hello PDF", title="My Title")
text = PDF.extract_text("doc.pdf")
```

### 2. 图像处理

包括水印添加、尺寸调整、格式转换等功能。

```python
from office import Image

# 调整尺寸
Image.resize("photo.jpg", 800, 600, output_path="resized.jpg")

# 格式转换
Image.convert("photo.jpg", "PNG", output_path="photo.png")

# 添加文字水印
Image.add_text_watermark("photo.jpg", "CONFIDENTIAL", output_path="wm.jpg")

# 添加图片水印
Image.add_image_watermark("photo.jpg", "logo.png", output_path="logo_wm.jpg")

# 生成缩略图
Image.thumbnail("photo.jpg", max_size=256)
```

### 3. 网络工具

包括二维码生成、网页内容抓取等功能。

```python
from office import Network

# 生成二维码
Network.generate_qrcode("https://github.com/aoshen01/python-office", output_path="qr.png")

# 抓取网页文本
text = Network.extract_text_from_url("https://example.com")

# 提取页面链接
links = Network.extract_links("https://example.com")

# 抓取页面中的表格
table = Network.scrape_table("https://example.com/table-page")
```

### 4. 自动化脚本

轻松实现重复性任务的自动化，如批量重命名文件、批量发送邮件等。

```python
from office import File, Email

# 批量重命名（正则替换）
File.batch_rename("./reports", pattern=r"report_(\d+)", replacement=r"annual_\1")

# 批量编号重命名
File.batch_rename_numbered("./images", prefix="img_", start=1, extensions=[".jpg"])

# 列出目录下的文件
files = File.list_files("./docs", extensions=[".pdf", ".docx"], recursive=True)

# 发送邮件
mailer = Email(
    smtp_host="smtp.gmail.com",
    smtp_port=465,
    username="you@gmail.com",
    password="your-app-password",
    use_ssl=True,
)
mailer.send(to="recipient@example.com", subject="Hello", body="Hi there!")

# 批量发送邮件
errors = mailer.send_batch(
    recipients=["a@example.com", "b@example.com"],
    subject="Newsletter",
    body="<h1>Welcome</h1>",
    html=True,
)
```

## 运行测试

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## 许可证

Apache License 2.0 — 详见 [LICENSE](LICENSE) 文件。
