"""
Demo：OpenAI × LangChain — 一行換模型

對應講義：OpenAI × LangChain

執行方式：
  python openai_langchain.py

需要：
  pip install langchain langchain-google-genai langchain-openai python-dotenv
  .env 裡設定 GOOGLE_API_KEY 和 OPENAI_API_KEY
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def main():
    print("=" * 55)
    print("  OpenAI × LangChain：一行換模型")
    print("=" * 55)

    # 共用的 Prompt 和 Parser
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是工安專家。分析違規事件，回答嚴重程度和建議。用繁體中文，簡短回答。"),
        ("human", "{violation}")
    ])
    parser = StrOutputParser()

    # 兩個 LLM，只差一行
    gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    openai_llm = ChatOpenAI(model="gpt-4o-mini")

    # 同一個 Chain 結構，不同 LLM
    gemini_chain = prompt | gemini | parser
    openai_chain = prompt | openai_llm | parser

    # 測試
    violations = [
        "工人沒戴安全帽",
        "高空作業未繫安全帶",
        "通道堆放雜物",
    ]

    for v in violations:
        print(f"\n{'─' * 55}")
        print(f"  違規：{v}")
        print(f"{'─' * 55}")

        # Gemini
        t0 = time.time()
        gemini_result = gemini_chain.invoke({"violation": v})
        gemini_time = time.time() - t0
        print(f"\n  Gemini ({gemini_time:.2f}s)：{gemini_result[:100]}")

        # OpenAI
        t0 = time.time()
        openai_result = openai_chain.invoke({"violation": v})
        openai_time = time.time() - t0
        print(f"  OpenAI ({openai_time:.2f}s)：{openai_result[:100]}")


if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("錯誤：請在 .env 設定 GOOGLE_API_KEY")
        exit(1)
    if not os.getenv("OPENAI_API_KEY"):
        print("錯誤：請在 .env 設定 OPENAI_API_KEY")
        exit(1)

    main()
