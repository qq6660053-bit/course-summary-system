from openai import OpenAI        # 导入OpenAI兼容接口客户端，通用于阿里云通义千问兼容模式、OpenAI原生接口
# 初始化大模型客户端对象
client = OpenAI(
    api_key="你的API-KEY",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"                 # 接口基础地址
)
# 全局常量，指定项目统一使用的大模型名称：通义千问plus
MODEL = "qwen-plus"
