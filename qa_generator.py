"""(5)：基于检索结果的生成 + 答案引用来源显示"""
from config import client, MODEL
from vector_store import VectorStore

store = VectorStore()


def init_knowledge_base(course_text, chunk_size=500, overlap=100):
    """将整本课程文本切块、向量化、存入知识库。返回块数。"""
    from chunker import chunk_text
    chunks = chunk_text(course_text, chunk_size, overlap) #：调用切分函数，把长文本切成小块。
    count = store.add(chunks)              #调用 VectorStore 的 add 方法，把所有块向量化并存入数据库。count 是成功存入的块数量。
    return count


# ═══════════════════════════════════
# 类型1：章节知识问答
# ═══════════════════════════════════
def ask_chapter_qa(question):


    chunks = store.search(question, top_k=3)  #调用知识库的 search 方法，把用户的问题作为查询，找出最相关的 3 个文本块。
    context = "\n\n---\n\n".join(chunks)  #把找出来的 3 个文本块，用 \n\n---\n\n（两个换行 + 分隔线 + 两个换行）拼接成一个长字符串

    prompt = f"""你是一个课程助教。请基于以下课程资料回答学生的问题。

【课程资料】
{context}

【学生问题】
{question}

要求：
1. 用中文回答，语言简洁清晰
2. 优先引用资料中的具体内容来支持你的回答
3. 如果资料中没有足够的信息，请明确说明
4. 在回答末尾用【引用来源】标注主要引用的资料段落编号"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return resp.choices[0].message.content


# ═══════════════════════════════════
# 类型2：跨章节比较分析
# ═══════════════════════════════════
def ask_cross_chapter(question):
    chunks = store.search(question, top_k=5)
    context = "\n\n---\n\n".join(chunks)

    prompt = f"""你是一个课程助教。请基于以下课程资料，对不同章节的相关内容进行对比分析。

【课程资料（来自不同章节）】
{context}

【对比问题】
{question}

要求：
1. 分别列出各章节中相关的知识点
2. 用对比的方式说明它们的异同
3. 如果存在互为补充或相互矛盾的内容，请特别指出
4. 在末尾用【引用来源】标注各知识点的资料出处"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return resp.choices[0].message.content


# ═══════════════════════════════════
# 类型3：复习提纲生成
# ═══════════════════════════════════
def generate_review_outline(topic=""):
    query = topic if topic else "课程核心知识点 重点难点"
    chunks = store.search(query, top_k=5)
    context = "\n\n---\n\n".join(chunks)

    prompt = f"""你是一个课程助教。请基于以下课程资料，生成一份系统化的复习提纲。

【课程资料】
{context}

【复习主题】{topic if topic else "全部课程内容"}

要求：
1. 使用 Markdown 层级格式（## 大章节，### 小节，- 具体知识点）
2. 用 ⭐ 标注重要程度（⭐一般 ⭐⭐重点 ⭐⭐⭐必考）
3. 知识点按逻辑递进关系组织
4. 末尾列出5个常见易混淆知识点并做辨析
5. 用【引用来源】标注提纲中各章节的知识来源"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return resp.choices[0].message.content


# ═══════════════════════════════════
# 类型4：知识点自测推荐
# ═══════════════════════════════════
def recommend_exercises(topic=""):
    query = topic if topic else "核心知识点"
    chunks = store.search(query, top_k=3)
    context = "\n\n---\n\n".join(chunks)

    prompt = f"""你是一个课程助教。请根据以下课程资料，为学生推荐自测题目并给出学习建议。

【课程资料】
{context}

要求：
1. 识别3个学生可能薄弱的环节
2. 为每个薄弱环节推荐一道自测题（四选一，含答案和解析）
3. 给出针对性的学习计划建议
4. 用 JSON 格式输出：
{{
  "weak_points": ["薄弱点1", "薄弱点2", "薄弱点3"],
  "questions": [
    {{"question": "...", "options": ["A...","B...","C...","D..."], "answer": "A", "explanation": "..."}}
  ],
  "study_plan": "学习建议内容"
}}
5. 末尾用【引用来源】标注题目所依据的资料内容"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    result = resp.choices[0].message.content
    return result.replace("```json", "").replace("```", "").strip()
