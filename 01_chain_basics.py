"""
Demo：第一個 Chain — 問答機器人

對應講義：LangChain → 第一個 Chain：問答機器人

執行方式：
  python 01_chain_basics.py

需要：
  pip install langchain langchain-google-genai python-dotenv
  .env 裡設定 GOOGLE_API_KEY
"""

import os
from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def main():
    print("=" * 50)
    print("  第一個 Chain：問答機器人")
    print("=" * 50)

    # 1. 建立 Prompt 模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是工安專家，專門回答職業安全相關問題。"),
        ("human", "{question}")
    ])

    # 2. 建立 LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    # 3. 建立 Parser
    parser = StrOutputParser()

    # 4. 組合成 Chain（用 | 串接）
    chain = prompt | llm | parser

    # 5. 測試
    questions = [
        "什麼是 PPE？",
        "高空作業需要什麼防護？",
        "工地噪音超標怎麼處理？",
    ]

    for q in questions:
        print(f"\n問：{q}")
        result = chain.invoke({"question": q})
        print(f"答：{result[:200]}...")


if __name__ == "__main__":
    main()
