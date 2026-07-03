"""摘要生成 —— 双方案对比：单轮直接生成 vs 多轮分步迭代"""
from config import client, MODEL


def summary_single(text):
    """方案一：单轮直接生成 —— 一次调用出摘要"""
    prompt = f"""请阅读以下课程资料，生成一份200-300字的摘要。

要求：
1. 概括核心概念和关键知识点
2. 字数严格控制在200-300字之间
3. 语言简洁专业，不要添加个人观点

课程资料：
{text}"""

    resp = client.chat.completions.create(                        ## 发起大模型对话生成请求
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return resp.choices[0].message.content   ## 提取模型返回的第一条回答文本并作为函数返回值


def summary_multi(text):
    """方案二：多轮分步迭代 —— 提取关键点 → 生成摘要 → 压缩润色"""
    # 步骤一：提取关键点
    step1 = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": f"""请从以下课程资料中提取5-8个核心知识点。
每个知识点用一句话概括，不要展开。

课程资料：
{text}"""}],
        temperature=0.3
    )
    key_points = step1.choices[0].message.content          # 保存第一步模型输出的知识点文本

    # 步骤二：基于关键点生成摘要
    step2 = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": f"""基于以下核心知识点，写一篇连贯的课程摘要。
直接输出摘要，不要标注"基于以下知识点"之类的开头。

核心知识点：
{key_points}

要求：语言连贯自然，像一篇独立的摘要。"""}],
        temperature=0.3
    )
    draft = step2.choices[0].message.content

    # 步骤三：压缩到200-300字
    step3 = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": f"""请将以下摘要压缩到200-300字之间。
保持核心信息完整，语言精炼。

原始摘要：
{draft}

直接输出压缩后的摘要，不要解释。"""}],
        temperature=0.3
    )
    return step3.choices[0].message.content


def compare_summary(text):
    """返回 (单轮结果, 多轮结果)"""
    return summary_single(text), summary_multi(text)
