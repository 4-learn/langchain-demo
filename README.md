# LangChain Demo

行為層（Orchestration）的 Demo 程式碼 - 決策編排。

## 安裝

```bash
pip install -r requirements.txt
```

## 設定

```bash
export OPENAI_API_KEY="your-api-key"
```

## 檔案說明

| 檔案 | 說明 |
|------|------|
| `01_chain_basics.py` | Chain 基礎：Prompt + LLM + Parser |
| `02_chain_composition.py` | Chain 組合：Sequential, Parallel |
| `03_tools.py` | Tool 定義與使用 |
| `04_agents.py` | Agent 基礎與控制 |
| `05_safety_chain.py` | 工安系統 Chain 範例 |

## 執行

```bash
# Chain 基礎
python 01_chain_basics.py

# Tool 使用
python 03_tools.py

# Agent
python 04_agents.py
```

## 概念

```
Chain = Prompt → LLM → OutputParser
Tool = LLM 與外部世界的橋樑
Agent = LLM 決定使用哪些 Tool
```
