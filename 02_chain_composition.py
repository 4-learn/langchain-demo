"""
Demo：Chain 的組合 — 多步驟處理

對應講義：LangChain → Chain 的組合：多步驟處理

執行方式：
  python 02_chain_composition.py

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
    print("  Chain 的組合：多步驟處理")
    print("=" * 50)

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    # 步驟 1：分析違規嚴重程度
    analyze_prompt = ChatPromptTemplate.from_messages([
        ("system", "分析違規事件的嚴重程度，回答：低/中/高"),
        ("human", "違規事件：{violation}")
    ])
    analyze_chain = analyze_prompt | llm | StrOutputParser()

    # 步驟 2：生成告警訊息
    alert_prompt = ChatPromptTemplate.from_messages([
        ("system", "根據違規分析結果，生成簡短的告警訊息"),
        ("human", "違規：{violation}\n嚴重程度：{severity}")
    ])
    alert_chain = alert_prompt | llm | StrOutputParser()

    # 測試
    violations = [
        "A區工人未配戴安全帽",
        "通道堆放雜物",
        "員工在禁煙區抽煙",
    ]

    for v in violations:
        print(f"\n{'─' * 50}")
        print(f"違規：{v}")

        # 先分析嚴重程度
        severity = analyze_chain.invoke({"violation": v})
        print(f"嚴重程度：{severity}")

        # 再生成告警
        alert = alert_chain.invoke({"violation": v, "severity": severity})
        print(f"告警訊息：{alert[:150]}")


if __name__ == "__main__":
    main()
