"""
Demo：with_fallbacks — 主模型失敗自動換備用

對應講義：LangChain → 中間失敗怎麼辦？

執行方式：
  python 03_fallbacks.py

需要：
  pip install langchain langchain-google-genai python-dotenv
  .env 裡設定 GOOGLE_API_KEY
"""

from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def main():
    print("=" * 50)
    print("  with_fallbacks：自動換備用模型")
    print("=" * 50)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是工安專家，用一句話回答。"),
        ("human", "{question}")
    ])
    parser = StrOutputParser()

    # Demo 1：沒有 fallback（模型名稱故意寫錯，會失敗）
    print("\n--- Demo 1：沒有 fallback ---")

    bad_llm = ChatGoogleGenerativeAI(model="gemini-0.0-不存在")
    bad_chain = prompt | bad_llm | parser

    try:
        result = bad_chain.invoke({"question": "什麼是 PPE？"})
        print(f"  回答：{result}")
    except Exception as e:
        print(f"  ❌ 失敗：{type(e).__name__}")

    # Demo 2：有 fallback（失敗自動換備用）
    print("\n--- Demo 2：有 fallback ---")

    main_llm = ChatGoogleGenerativeAI(model="gemini-0.0-不存在")  # 故意用壞的
    backup_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")  # 備用
    safe_llm = main_llm.with_fallbacks([backup_llm])

    safe_chain = prompt | safe_llm | parser

    result = safe_chain.invoke({"question": "什麼是 PPE？"})
    print(f"  ✅ 回答：{result[:100]}")
    print(f"  （主模型失敗，自動換成 gemini-2.5-flash）")

    # Demo 3：實務用法（便宜的當主力，貴的當 fallback）
    print("\n--- Demo 3：實務用法 ---")

    cheap_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")   # 便宜
    strong_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")  # 貴但強
    smart_llm = cheap_llm.with_fallbacks([strong_llm])

    smart_chain = prompt | smart_llm | parser

    result = smart_chain.invoke({"question": "高空作業需要什麼防護？"})
    print(f"  回答：{result[:100]}")
    print(f"  （平常用便宜的 gemini-2.0-flash，失敗才換 gemini-2.5-flash）")


if __name__ == "__main__":
    main()
