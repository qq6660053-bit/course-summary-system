# 课程资料智能摘要与测验生成系统

基于大语言模型的课程资料自动化处理与智能问答系统。上传课程PDF/TXT，一键生成摘要、知识点提纲和选择题，并基于RAG架构实现跨章节知识问答。

## 功能

**文档处理**
- 资料导入：支持 PDF / Word / TXT / Markdown
- 摘要生成：200-300字课程摘要（单轮直接生成 vs 多轮分步迭代 双方案对比）
- 知识点提纲：分层Markdown输出
- 选择题生成：5道四选一 + 答案 + 解析（双方案对比）
- 结果导出：JSON / Markdown / HTML

**RAG智能问答**
- 文档切分与向量化（text-embedding-v2，1536维）
- 本地知识库构建与持久化
- 余弦相似度语义检索
- LLM生成带【引用来源】的回答
- 四类查询：章节问答 / 跨章节比较 / 复习提纲 / 自测推荐
- 习题推荐（题库匹配 + 自动生成兜底）

## 技术栈

Python / 通义千问 API / Streamlit / Embedding API / Prompt Engineering

## 快速开始

```bash
pip install streamlit openai pypdf python-docx
streamlit run app.py
```

在 `config.py` 中配置你的阿里云百炼 API Key。

## 项目结构

```
├── config.py               # API配置
├── file_importer.py        # 资料导入
├── summarizer.py           # 摘要生成（双方案对比）
├── outline_generator.py    # 知识点提纲生成
├── quiz_generator.py       # 选择题生成（双方案对比）
├── exporter.py             # 结果导出
├── chunker.py              # 文档切分
├── vector_store.py         # 向量化+知识库+检索
├── qa_generator.py         # RAG生成+引用来源
├── exercise_recommender.py # 题目推荐
├── experiment.py           # 对比实验脚本
├── app.py                  # Web主界面
└── 实验报告.md              # 完整实验报告
```

## 实验结论

对比实验表明：多轮分步迭代在字数控制（340字→300字）和格式规范性上优于单轮直接生成，但耗时约为单轮的2.8倍（23.8s vs 66.8s）。两种方案各有适用场景——单轮适合实时交互，多轮适合高质量输出需求。
