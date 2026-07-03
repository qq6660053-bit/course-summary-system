"""知识点提纲 —— 自动输出分层知识点"""
from config import client, MODEL


def generate_outline(text):
    prompt = f"""请为以下课程内容生成分层知识点提纲。

要求：
1. 使用 Markdown 格式，第一层用 ## ，第二层用 ### ，第三层用 -
2. 每个知识点用一句话概括
3. 知识点之间要有逻辑递进关系
4. 覆盖所有重要内容，不要遗漏

课程资料：
{text}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content
