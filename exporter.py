"""结果导出 —— JSON / Markdown / HTML"""
import json


def export_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def export_markdown(summary, outline, quizzes, filepath):
    md = f"# 课程摘要\n\n{summary}\n\n---\n\n"
    md += f"# 知识点提纲\n\n{outline}\n\n---\n\n"
    md += "# 选择题\n\n"
    for i, q in enumerate(quizzes, 1):
        md += f"## 第{i}题\n\n**题目：** {q['question']}\n\n"
        for opt in q['options']:
            md += f"- {opt}\n"
        md += f"\n**正确答案：** {q['answer']}\n\n"
        md += f"**解析：** {q['explanation']}\n\n---\n\n"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md)


def export_html(summary, outline, quizzes, filepath):
    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>课程学习报告</title>
<style>
body{font-family:"Microsoft YaHei",sans-serif;max-width:800px;margin:0 auto;padding:20px;line-height:1.8}
h1{border-bottom:2px solid #333;padding-bottom:10px}
h2{margin-top:30px;color:#2c3e50}
.question{background:#f8f9fa;padding:15px;margin:15px 0;border-radius:8px;border-left:4px solid #3498db}
.answer{color:#27ae60;font-weight:bold}
</style></head><body>"""
    html += f"<h1>课程摘要</h1><p>{summary}</p>"
    html += f"<h1>知识点提纲</h1>{outline}"
    html += "<h1>选择题</h1>"
    for i, q in enumerate(quizzes, 1):
        html += f'<div class="question"><strong>第{i}题：{q["question"]}</strong><br>'
        for opt in q['options']:
            html += f"{opt}<br>"
        html += f'<span class="answer">答案：{q["answer"]} | 解析：{q["explanation"]}</span></div>'
    html += "</body></html>"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
