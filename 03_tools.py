"""
Demo：Tool — LLM 與系統的邊界

對應講義：Tool：LLM 與系統的邊界

執行方式：
  python 03_tools.py

需要：
  pip install langchain langchain-google-genai python-dotenv
  .env 裡設定 GOOGLE_API_KEY
"""

from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool


# === 定義 Tool ===

@tool
def search_regulation(keyword: str) -> str:
    """搜尋工安法規

    Args:
        keyword: 搜尋關鍵字，例如「安全帽」「反光背心」
    """
    regulations = {
        "安全帽": "職安法第 281 條：雇主應使勞工確實使用安全帽。",
        "反光背心": "職安法第 21 條：雇主應提供反光背心。",
        "安全帶": "職安法第 225 條：高空作業應使用安全帶。",
    }
    result = regulations.get(keyword, f"找不到「{keyword}」相關法規")
    print(f"  [Tool] search_regulation({keyword}) → {result}")
    return result


@tool
def send_alert(message: str, level: str) -> str:
    """發送告警通知

    Args:
        message: 告警訊息
        level: 嚴重等級 (low/medium/high)
    """
    print(f"  [Tool] send_alert({level}) → {message}")
    return f"告警已發送：[{level.upper()}] {message}"


@tool
def log_violation(description: str, location: str) -> str:
    """記錄違規事件

    Args:
        description: 違規描述
        location: 發生地點
    """
    print(f"  [Tool] log_violation → {location}: {description}")
    return f"已記錄：{location} - {description}"


# === Demo 1：bind_tools（手動兩段式） ===

def demo_bind_tools():
    print("=" * 50)
    print("  Demo 1：bind_tools（LLM 選 Tool）")
    print("=" * 50)

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    llm_with_tools = llm.bind_tools([search_regulation, send_alert, log_violation])

    # 第一段：LLM 選擇要呼叫哪個 Tool
    response = llm_with_tools.invoke("幫我查安全帽的法規")

    print(f"\n  LLM 選擇的 Tool：")
    for tc in response.tool_calls:
        print(f"    {tc['name']}({tc['args']})")

    # 第二段：你手動執行
    if response.tool_calls:
        tc = response.tool_calls[0]
        tool_map = {
            "search_regulation": search_regulation,
            "send_alert": send_alert,
            "log_violation": log_violation,
        }
        result = tool_map[tc["name"]].invoke(tc["args"])
        print(f"\n  執行結果：{result}")


# === Demo 2：create_agent（自動執行） ===

def demo_agent():
    print(f"\n{'=' * 50}")
    print("  Demo 2：create_agent（自動執行 Tool）")
    print("=" * 50)

    from langchain.agents import create_agent

    tools = [search_regulation, send_alert, log_violation]

    agent = create_agent(
        "google_genai:gemini-2.5-flash",
        tools=tools,
        system_prompt="你是工安助手，可以查詢法規、發送告警、記錄違規。用繁體中文回答。",
    )

    instructions = [
        "幫我查安全帽的法規",
        "A區有人沒戴安全帽，發一個 high 告警",
    ]

    for instruction in instructions:
        print(f"\n  指令：{instruction}")
        result = agent.invoke({"messages": [{"role": "user", "content": instruction}]})
        # 取最後一條 AI 訊息
        last_msg = result["messages"][-1]
        print(f"  回答：{last_msg.content[:150]}")


if __name__ == "__main__":
    demo_bind_tools()
    demo_agent()
