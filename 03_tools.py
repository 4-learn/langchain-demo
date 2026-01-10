"""
Tool：LLM 與系統的邊界

學習目標：
1. 理解 Tool 的概念
2. 定義自訂 Tool
3. Tool 輸入驗證
4. Tool 與系統整合
"""

import os
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def check_api_key():
    if not os.getenv("OPENAI_API_KEY"):
        return False
    return True


def demo_tool_concept():
    """Tool 概念"""
    print("=== Tool 概念 ===\n")

    print("""
# Tool 是 LLM 與外部世界的橋樑

為什麼需要 Tool？
- LLM 不知道「現在」的資訊 → 用 Tool 查詢資料庫
- LLM 數學計算可能出錯 → 用 Tool 呼叫計算器
- LLM 無法執行動作 → 用 Tool 發送通知

Tool 的組成：
- name: 工具名稱（LLM 會用這個名稱來選擇）
- description: 工具描述（LLM 根據這個決定何時使用）
- args_schema: 參數定義（告訴 LLM 要傳什麼參數）
- func: 實際執行的函數
""")


def demo_basic_tool():
    """基本 Tool 定義"""
    print("\n=== 基本 Tool 定義 ===\n")

    print("""
# 方法 1: 使用 @tool 裝飾器（最簡單）

from langchain_core.tools import tool

@tool
def get_violation_count(zone: str) -> int:
    '''取得指定區域的違規數量

    Args:
        zone: 區域名稱（construction, office, entrance）

    Returns:
        該區域的違規數量
    '''
    # 模擬查詢資料庫
    data = {"construction": 15, "office": 3, "entrance": 7}
    return data.get(zone, 0)

# 查看 Tool 資訊
print(get_violation_count.name)  # "get_violation_count"
print(get_violation_count.description)  # docstring 內容
print(get_violation_count.args_schema.schema())  # 參數 schema

# 直接呼叫
result = get_violation_count.invoke({"zone": "construction"})
print(result)  # 15
""")

    from langchain_core.tools import tool

    @tool
    def get_violation_count(zone: str) -> int:
        """取得指定區域的違規數量"""
        data = {"construction": 15, "office": 3, "entrance": 7}
        return data.get(zone, 0)

    print(f"Tool 名稱: {get_violation_count.name}")
    print(f"Tool 描述: {get_violation_count.description}")
    result = get_violation_count.invoke({"zone": "construction"})
    print(f"執行結果: {result}")


def demo_structured_tool():
    """結構化 Tool"""
    print("\n=== 結構化 Tool（StructuredTool）===\n")

    print("""
# 方法 2: 使用 StructuredTool（更多控制）

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

# 定義輸入 Schema
class ViolationQueryInput(BaseModel):
    zone: str = Field(description="區域名稱")
    start_date: str = Field(description="開始日期 (YYYY-MM-DD)")
    end_date: str = Field(description="結束日期 (YYYY-MM-DD)")
    severity: str = Field(default="all", description="嚴重程度篩選")

# 定義函數
def query_violations(zone: str, start_date: str, end_date: str, severity: str = "all") -> dict:
    '''查詢違規記錄'''
    # 模擬查詢
    return {
        "zone": zone,
        "count": 10,
        "period": f"{start_date} to {end_date}",
        "severity_filter": severity
    }

# 建立 Tool
violation_query_tool = StructuredTool.from_function(
    func=query_violations,
    name="violation_query",
    description="查詢指定區域和時間範圍的違規記錄",
    args_schema=ViolationQueryInput,
)
""")

    from langchain_core.tools import StructuredTool
    from pydantic import BaseModel, Field

    class ViolationQueryInput(BaseModel):
        zone: str = Field(description="區域名稱")
        severity: str = Field(default="all", description="嚴重程度")

    def query_violations(zone: str, severity: str = "all") -> dict:
        return {"zone": zone, "count": 10, "severity": severity}

    tool = StructuredTool.from_function(
        func=query_violations,
        name="violation_query",
        description="查詢違規記錄",
        args_schema=ViolationQueryInput,
    )

    print(f"Tool: {tool.name}")
    result = tool.invoke({"zone": "construction", "severity": "high"})
    print(f"結果: {result}")


def demo_tool_class():
    """Tool 類別"""
    print("\n=== Tool 類別（BaseTool）===\n")

    print("""
# 方法 3: 繼承 BaseTool（最大彈性）

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class SendAlertInput(BaseModel):
    message: str = Field(description="告警訊息")
    severity: str = Field(description="嚴重程度: high/medium/low")
    recipients: list[str] = Field(description="收件人列表")

class SendAlertTool(BaseTool):
    name: str = "send_alert"
    description: str = "發送告警通知給指定人員"
    args_schema: Type[BaseModel] = SendAlertInput

    # 可以加入狀態
    sent_count: int = 0

    def _run(self, message: str, severity: str, recipients: list[str]) -> str:
        '''同步執行'''
        self.sent_count += 1
        # 實際發送邏輯
        return f"已發送 {severity} 告警給 {len(recipients)} 人"

    async def _arun(self, message: str, severity: str, recipients: list[str]) -> str:
        '''非同步執行'''
        # 非同步發送邏輯
        return await self._async_send(message, severity, recipients)

# 使用
alert_tool = SendAlertTool()
result = alert_tool.invoke({
    "message": "施工區發現違規",
    "severity": "high",
    "recipients": ["supervisor@company.com"]
})
""")


