"""
Agent：受控的行為選擇

學習目標：
1. 理解 Agent 的概念
2. 建立基本 Agent
3. Agent 執行流程
4. 控制 Agent 行為
"""

import os
from dotenv import load_dotenv

load_dotenv()


def check_api_key():
    if not os.getenv("OPENAI_API_KEY"):
        return False
    return True


def demo_agent_concept():
    """Agent 概念"""
    print("=== Agent 概念 ===\n")

    print("""
# Agent = LLM + Tools + 決策循環

Chain vs Agent:
- Chain: 固定流程，A → B → C
- Agent: 動態決策，LLM 決定下一步

Agent 的運作：
1. 接收用戶輸入
2. LLM 決定要使用哪個 Tool（或直接回答）
3. 執行 Tool，取得結果
4. LLM 根據結果決定下一步
5. 重複直到 LLM 決定可以回答

什麼時候用 Agent？
- 需要多步驟推理
- 不確定需要哪些資訊
- 需要根據中間結果調整策略
""")


def demo_basic_agent():
    """基本 Agent"""
    print("\n=== 基本 Agent ===\n")

    print("""
# 使用 create_tool_calling_agent 建立 Agent

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor

# 1. 準備 LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. 準備 Tools
tools = [get_violation_count, lookup_regulation, send_alert]

# 3. 準備 Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是工安監控系統的 AI 助手。使用提供的工具來回答問題。"),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),  # Agent 思考過程
])

# 4. 建立 Agent
agent = create_tool_calling_agent(llm, tools, prompt)

# 5. 建立 Executor（執行器）
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # 顯示執行過程
)

# 6. 執行
result = executor.invoke({"input": "施工區今天有多少違規？相關法規是什麼？"})
print(result["output"])
""")

    if check_api_key():
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain.agents import create_tool_calling_agent, AgentExecutor
        from langchain_core.tools import tool

        # 定義簡單 Tools
        @tool
        def get_violation_count(zone: str = "all") -> dict:
            """取得違規數量"""
            return {"zone": zone, "count": 5}

        @tool
        def lookup_law(violation_type: str) -> str:
            """查詢法規"""
            laws = {"no_helmet": "職安法第281條"}
            return laws.get(violation_type, "未知法規")

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        tools = [get_violation_count, lookup_law]

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是工安助手，使用工具回答問題，用繁體中文回答。"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(llm, tools, prompt)
        executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        print("執行 Agent...\n")
        result = executor.invoke({"input": "施工區有多少違規？"})
        print(f"\n最終回答: {result['output']}")


def demo_agent_control():
    """Agent 控制"""
    print("\n=== Agent 控制 ===\n")

    print("""
# 控制 Agent 的行為

# 1. 限制執行次數
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=5,  # 最多執行 5 次
    max_execution_time=30,  # 最多 30 秒
)

# 2. 錯誤處理
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,  # 自動處理解析錯誤
    # 或自訂處理
    handle_parsing_errors="請重新格式化你的回應",
)

# 3. 提前終止
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    early_stopping_method="generate",  # 達到限制時讓 LLM 生成回答
    # early_stopping_method="force"  # 直接停止
)

# 4. 回傳中間步驟
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    return_intermediate_steps=True,
)

result = executor.invoke({"input": "..."})
for step in result["intermediate_steps"]:
    action, observation = step
    print(f"Action: {action}")
    print(f"Observation: {observation}")
""")


def demo_agent_with_memory():
    """Agent 與記憶"""
    print("\n=== Agent 與記憶 ===\n")

    print("""
# Agent 可以保持對話歷史

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 建立記憶存儲
memory_store = {}

def get_session_history(session_id: str):
    if session_id not in memory_store:
        memory_store[session_id] = InMemoryChatMessageHistory()
    return memory_store[session_id]

# 包裝 Agent
agent_with_memory = RunnableWithMessageHistory(
    executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# 對話
config = {"configurable": {"session_id": "user_001"}}

result1 = agent_with_memory.invoke(
    {"input": "施工區有多少違規？"},
    config=config
)

result2 = agent_with_memory.invoke(
    {"input": "那辦公區呢？"},  # Agent 會記得上下文
    config=config
)
""")


def demo_react_agent():
    """ReAct Agent"""
    print("\n=== ReAct Agent ===\n")

    print("""
# ReAct = Reasoning + Acting

# ReAct 模式讓 Agent 明確展示思考過程：
# Thought: 我需要查詢今日違規數量
# Action: get_violation_count
# Action Input: {"zone": "construction"}
# Observation: {"count": 5}
# Thought: 我現在知道施工區有 5 個違規，需要查詢相關法規
# Action: lookup_regulation
# ...

from langchain.agents import create_react_agent
from langchain import hub

# 使用標準 ReAct prompt
prompt = hub.pull("hwchase17/react")

# 或自訂
react_prompt = '''你是工安系統助手。

可用工具：
{tools}

工具名稱：{tool_names}

使用以下格式：

Question: 用戶的問題
Thought: 思考要做什麼
Action: 工具名稱
Action Input: 工具參數
Observation: 工具回傳結果
... (重複 Thought/Action/Observation)
Thought: 我現在知道最終答案了
Final Answer: 對用戶問題的回答

開始！

Question: {input}
Thought: {agent_scratchpad}'''

agent = create_react_agent(llm, tools, prompt)
""")


def demo_structured_chat_agent():
    """Structured Chat Agent"""
    print("\n=== Structured Chat Agent ===\n")

    print("""
# 適合複雜參數的 Agent

from langchain.agents import create_structured_chat_agent

# 當 Tool 有複雜參數時使用
complex_tool_schema = {
    "type": "object",
    "properties": {
        "zone": {"type": "string"},
        "severity": {"type": "string", "enum": ["high", "medium", "low"]},
        "date_range": {
            "type": "object",
            "properties": {
                "start": {"type": "string"},
                "end": {"type": "string"}
            }
        }
    }
}

agent = create_structured_chat_agent(llm, tools, prompt)
""")


def demo_agent_best_practices():
    """Agent 最佳實踐"""
    print("\n=== Agent 最佳實踐 ===\n")

    print("""
# 1. 限制工具數量
#    - 太多工具會讓 LLM 困惑
#    - 建議 3-7 個核心工具

# 2. 清晰的工具描述
@tool
def get_violations():
    '''取得違規記錄

    使用時機：當用戶詢問違規數量、違規列表時
    不要使用：當用戶詢問法規內容時
    '''
    ...

# 3. 適當的錯誤處理
@tool(handle_tool_error=True)
def risky_tool():
    '''可能失敗的操作'''
    ...

# 4. 設定合理的限制
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=10,
    max_execution_time=60,
)

# 5. 監控和日誌
from langchain.callbacks import StdOutCallbackHandler

executor.invoke(
    {"input": "..."},
    config={"callbacks": [StdOutCallbackHandler()]}
)

# 6. 使用 verbose 模式 debug
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 7. 考慮是否真的需要 Agent
#    - 固定流程用 Chain
#    - 需要動態決策才用 Agent
""")


# === 主程式 ===
if __name__ == "__main__":
    print("=" * 50)
    print("Agent：受控的行為選擇")
    print("=" * 50)
    print()

    demo_agent_concept()
    demo_basic_agent()
    demo_agent_control()
    demo_agent_with_memory()
    demo_react_agent()
    demo_structured_chat_agent()
    demo_agent_best_practices()

    print("\n完成！")
