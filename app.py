"""
课程作业：课程资料智能摘要与测验生成系统
资料导入
摘要生成 —— 两种方案：单轮直接生成 vs 多轮分步迭代
知识点提纲
选择题生成 —— 两种方案：单轮直接生成 vs 多轮分步迭代
结果导出
"""
import streamlit as st
from file_importer import import_file
from summarizer import compare_summary
from outline_generator import generate_outline
from quiz_generator import compare_quiz
from exporter import export_json, export_markdown, export_html
# ── RAG智能问答功能导入 ──
from qa_generator import init_knowledge_base, ask_chapter_qa, ask_cross_chapter, generate_review_outline, recommend_exercises
from exercise_recommender import save_quiz_bank
# 全局页面基础配置：网页标题、页面布局设为宽屏
st.set_page_config(page_title="课程资料智能处理系统", layout="wide")
st.title("课程资料智能摘要与测验生成系统")
st.caption("基于大语言模型的课程资料智能处理系统")

# ═══════════════════════════
# 资料导入
# ═══════════════════════════
# 创建左侧侧边栏容器，所有文件上传功能放在侧边栏
with st.sidebar:  #侧边栏
    st.header("资料导入")
    st.caption("支持课程PPT提取文本 / TXT / Markdown")
    uploaded_file = st.file_uploader("上传课程资料", type=["txt", "md", "pdf", "docx"])
    if uploaded_file:
        st.success(f"已上传：{uploaded_file.name}")

    # ── RAG智能问答功能：知识库构建按钮 ──
    if uploaded_file and st.button("构建知识库", type="secondary"):
        raw = import_file(uploaded_file)
        if raw:
            with st.spinner("正在切分文档、向量化、构建知识库..."):
                count = init_knowledge_base(raw)
                st.session_state["kb_ready"] = True
                st.session_state["course_text"] = raw
                st.success(f"知识库构建完成，共 {count} 个文档块")

if uploaded_file:
    text = import_file(uploaded_file)
else:
    text = ""

