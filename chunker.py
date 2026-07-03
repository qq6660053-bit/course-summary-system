"""文档切分模块 —— 将长文本智能切分为适合向量化的小块"""
import re


def chunk_text(text, chunk_size=500, overlap=100):
    """将长文本切成固定大小的块，相邻块之间重叠 overlap 字。
    优先按段落边界切分，避免句子被截断。
    """
    if not text:
        return []

    # 先按段落分
    paragraphs = re.split(r"\n\s*\n", text)
    chunks = []        #初始化一个空列表，用于存放最终生成的文本块。
    current = ""           #用于累积当前正在构建的块内容（字符串）。

    for para in paragraphs:
        para = para.strip()  #移除字符串首尾所有空白字符（包括换行符 \n、空格、制表符 \t 等），字符串中间的空格会保留。
        if not para:
            continue
        # 如果当前块加上新段落不超限，就追加
        if len(current) + len(para) <= chunk_size:
            current += para + "\n\n"
        else:
            # 当前块存起来
            if current.strip():
                chunks.append(current.strip())
            # 新段落开始新块
            current = para + "\n\n"

    if current.strip():
        chunks.append(current.strip())

    # 如果块太少（长段落），用固定窗口再切一次
    if not chunks or max(len(c) for c in chunks) > chunk_size * 1.5:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(text):
                break
            start = end - overlap

    return chunks



# #具体来说，代码不是把“段落结果”和“窗口结果”拼在一起，而是二选一：
#
# 上面部分（优先）：先尝试按段落切分，这是最理想的方式（保证句子完整）。
#
# 中间的条件（裁判）：检查上面的结果合不合格。
#
# 下面部分（兜底）：只有上面结果不合格时，才执行下面部分，把上面部分的结果全部覆盖掉，改用强制滑动窗口切分。
#
# 1. 上面部分（优先策略）
# 目标：保持语义完整。
#
# 做法：顺着段落走，尽量把一个完整的段落塞进一个块里。如果一个块放不下，就断在段落与段落之间。
#
# 结果：chunks 里的块基本上是“完整段落”或“几个完整段落的组合”。
#
# 2. 中间的条件判断（裁判）
# python
# if not chunks or max(len(c) for c in chunks) > chunk_size * 1.5:
# 这句话是“兜底”的开关，它在判断两种情况：
#
# 情况A（not chunks）：上面完全没切出块来（比如整个文本没有一个空行，全是一个超长段落）。
#
# 情况B（max(len(c) ...) > chunk_size * 1.5）：上面切出来的块里，最大的那一块超过了 750 字（因为你的 chunk_size=500，1.5倍=750）。
#
# 意思就是：如果上面的段落式切分，切出来一个长达 800 字的块，这个块太长了，后面模型可能处理不了，所以必须把这个“不合格”的结果抛弃。
#
# 3. 下面部分（兜底/强制策略）
# 触发时机：只要上面两条任意一条成立（切不出来，或块太大），就执行下面。
#
# 做什么：chunks = []（清空上面所有辛苦切出来的结果），然后改用 while 循环，死板地每隔 500 个字切一刀，同时保留 100 个字的重叠。
#
# 结果：虽然可能会把句子拦腰截断，但保证了每个块都不会超过 500 字，程序绝对不会因为文本太长而崩溃。

#31-33
#
# 兜底保存：确保文本末尾的内容不会被遗忘，全部被切分成块。
#
# 数据清洗：去除末尾多余的空行和换行符，保证入库的文本块是干净的。
#
# 防呆处理：如果最后只剩空白，自动忽略，不产生无效的空块。
#
# 一句话记忆点：它解决的是 “循环结束，手有余料” 的问题，是保证文本不丢失的 “最后一公里”。