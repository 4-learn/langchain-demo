"""
工安系統 Chain 範例

學習目標：
1. 整合 Chain、Tool、Agent
2. 建立工安分析系統
3. 系統設計模式
"""

import os
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def check_api_key():
    if not os.getenv("OPENAI_API_KEY"):
        return False
    return True


# === 資料結構 ===

@dataclass
class ViolationEvent:
    """違規事件"""
    id: str
    timestamp: datetime
    zone: str
    violation_type: str
    confidence: float
    severity: str


# === 模擬資料庫 ===

class SafetyDatabase:
    """模擬資料庫"""

    def __init__(self):
        self.violations = [
            ViolationEvent("V001", datetime.now(timezone.utc), "construction", "no_helmet", 0.92, "high"),
            ViolationEvent("V002", datetime.now(timezone.utc), "entrance", "no_vest", 0.78, "medium"),
            ViolationEvent("V003", datetime.now(timezone.utc), "construction", "no_helmet", 0.85, "high"),
            ViolationEvent("V004", datetime.now(timezone.utc), "office", "blocked_exit", 0.65, "medium"),
        ]

        self.regulations = {
            "no_helmet": {
                "title": "職業安全衛生設施規則 第 281 條",
                "content": "雇主對於在高度二公尺以上之處所作業，勞工有墜落之虞者，應使勞工確實使用安全帽。"
            },
            "no_vest": {
                "title": "職業安全衛生設施規則 第 277 條",
                "content": "雇主對於有車輛出入之場所，應設置反光標誌或使勞工穿著反光衣著。"
            },
            "no_safety_belt": {
                "title": "職業安全衛生設施規則 第 225 條",
                "content": "雇主對於在高度二公尺以上之處所作業，應使勞工確實使用安全帶。"
            },
            "blocked_exit": {
                "title": "職業安全衛生設施規則 第 33 條",
                "content": "緊急出口及通道應保持暢通，不得堆積物品。"
            }
        }

    def get_violations(self, zone: Optional[str] = None, severity: Optional[str] = None) -> list:
        """查詢違規"""
        result = self.violations
        if zone:
            result = [v for v in result if v.zone == zone]
        if severity:
            result = [v for v in result if v.severity == severity]
        return result

    def get_stats(self) -> dict:
        """取得統計"""
        by_zone = {}
        by_type = {}
        for v in self.violations:
            by_zone[v.zone] = by_zone.get(v.zone, 0) + 1
            by_type[v.violation_type] = by_type.get(v.violation_type, 0) + 1
        return {
            "total": len(self.violations),
            "by_zone": by_zone,
            "by_type": by_type
        }

    def get_regulation(self, violation_type: str) -> Optional[dict]:
        """查詢法規"""
        return self.regulations.get(violation_type)


# === 定義 Tools ===

def create_safety_tools(db: SafetyDatabase):
    """建立工安相關 Tools"""
    from langchain_core.tools import tool

    @tool
    def query_violations(zone: Optional[str] = None, severity: Optional[str] = None) -> str:
        """查詢違規記錄

        Args:
            zone: 區域篩選（construction, office, entrance）
            severity: 嚴重程度篩選（high, medium, low）
        """
        violations = db.get_violations(zone, severity)
        if not violations:
            return "沒有找到符合條件的違規記錄"

        result = []
        for v in violations:
            result.append(f"- [{v.id}] {v.zone}: {v.violation_type} ({v.severity})")
        return "\n".join(result)

    @tool
    def get_statistics() -> str:
        """取得違規統計摘要"""
        stats = db.get_stats()
        lines = [
            f"總違規數: {stats['total']}",
            "依區域:",
        ]
        for zone, count in stats["by_zone"].items():
            lines.append(f"  - {zone}: {count}")
        lines.append("依類型:")
        for vtype, count in stats["by_type"].items():
            lines.append(f"  - {vtype}: {count}")
        return "\n".join(lines)

    @tool
    def lookup_regulation(violation_type: str) -> str:
        """查詢違規類型對應的法規

        Args:
            violation_type: 違規類型（no_helmet, no_vest, no_safety_belt, blocked_exit）
        """
        reg = db.get_regulation(violation_type)
        if not reg:
            return f"找不到 {violation_type} 對應的法規"
        return f"{reg['title']}\n\n{reg['content']}"

    @tool
    def send_alert(message: str, priority: str = "normal") -> str:
        """發送告警通知

        Args:
            message: 告警訊息內容
            priority: 優先級（urgent, normal）
        """
        # 模擬發送
        return f"已發送 {priority} 告警: {message[:50]}..."

    return [query_violations, get_statistics, lookup_regulation, send_alert]


