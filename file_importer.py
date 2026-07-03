"""资料导入 —— 支持 PDF / Word / TXT / Markdown"""
from pypdf import PdfReader   #第三方库 PyPDF2 的读取类，专门用来解析 PDF 文件。
from docx import Document     #专门用来读取 .docx Word 文档的类。


def import_file(uploaded_file):
    """读取上传的文件，返回提取的文本内容。
    参数 uploaded_file：Streamlit 的 UploadedFile 对象
    返回：字符串（提取的文本），如果读取失败返回空字符串
    """
    if uploaded_file is None:
        return ""

    fn = uploaded_file.name.lower()  #统一后缀判断逻辑

    if fn.endswith(".pdf"):
        pages = PdfReader(uploaded_file).pages
        return "\n".join([p.extract_text() or "" for p in pages])  # 遍历每一页提取文本，无文本页面填空字符串，用换行符拼接所有页面内容并返回

    if fn.endswith(".docx"):
        paragraphs = Document(uploaded_file).paragraphs
        return "\n".join([p.text for p in paragraphs])

    # txt / md / 其他文本格式
    return uploaded_file.read().decode("utf-8")  # 匹配txt、md等纯文本文件，读取二进制流并以utf-8编码解码为字符串返回
