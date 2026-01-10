"""
Chain 基礎：Prompt + LLM + Parser

學習目標：
1. 理解 Chain 的概念
2. 使用 PromptTemplate
3. 使用 OutputParser
4. LCEL (LangChain Expression Language)
"""

import os
from dotenv import load_dotenv

load_dotenv()


def check_api_key():
    """檢查 API Key"""
    if not os.getenv("OPENAI_API_KEY"):
        print("警告：未設定 OPENAI_API_KEY")
        print("以下為程式碼示範，不會實際執行\n")
        return False
    return True


def demo_basic_chain():
    """基本 Chain"""
    print("=== 基本 Chain ===\n")

    print("""
# Chain 的核心概念：Prompt → LLM → Output

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 1. 定義 Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是工安專家，專門分析違規事件。"),
    ("human", "分析這個違規：{violation}")
])

# 2. 建立 LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 3. 組合成 Chain（使用 | 運算子）
chain = prompt | llm

# 4. 執行
response = chain.invoke({"violation": "施工區未戴安全帽"})
print(response.content)
""")

    if check_api_key():
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是工安專家，用一句話分析違規。"),
            ("human", "分析這個違規：{violation}")
        ])

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        chain = prompt | llm

        response = chain.invoke({"violation": "施工區未戴安全帽"})
        print(f"回應: {response.content}")


def demo_output_parser():
    """使用 OutputParser"""
    print("\n=== OutputParser ===\n")

    print("""
# OutputParser 將 LLM 輸出轉換為結構化資料

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

# 定義輸出結構
class ViolationAnalysis(BaseModel):
    severity: str = Field(description="嚴重程度：high/medium/low")
    description: str = Field(description="分析描述")
    action: str = Field(description="建議行動")

# 建立 Parser
parser = JsonOutputParser(pydantic_object=ViolationAnalysis)

# 建立 Prompt（包含格式指令）
prompt = PromptTemplate(
    template=\"\"\"分析以下違規事件：

{violation}

{format_instructions}
\"\"\",
    input_variables=["violation"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# 組合 Chain
chain = prompt | llm | parser

# 執行
result = chain.invoke({"violation": "高空作業未繫安全帶"})
# result 是 dict: {"severity": "high", "description": "...", "action": "..."}
""")

    if check_api_key():
        from langchain_openai import ChatOpenAI
        from langchain_core.output_parsers import JsonOutputParser
        from langchain_core.prompts import PromptTemplate
        from pydantic import BaseModel, Field

        class ViolationAnalysis(BaseModel):
            severity: str = Field(description="嚴重程度：high/medium/low")
            description: str = Field(description="分析描述")
            action: str = Field(description="建議行動")

        parser = JsonOutputParser(pydantic_object=ViolationAnalysis)
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        prompt = PromptTemplate(
            template="""分析以下違規事件，用繁體中文回答：

{violation}

{format_instructions}
""",
            input_variables=["violation"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        chain = prompt | llm | parser
        result = chain.invoke({"violation": "高空作業未繫安全帶"})

        print(f"結果類型: {type(result)}")
        print(f"結果內容: {result}")


def demo_string_parser():
    """字串解析器"""
    print("\n=== StrOutputParser ===\n")

    print("""
# StrOutputParser 直接取得文字內容（最常用）

from langchain_core.output_parsers import StrOutputParser

chain = prompt | llm | StrOutputParser()

result = chain.invoke({"violation": "..."})
# result 是 str，不是 AIMessage
""")


def demo_prompt_templates():
    """各種 Prompt Templates"""
    print("\n=== Prompt Templates ===\n")

    print("""
# 1. 基本 PromptTemplate
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template(
    "分析違規：{violation}"
)

# 2. ChatPromptTemplate（對話格式）
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是工安專家"),
    ("human", "{question}")
])

# 3. MessagesPlaceholder（動態訊息）
from langchain_core.prompts import MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是工安專家"),
    MessagesPlaceholder("history"),  # 對話歷史
    ("human", "{question}")
])

# 4. Few-shot Prompt
from langchain_core.prompts import FewShotPromptTemplate

examples = [
    {"input": "未戴安全帽", "output": "高風險，需立即處理"},
    {"input": "通道阻塞", "output": "中風險，需清理"},
]

example_prompt = PromptTemplate.from_template(
    "違規：{input}\\n分析：{output}"
)

prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="以下是違規分析範例：",
    suffix="違規：{input}\\n分析：",
    input_variables=["input"]
)
""")


def demo_lcel():
    """LCEL (LangChain Expression Language)"""
    print("\n=== LCEL 語法 ===\n")

    print("""
# LCEL 使用 | 運算子串接組件

# 基本串接
chain = prompt | llm | parser

# 等同於
chain = prompt.pipe(llm).pipe(parser)

# 並行處理
from langchain_core.runnables import RunnableParallel

parallel = RunnableParallel(
    analysis=analysis_chain,
    translation=translation_chain,
)
result = parallel.invoke({"input": "..."})
# result = {"analysis": ..., "translation": ...}

# 條件分支
from langchain_core.runnables import RunnableBranch

branch = RunnableBranch(
    (lambda x: x["severity"] == "high", high_priority_chain),
    (lambda x: x["severity"] == "medium", medium_priority_chain),
    default_chain  # 預設
)

# 批次處理
results = chain.batch([
    {"violation": "違規1"},
    {"violation": "違規2"},
])

# 串流
for chunk in chain.stream({"violation": "..."}):
    print(chunk, end="")

# 非同步
result = await chain.ainvoke({"violation": "..."})
""")


def demo_runnable_lambda():
    """自訂處理邏輯"""
    print("\n=== RunnableLambda ===\n")

    print("""
# 使用 RunnableLambda 插入自訂邏輯

from langchain_core.runnables import RunnableLambda

# 定義處理函數
def preprocess(input_dict):
    '''前處理'''
    return {
        "violation": input_dict["violation"].strip().lower(),
        "timestamp": datetime.now().isoformat()
    }

def postprocess(output):
    '''後處理'''
    if output.get("severity") == "high":
        send_alert(output)
    return output

# 組合 Chain
chain = (
    RunnableLambda(preprocess)
    | prompt
    | llm
    | parser
    | RunnableLambda(postprocess)
)
""")


# === 主程式 ===
if __name__ == "__main__":
    print("=" * 50)
    print("Chain 基礎")
    print("=" * 50)
    print()

    demo_basic_chain()
    demo_output_parser()
    demo_string_parser()
    demo_prompt_templates()
    demo_lcel()
    demo_runnable_lambda()

    print("\n完成！")
