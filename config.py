import os
from openai import OpenAI

# API Key：优先从环境变量读取，本地运行时填入下方
api_key = os.environ.get("DASHSCOPE_API_KEY", "你的API-KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
# 全局常量，指定项目统一使用的大模型名称：通义千问plus
MODEL = "qwen-plus"