if text:   # 文本不为空时，展示文件全文预览框
    st.text_area("文件内容预览", text, height=180, disabled=True)  #只读文本域，禁用编辑

    # ═══════════════════════════
    # (3)(4)
    # ═══════════════════════════
    st.markdown("---")    #分隔预览区与功能区
    st.header("功能操作")

    t1, t2, t3 = st.tabs([      #标签页
        "摘要生成",
        "知识点提纲",
        "选择题生成"
    ])

    # ── 摘要 ──
    with t1:
        st.caption("自动生成200至300字课程摘要 —— 两种方案对比")
        if st.button("生成摘要（两种方案对比）", type="primary"):
            with st.spinner("方案一和方案二同时生成中..."):   #等待，模型正在计算
                try:
                    s1, s2 = compare_summary(text)
                    st.session_state["summary_single"] = s1  #单轮
                    st.session_state["summary_multi"] = s2   #多轮 3次

                    st.markdown("---")
                    cL, cR = st.columns(2)  #页面横向分成多列，实现并排布局
                    with cL: #左栏：单轮直接生成方案展示
                        st.markdown("### 方案一：单轮直接生成")
                        st.caption("一次调用模型，直接输出最终摘要")
                        st.info(s1)        # info样式文本框展示单轮摘要内容  ---浅蓝色背景，普通提示框
                        st.caption(f"字数：{len(s1)} | API调用：1次")   # # 统计摘要字符长度、API调用次数说明

                    with cR:  # 右栏：多轮分步迭代方案展示
                        st.markdown("### 方案二：多轮分步迭代")
                        st.caption("步骤①提取关键点 → ②生成摘要 → ③压缩润色")
                        st.success(s2)   #浅绿色背景，成功完成提示框
                        st.caption(f"字数：{len(s2)} | API调用：3次")

                    st.markdown("---")
                    st.caption("对比维度：输出质量、字数控制、计算成本。详见实验报告。")
                except Exception as e:
                    st.error(f"失败：{e}")

    # ── 提纲 ──
    with t2:
        st.caption("自动输出分层知识点")  #提示功能说明
        if st.button("生成提纲", type="primary"):
            with st.spinner("生成中..."):  #代码运行耗时的时候，页面显示转圈加载提示
                try:
                    o = generate_outline(text)        # 调用提纲生成函数，返回markdown格式分层提纲
                    st.session_state["outline"] = o   # 存入会话缓存，防止页面刷新丢失
                    st.markdown(o)                    # 直接渲染markdown格式提纲
                except Exception as e:                # 捕捉异常存入e
                    st.error(f"失败：{e}")

    # ── 选择题 ──
    with t3:
        st.caption("自动生成5道四选一选择题 + 答案 + 解析 —— 两种方案对比")
        if st.button("生成选择题（两种方案对比）", type="primary"):
            with st.spinner("方案一和方案二同时生成中..."):
                try:
                    q1, q2 = compare_quiz(text)
                    st.session_state["quiz_single"] = q1
                    st.session_state["quiz_multi"] = q2

                    st.markdown("---")
                    cL, cR = st.columns(2)
                    with cL:
                        st.markdown("### 方案一：单轮直接生成")
                        st.caption("一次调用模型，直接输出5道题")
                        for i, item in enumerate(q1, 1):                            ## 循环遍历5道题目，序号从1开始
                            st.markdown(f"**{i}. {item.get('question', '?')}**")
                            for o in item.get("options", []):
                                st.text(o)
                            st.caption(f"答案：{item.get('answer', '?')} | 解析：{item.get('explanation', '?')}")
                            st.divider()             # 单题分割线
                        st.caption("API调用：1次")

                    with cR:
                        st.markdown("### 方案二：多轮分步迭代")
                        st.caption("①提取知识点 → ②逐知识点出题 → ③校验修正")
                        for i, item in enumerate(q2, 1):
                            st.markdown(f"**{i}. {item.get('question', '?')}**")
                            for o in item.get("options", []):
                                st.text(o)
                            st.caption(f"答案：{item.get('answer', '?')} | 解析：{item.get('explanation', '?')}")
                            st.divider()
                        st.caption("API调用：3次")

                    st.markdown("---")
                    st.caption("对比维度：题目覆盖度、解析质量、格式规范性、计算成本。详见实验报告。")
                except Exception as e:
                    st.error(f"失败：{e}")

    # ═══════════════════════════
    # 结果导出
    # ═══════════════════════════
    if any(k in st.session_state for k in ["summary_single", "summary_multi", "outline", "quiz_single", "quiz_multi"]):  # 判断会话缓存中是否存在任意一种生成结果，存在才展示导出区域
        st.markdown("---")
        st.header("结果导出")
        st.caption("支持导出为 JSON / Markdown / 网页（HTML）")
        # 从会话缓存读取所有生成数据，无数据则为空
        s1 = st.session_state.get("summary_single", "")
        s2 = st.session_state.get("summary_multi", "")
        o = st.session_state.get("outline", "")
        q1 = st.session_state.get("quiz_single", [])
        q2 = st.session_state.get("quiz_multi", [])
        # 三等分布局，三个导出按钮并排
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("导出 JSON"):
                data = {                           # # 整合全部生成内容为字典结构化数据
                    "方案一_单轮摘要": s1,
                    "方案二_多轮摘要": s2,
                    "知识点提纲": o,
                    "方案一_单轮选择题": q1,
                    "方案二_多轮选择题": q2
                }
                export_json(data, "result.json")
                st.success("→ result.json")
        with c2:
            if st.button("导出 Markdown"):
                export_markdown(s2, o, q2, "result.md")
                st.success("→ result.md")
        with c3:
            if st.button("导出 HTML网页"):
                export_html(s2, o, q2, "result.html")
                st.success("→ result.html")

    # ═══════════════════════════════════════
    # RAG智能问答功能：RAG 智能问答（4类查询 + 习题推荐）
    # ═══════════════════════════════════════
    if st.session_state.get("kb_ready"):
        st.markdown("---")
        st.header("RAG 课程智能问答")
        st.caption("支持4类查询 —— 章节知识问答、跨章节比较、复习提纲生成、知识点自测推荐")

        query_type = st.radio(
            "查询类型",
            ["章节知识问答", "跨章节比较分析", "复习提纲生成", "知识点自测推荐"],
            horizontal=True
        )
        user_input = st.text_area("输入问题或主题", placeholder="例如：BERT和GPT有什么区别？", height=80)

        if st.button("提交查询", type="primary") and user_input:
            with st.spinner("正在检索知识库并生成回答..."):
                try:
                    if query_type == "章节知识问答":
                        result = ask_chapter_qa(user_input)
                    elif query_type == "跨章节比较分析":
                        result = ask_cross_chapter(user_input)
                    elif query_type == "复习提纲生成":
                        result = generate_review_outline(user_input)
                    else:
                        result = recommend_exercises(user_input)
                    st.markdown("### 结果")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"查询失败：{e}")

else:
    st.info(" 请在左侧上传课程资料开始使用")      ## 无文件上传/无文本时展示引导提示与系统模块总表
    st.markdown("""
    ### 系统模块一览
    | 模块 | 功能 | 两种方案对比 |
    |------|------|-------------|
    | (1) | 资料导入 | - |
    | (2) | 摘要生成 | 单轮直接生成 vs 多轮分步迭代 |
    | (3) | 知识点提纲 | 分层输出 |
    | (4) | 选择题生成 | 单轮直接生成 vs 多轮分步迭代 |
    | (5) | 结果导出 | JSON / Markdown / HTML |
    ### RAG智能问答
    | 功能模块 | 说明 |
    |---------|------|
    | (1) 文档切分与向量化 | 长文本智能切块，调用Embedding API向量化 |
    | (2) 课程知识库构建 | 向量存入本地知识库，支持持续添加 |
    | (3) 检索模块 | 余弦相似度语义检索 |
    | (4) 基于检索的生成 | 检索结果+问题拼入prompt，LLM生成回答 |
    | (5) 答案引用来源 | 回答末尾标注【引用来源】，可追溯 |
    | (6) 题目推荐 | 从题库检索+自动生成补充题目 |
    | (7) 4类查询 | 章节问答/跨章节比较/复习提纲/自测推荐 |
    """)
