"""
Chain 組合：Sequential, Parallel, Branching

學習目標：
1. 串接多個 Chain
2. 並行處理
3. 條件分支
4. 錯誤處理
"""

import os
from dotenv import load_dotenv

load_dotenv()


def check_api_key():
    if not os.getenv("OPENAI_API_KEY"):
        return False
    return True


def demo_sequential_chain():
    """串接 Chain"""
    print("=== Sequential Chain ===\n")

    print("""
# 串接多個處理步驟

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini")

# Chain 1: 分析違規
analyze_prompt = ChatPromptTemplate.from_template(
    "分析這個工安違規：{violation}"
)
analyze_chain = analyze_prompt | llm | StrOutputParser()

# Chain 2: 產生建議
suggest_prompt = ChatPromptTemplate.from_template(
    "根據以下分析，給出具體的改善建議：\\n{analysis}"
)
suggest_chain = suggest_prompt | llm | StrOutputParser()

# 串接（前一個的輸出變成後一個的輸入）
from langchain_core.runnables import RunnablePassthrough

full_chain = (
    {"analysis": analyze_chain}
    | suggest_chain
)

result = full_chain.invoke({"violation": "施工區未戴安全帽"})
""")

    if check_api_key():
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        analyze_prompt = ChatPromptTemplate.from_template(
            "用一句話分析這個工安違規：{violation}"
        )
        analyze_chain = analyze_prompt | llm | StrOutputParser()

        suggest_prompt = ChatPromptTemplate.from_template(
            "根據以下分析，用一句話給出改善建議：\n{analysis}"
        )
        suggest_chain = suggest_prompt | llm | StrOutputParser()

        full_chain = {"analysis": analyze_chain} | suggest_chain

        result = full_chain.invoke({"violation": "施工區未戴安全帽"})
        print(f"結果: {result}")


def demo_parallel_chain():
    """並行 Chain"""
    print("\n=== Parallel Chain ===\n")

    print("""
# 同時執行多個 Chain

from langchain_core.runnables import RunnableParallel

# 定義多個 Chain
severity_chain = severity_prompt | llm | StrOutputParser()
category_chain = category_prompt | llm | StrOutputParser()
action_chain = action_prompt | llm | StrOutputParser()

# 並行執行
parallel_chain = RunnableParallel(
    severity=severity_chain,
    category=category_chain,
    action=action_chain
)

result = parallel_chain.invoke({"violation": "..."})
# result = {
#     "severity": "high",
#     "category": "PPE",
#     "action": "立即處理"
# }
""")

    if check_api_key():
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnableParallel

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        severity_prompt = ChatPromptTemplate.from_template(
            "判斷這個違規的嚴重程度（回答 high/medium/low）：{violation}"
        )
        category_prompt = ChatPromptTemplate.from_template(
            "這個違規屬於哪個類別（回答 PPE/環境/設備）：{violation}"
        )

        parallel = RunnableParallel(
            severity=severity_prompt | llm | StrOutputParser(),
            category=category_prompt | llm | StrOutputParser(),
        )

        result = parallel.invoke({"violation": "高空作業未繫安全帶"})
        print(f"並行結果: {result}")


def demo_branching():
    """條件分支"""
    print("\n=== Branching ===\n")

    print("""
# 根據條件選擇不同的 Chain

from langchain_core.runnables import RunnableBranch

# 定義不同處理路徑
high_priority_chain = high_prompt | llm | StrOutputParser()
medium_priority_chain = medium_prompt | llm | StrOutputParser()
low_priority_chain = low_prompt | llm | StrOutputParser()

# 建立分支
branch = RunnableBranch(
    # (條件, 對應的 Chain)
    (lambda x: x.get("severity") == "high", high_priority_chain),
    (lambda x: x.get("severity") == "medium", medium_priority_chain),
    low_priority_chain  # 預設（最後一個沒有條件）
)

# 完整流程
full_chain = (
    classify_chain  # 先分類
    | branch        # 再分支處理
)
""")


def demo_passthrough():
    """保留原始輸入"""
    print("\n=== RunnablePassthrough ===\n")

    print("""
# 保留原始輸入，同時執行其他處理

from langchain_core.runnables import RunnablePassthrough

chain = (
    {
        "original": RunnablePassthrough(),  # 保留原始輸入
        "analysis": analyze_chain,           # 同時分析
    }
    | combine_chain  # 結合使用
)

result = chain.invoke({"violation": "..."})
# result["original"] = {"violation": "..."}（原始輸入）
# result["analysis"] = "..."（分析結果）
""")


def demo_with_config():
    """Chain 配置"""
    print("\n=== Chain 配置 ===\n")

    print("""
# 動態配置 Chain

from langchain_core.runnables import RunnableConfig

# 執行時配置
result = chain.invoke(
    {"violation": "..."},
    config=RunnableConfig(
        tags=["safety-analysis"],
        metadata={"source": "camera_01"},
        max_concurrency=5,  # 並行限制
    )
)

# Callback 處理
from langchain_core.callbacks import BaseCallbackHandler

class LoggingHandler(BaseCallbackHandler):
    def on_chain_start(self, serialized, inputs, **kwargs):
        print(f"Chain 開始: {inputs}")

    def on_chain_end(self, outputs, **kwargs):
        print(f"Chain 結束: {outputs}")

result = chain.invoke(
    {"violation": "..."},
    config={"callbacks": [LoggingHandler()]}
)
""")


def demo_error_handling():
    """錯誤處理"""
    print("\n=== 錯誤處理 ===\n")

    print("""
# 使用 with_fallbacks 處理錯誤

from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama

# 主要模型
main_llm = ChatOpenAI(model="gpt-4o-mini")

# 備用模型
fallback_llm = Ollama(model="llama3.2")

# 設定 fallback
robust_llm = main_llm.with_fallbacks([fallback_llm])

chain = prompt | robust_llm | parser

# 使用 with_retry 重試
from langchain_core.runnables import RunnableRetry

retry_chain = chain.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)

# 自訂錯誤處理
def safe_invoke(chain, input_data):
    try:
        return chain.invoke(input_data)
    except Exception as e:
        return {
            "error": str(e),
            "fallback": "無法分析，請人工處理"
        }
""")


def demo_batch_processing():
    """批次處理"""
    print("\n=== 批次處理 ===\n")

    print("""
# 批次處理多個輸入

violations = [
    {"violation": "未戴安全帽"},
    {"violation": "未穿反光背心"},
    {"violation": "高空作業無防護"},
]

# 批次執行
results = chain.batch(violations)

# 帶配置的批次
results = chain.batch(
    violations,
    config={"max_concurrency": 3}  # 最多 3 個同時執行
)

# 批次串流
for result in chain.batch_as_completed(violations):
    print(f"完成: {result}")
""")


def demo_streaming():
    """串流輸出"""
    print("\n=== 串流輸出 ===\n")

    print("""
# 即時輸出生成結果

# 基本串流
for chunk in chain.stream({"violation": "..."}):
    print(chunk, end="", flush=True)

# 串流事件（更詳細）
async for event in chain.astream_events({"violation": "..."}, version="v1"):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="")
    elif event["event"] == "on_chain_end":
        print(f"\\n完成: {event['data']['output']}")
""")


# === 主程式 ===
if __name__ == "__main__":
    print("=" * 50)
    print("Chain 組合")
    print("=" * 50)
    print()

    demo_sequential_chain()
    demo_parallel_chain()
    demo_branching()
    demo_passthrough()
    demo_with_config()
    demo_error_handling()
    demo_batch_processing()
    demo_streaming()

    print("\n完成！")
