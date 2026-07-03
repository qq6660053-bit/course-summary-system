"""两种方案对比实验：单轮直接生成 vs 多轮分步迭代"""
import time
from summarizer import summary_single, summary_multi
from quiz_generator import quiz_single, quiz_multi

TEST_TEXT = """
自然语言处理（NLP）是人工智能的一个重要分支，主要研究计算机与人类自然语言之间的交互。
NLP的核心任务包括：分词、词性标注、命名实体识别、句法分析、语义理解、情感分析、文本分类等。

近年来，基于Transformer架构的预训练语言模型极大地推动了NLP的发展。
BERT通过双向编码器在大规模无标注文本上预训练，然后在特定下游任务上微调，在多项NLP基准测试中取得突破性成绩。

GPT系列则采用自回归解码器架构，通过海量数据训练，展示了强大的语言生成能力。
从GPT-3到GPT-4，模型规模不断扩大，涌现出了上下文学习、思维链推理等能力。

大语言模型（LLM）是指参数量达到数十亿甚至数千亿的语言模型。
它们通过在海量文本数据上进行预训练，学习到了丰富的语言知识和世界知识，
能够完成翻译、摘要、问答、代码生成等多种任务，而无需针对每个任务单独训练。
"""

print("=" * 60)
print("实验：单轮直接生成 vs 多轮分步迭代")
print("=" * 60)

# 摘要对比
print("\n【摘要生成对比】\n")

t0 = time.time()
r1 = summary_single(TEST_TEXT)
t1 = round(time.time() - t0, 2)

t0 = time.time()
r2 = summary_multi(TEST_TEXT)
t2 = round(time.time() - t0, 2)

print(f"方案一（单轮直接生成）：")
print(f"  耗时：{t1}s | 字数：{len(r1)} | API调用：1次")
safe1 = r1[:120].encode("gbk", errors="replace").decode("gbk", errors="replace")
print(f"  内容：{safe1}...")

print(f"\n方案二（多轮分步迭代）：")
print(f"  耗时：{t2}s | 字数：{len(r2)} | API调用：3次")
safe2 = r2[:120].encode("gbk", errors="replace").decode("gbk", errors="replace")
print(f"  内容：{safe2}...")

# 选择题对比
print("\n\n【选择题生成对比】\n")

t0 = time.time()
q1 = quiz_single(TEST_TEXT)
t3 = round(time.time() - t0, 2)

t0 = time.time()
q2 = quiz_multi(TEST_TEXT)
t4 = round(time.time() - t0, 2)

print(f"方案一（单轮直接生成）：")
print(f"  耗时：{t3}s | 题目数：{len(q1)} | API调用：1次")

print(f"\n方案二（多轮分步迭代）：")
print(f"  耗时：{t4}s | 题目数：{len(q2)} | API调用：3次")

# 汇总表
print("\n\n" + "=" * 60)
print("数据汇总")
print("=" * 60)
print(f"{'指标':20} {'方案一(单轮)':15} {'方案二(多轮)':15}")
print(f"{'摘要字数':20} {len(r1):<15} {len(r2):<15}")
print(f"{'摘要耗时':20} {t1:<14.1f}s {t2:<14.1f}s")
print(f"{'选择题数量':20} {len(q1):<15} {len(q2):<15}")
print(f"{'选择题耗时':20} {t3:<14.1f}s {t4:<14.1f}s")
print(f"{'API总调用次数':20} {'1+1=2':15} {'3+3=6':15}")
print(f"{'总耗时':20} {t1+t3:<14.1f}s {t2+t4:<14.1f}s")
print()

print("人工评分表（请在报告中填写，满分10分/项）")
print("-" * 60)
for t in ["摘要-准确性", "摘要-可读性", "摘要-字数控制", "选择题-覆盖度", "选择题-解析质量", "选择题-格式规范"]:
    print(f"  {t}:  方案一 __/10  方案二 __/10")