# === 建立 Agent ===

def create_safety_agent():
    """建立工安助手 Agent"""

    if not check_api_key():
        print("需要設定 OPENAI_API_KEY")
        return None

    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.agents import create_tool_calling_agent, AgentExecutor

    # 資料庫
    db = SafetyDatabase()

    # LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Tools
    tools = create_safety_tools(db)

    # Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是工安監控系統的 AI 助手。

你的職責：
1. 回答關於違規記錄的查詢
2. 提供違規統計分析
3. 查詢相關法規
4. 需要時發送告警

回答時：
- 使用繁體中文
- 提供具體數據
- 引用相關法規
- 給出明確建議"""),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    # 建立 Agent
    agent = create_tool_calling_agent(llm, tools, prompt)

    # 建立 Executor
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
    )

    return executor


# === Chain 版本（固定流程）===

def create_safety_chain():
    """建立工安分析 Chain（固定流程）"""

    if not check_api_key():
        print("需要設定 OPENAI_API_KEY")
        return None

    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.runnables import RunnablePassthrough, RunnableLambda
    from pydantic import BaseModel, Field

    # 輸出結構
    class ViolationAnalysis(BaseModel):
        summary: str = Field(description="違規摘要")
        severity_assessment: str = Field(description="嚴重程度評估")
        recommended_actions: list = Field(description="建議行動")
        relevant_regulations: list = Field(description="相關法規")

    db = SafetyDatabase()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    parser = JsonOutputParser(pydantic_object=ViolationAnalysis)

    # Step 1: 取得資料
    def get_context(input_dict):
        stats = db.get_stats()
        violations = db.get_violations()
        return {
            "question": input_dict["question"],
            "stats": str(stats),
            "violations": str([f"{v.zone}:{v.violation_type}" for v in violations]),
        }

    # Step 2: 分析
    analysis_prompt = ChatPromptTemplate.from_template("""
根據以下工安資料回答問題。

統計資料：
{stats}

違規列表：
{violations}

問題：{question}

{format_instructions}
""")

    # 組合 Chain
    chain = (
        RunnableLambda(get_context)
        | analysis_prompt.partial(format_instructions=parser.get_format_instructions())
        | llm
        | parser
    )

    return chain


# === 展示 ===

def demo_tools():
    """展示 Tools"""
    print("=== 工安系統 Tools ===\n")

    db = SafetyDatabase()
    tools = create_safety_tools(db)

    print("定義的 Tools:")
    for t in tools:
        print(f"  - {t.name}: {t.description[:40]}...")

    print("\n測試 Tools:")

    # query_violations
    result = tools[0].invoke({"zone": "construction"})
    print(f"\nquery_violations(zone='construction'):")
    print(result)

    # get_statistics
    result = tools[1].invoke({})
    print(f"\nget_statistics():")
    print(result)

    # lookup_regulation
    result = tools[2].invoke({"violation_type": "no_helmet"})
    print(f"\nlookup_regulation('no_helmet'):")
    print(result)


def demo_agent():
    """展示 Agent"""
    print("\n=== 工安助手 Agent ===\n")

    agent = create_safety_agent()
    if not agent:
        return

    # 測試對話
    questions = [
        "施工區有哪些違規？",
        "未戴安全帽違反什麼法規？",
        "給我一個今日違規的摘要報告",
    ]

    for q in questions:
        print(f"\n問: {q}")
        result = agent.invoke({"input": q})
        print(f"答: {result['output']}")


def demo_chain():
    """展示 Chain"""
    print("\n=== 工安分析 Chain ===\n")

    chain = create_safety_chain()
    if not chain:
        return

    result = chain.invoke({"question": "今天的違規狀況如何？有什麼建議？"})
    print("Chain 分析結果:")
    print(f"  摘要: {result['summary']}")
    print(f"  嚴重程度: {result['severity_assessment']}")
    print(f"  建議: {result['recommended_actions']}")
    print(f"  法規: {result['relevant_regulations']}")


# === 主程式 ===

def main():
    print("=" * 50)
    print("工安系統 LangChain 整合範例")
    print("=" * 50)
    print()

    # 1. 展示 Tools（不需 API Key）
    demo_tools()

    # 2. 展示 Agent（需要 API Key）
    if check_api_key():
        print("\n" + "=" * 50)
        demo_agent()

        print("\n" + "=" * 50)
        demo_chain()
    else:
        print("\n提示：設定 OPENAI_API_KEY 可測試 Agent 和 Chain")

    print("\n完成！")


if __name__ == "__main__":
    main()
