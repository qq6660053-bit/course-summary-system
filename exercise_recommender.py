"""题目推荐模块 —— 从题库中推荐相关练习"""
import json
import os
from vector_store import VectorStore
from config import client, MODEL

store = VectorStore()


def save_quiz_bank(quizzes, filepath="quiz_bank.json"):
    """将生成的题库保存到文件"""
    existing = []  #初始化一个空列表，用来存放老题库
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            existing = json.load(f)
    existing.extend(quizzes)     #。把新传入的 quizzes（题目列表）拼接到老题库的末尾。这样旧题保留，新题追加。
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)


def load_quiz_bank(filepath="quiz_bank.json"):
    """加载已有题库"""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def recommend_by_topic(topic, quiz_bank=None):
    """根据主题从题库中推荐相关题目。
    如果题库为空或没有匹配结果，则基于知识库自动生成新题。
    """
    if quiz_bank is None:
        quiz_bank = load_quiz_bank()

    # 用向量检索在题库中找相关题目
    relevant = []
    for q in quiz_bank:
        q_text = q.get("question", "")   #取出题目文本，如果没有则设为空字符串。
        q_exp = q.get("explanation", "")  #取出解析文本。
        combined = q_text + " " + q_exp
        if topic.lower() in combined.lower() or any(                 #关键词匹配
            kw in combined for kw in topic.split()                  #把主题按空格拆成多个关键词
        ):
            relevant.append(q)

    # 如果题库匹配不足，自动生成补充题目
    if len(relevant) < 3:
        chunks = store.search(topic, top_k=3)
        if chunks:
            context = "\n\n".join(chunks)  #把检索到的片段拼成上下文。
            prompt = f"""请根据以下课程资料，针对"{topic}"这个知识点生成3道四选一选择题。
输出JSON数组，每题含question、options、answer、explanation。

课程资料：
{context}"""

            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            result = resp.choices[0].message.content
            result = result.replace("```json", "").replace("```", "").strip()  #去除 AI 可能添加的 Markdown 代码块标记。
            try:
                generated = json.loads(result)
                relevant.extend(generated)
            except json.JSONDecodeError:
                pass

    return relevant[:5]  # 最多推荐5题
