"""选择题生成 —— 两种方案对比：单轮直接 vs 多轮分步"""
import json
from config import client, MODEL


def quiz_single(text):
    """方案一：单轮直接生成 —— 一次调用出5道题"""
    prompt = f"""请根据以下课程内容生成5道四选一选择题。

课程资料：
{text}

输出要求：
1. 严格输出纯JSON数组，不要包含任何其他文字
2. JSON格式如下：
[
  {{
    "question": "题目内容",
    "options": ["A. 选项一", "B. 选项二", "C. 选项三", "D. 选项四"],
    "answer": "A",
    "explanation": "解析说明"
  }}
]
3. 题目必须覆盖不同知识点，不能集中在某一段
4. 正确答案必须唯一且明确"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    result = resp.choices[0].message.content
    result = result.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return [{"question": "JSON解析失败", "options": [], "answer": "", "explanation": result[:200]}]


def quiz_multi(text):
    """方案二：多轮分步迭代 —— 提取知识点 → 逐知识点出题 → 格式化"""
    # 步骤一：提取5个适合出题的知识点
    step1 = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": f"""请从以下课程资料中提取5个最适合出选择题的知识点。
每个知识点一行，格式："知识点名称：一句话描述"。

课程资料：
{text}"""}],
        temperature=0.3
    )
    knowledge_points = step1.choices[0].message.content

    # 步骤二：基于知识点出题
    step2 = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": f"""请基于以下知识点，为每个知识点出一道四选一选择题。
输出纯JSON数组。

知识点列表：
{knowledge_points}

JSON格式：
[
  {{
    "question": "题目内容",
    "options": ["A. xxx", "B. xxx", "C. xxx", "D. xxx"],
    "answer": "A",
    "explanation": "解析说明（为什么A对，其他选项错在哪）"
  }}
]"""}],
        temperature=0.5
    )
    result = step2.choices[0].message.content
    result = result.replace("```json", "").replace("```", "").strip()
    try:
        questions = json.loads(result)
        # 步骤三：校验题目质量
        step3 = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": f"""请检查以下选择题的质量。如果有问题请修正后重新输出完整JSON。

题目：
{json.dumps(questions, ensure_ascii=False)}

修正标准：
1. 每题必须有唯一正确答案
2. 错误选项必须看似合理但确实错误
3. 解析必须说明为什么正确答案对、为什么其他选项错
4. 题目之间不能有知识点重叠

输出修正后的完整JSON数组。"""}],
            temperature=0.3
        )
        final = step3.choices[0].message.content
        final = final.replace("```json", "").replace("```", "").strip()
        return json.loads(final)
    except json.JSONDecodeError:
        return questions if isinstance(questions, list) else [{"question": "解析失败", "options": [], "answer": "", "explanation": str(result)[:200]}]


def compare_quiz(text):
    """返回 (单轮结果, 多轮结果)"""
    return quiz_single(text), quiz_multi(text)
