"""(2)(3)：向量化 + 知识库构建 + 检索"""
import json
import os
from config import client

EMBEDDING_MODEL = "text-embedding-v2"
                                     #定义一个全局常量（通常用大写字母命名）。它指定了我们要使用的向量化模型名称。
                                        # text-embedding-v2 是百炼提供的一个模型，
                                         # 能把一段文字转换成一组固定的数字（向量），方便计算机计算语义相似度


class VectorStore:   #：定义一个名为 VectorStore 的类（可以理解为“向量知识库”的蓝图）。后面的缩进内容全是这个类的属性和方法
    """向量知识库：将文档块转为向量并支持语义检索"""

    def __init__(self, db_path="knowledge_base.json"):
        self.chunks = []      #创建实例属性 chunks，初始为空列表。它用来存储所有文本块（原始文字）。
        self.embeddings = []  #创建实例属性 embeddings，初始为空列表。它用来存储所有文本块对应的向量（数字列表）
        self.db_path = db_path
        self._load()

    def get_embedding(self, text):
        """调用百炼 Embedding API，将文本转为向量（浮点数列表）"""
        resp = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return resp.data[0].embedding

    def add(self, chunks):
        """将一批文档块向量化后加入知识库。返回加入的块数。"""
        added = 0
        for chunk in chunks:
            if not chunk.strip():
                continue
            emb = self.get_embedding(chunk)
            self.chunks.append(chunk)
            self.embeddings.append(emb)
            added += 1
        self._save()
        return added

    def search(self, query, top_k=3):
        """余弦相似度检索，返回最相关的 top_k 个文档块"""
        if not self.chunks:
            return []
        query_emb = self.get_embedding(query)

        scores = []  #准备一个空列表，用来存放每个文档块和查询的相似度分数。
        for emb in self.embeddings:
            # 余弦相似度 = 点积 / (模长乘积)
            dot = sum(a * b for a, b in zip(query_emb, emb))
            norm_q = sum(a * a for a in query_emb) ** 0.5
            norm_d = sum(b * b for b in emb) ** 0.5
            cos_sim = dot / (norm_q * norm_d + 1e-8)
            scores.append(cos_sim)

        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)  #按相似度降序排序，同时保留原始索引
        return [self.chunks[i] for i, _ in ranked[:top_k]]

    def clear(self):
        """清空知识库"""
        self.chunks = []
        self.embeddings = []
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def _save(self):          #把内存里的分块和向量写入本地 JSON 文件
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump({
                "chunks": self.chunks,
                "embeddings": self.embeddings
            }, f, ensure_ascii=False)

    def _load(self):          #启动时从本地 JSON 文件把数据读回内存
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.chunks = data.get("chunks", [])
                self.embeddings = data.get("embeddings", [])