def demo_tool_error_handling():
    """Tool 錯誤處理"""
    print("\n=== Tool 錯誤處理 ===\n")

    print("""
# Tool 應該優雅地處理錯誤

from langchain_core.tools import tool, ToolException

@tool(handle_tool_error=True)
def risky_operation(param: str) -> str:
    '''可能失敗的操作'''
    if not param:
        raise ToolException("參數不能為空")
    return f"成功: {param}"

# 或自訂錯誤處理
def custom_error_handler(error: ToolException) -> str:
    return f"操作失敗: {error}，請稍後重試"

@tool(handle_tool_error=custom_error_handler)
def another_risky_operation(param: str) -> str:
    '''另一個可能失敗的操作'''
    if param == "error":
        raise ToolException("測試錯誤")
    return f"成功: {param}"
""")


def demo_safety_tools():
    """工安系統 Tools"""
    print("\n=== 工安系統 Tools ===\n")

    from langchain_core.tools import tool
    from pydantic import BaseModel, Field

    # 模擬資料庫
    VIOLATION_DB = [
        {"id": 1, "zone": "construction", "type": "no_helmet", "severity": "high", "time": "09:30"},
        {"id": 2, "zone": "entrance", "type": "no_vest", "severity": "medium", "time": "10:15"},
        {"id": 3, "zone": "construction", "type": "no_helmet", "severity": "high", "time": "11:00"},
    ]

    LAW_DB = {
        "no_helmet": "職業安全衛生設施規則 第 281 條",
        "no_vest": "職業安全衛生設施規則 第 277 條",
        "no_safety_belt": "職業安全衛生設施規則 第 225 條",
    }

    @tool
    def get_today_violations(zone: Optional[str] = None) -> list:
        """取得今日違規記錄

        Args:
            zone: 區域篩選（可選）
        """
        if zone:
            return [v for v in VIOLATION_DB if v["zone"] == zone]
        return VIOLATION_DB

    @tool
    def get_violation_stats() -> dict:
        """取得違規統計"""
        stats = {}
        for v in VIOLATION_DB:
            vtype = v["type"]
            stats[vtype] = stats.get(vtype, 0) + 1
        return {
            "total": len(VIOLATION_DB),
            "by_type": stats
        }

    @tool
    def lookup_regulation(violation_type: str) -> str:
        """查詢違規類型對應的法規

        Args:
            violation_type: 違規類型 (no_helmet, no_vest, no_safety_belt)
        """
        return LAW_DB.get(violation_type, "未找到對應法規")

    @tool
    def send_notification(message: str, channel: str = "email") -> str:
        """發送通知

        Args:
            message: 通知內容
            channel: 通知管道 (email, sms, slack)
        """
        # 模擬發送
        return f"已透過 {channel} 發送通知: {message[:50]}..."

    # 展示 Tools
    tools = [get_today_violations, get_violation_stats, lookup_regulation, send_notification]

    print("定義的工安 Tools:")
    for t in tools:
        print(f"  - {t.name}: {t.description[:40]}...")

    # 測試
    print("\n測試 get_today_violations:")
    print(f"  {get_today_violations.invoke({'zone': 'construction'})}")

    print("\n測試 get_violation_stats:")
    print(f"  {get_violation_stats.invoke({})}")

    print("\n測試 lookup_regulation:")
    print(f"  {lookup_regulation.invoke({'violation_type': 'no_helmet'})}")


def demo_tool_binding():
    """Tool 綁定到 LLM"""
    print("\n=== Tool 綁定到 LLM ===\n")

    print("""
# 將 Tools 綁定到 LLM，讓 LLM 可以決定何時使用

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

# 綁定 Tools
tools = [get_today_violations, get_violation_stats, lookup_regulation]
llm_with_tools = llm.bind_tools(tools)

# 呼叫 LLM
response = llm_with_tools.invoke("今天有多少違規？")

# 檢查 LLM 是否決定使用 Tool
if response.tool_calls:
    for tool_call in response.tool_calls:
        print(f"LLM 決定呼叫: {tool_call['name']}")
        print(f"參數: {tool_call['args']}")
else:
    print(f"LLM 直接回答: {response.content}")
""")

    if check_api_key():
        from langchain_openai import ChatOpenAI
        from langchain_core.tools import tool

        @tool
        def get_violation_count() -> int:
            """取得今日違規總數"""
            return 15

        llm = ChatOpenAI(model="gpt-4o-mini")
        llm_with_tools = llm.bind_tools([get_violation_count])

        response = llm_with_tools.invoke("今天有多少違規？")

        if response.tool_calls:
            print("LLM 決定使用 Tool:")
            for tc in response.tool_calls:
                print(f"  工具: {tc['name']}, 參數: {tc['args']}")
        else:
            print(f"LLM 直接回答: {response.content}")


# === 主程式 ===
if __name__ == "__main__":
    print("=" * 50)
    print("Tool：LLM 與系統的邊界")
    print("=" * 50)
    print()

    demo_tool_concept()
    demo_basic_tool()
    demo_structured_tool()
    demo_tool_class()
    demo_tool_error_handling()
    demo_safety_tools()
    demo_tool_binding()

    print("\n完成！")
