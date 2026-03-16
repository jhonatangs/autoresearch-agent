# System Architecture: Corporate Financial Equity Agent

## Overview
This system is an automated, self-improving research pipeline designed to build an AI agent capable of researching and structuring financial reports on publicly traded companies (Equities/Blue Chips). 

## System Pillars (Static Files)
- `architecture.md`: Defines roles, responsibilities, and system boundaries.
- `program.md`: Contains the strict constraints and the iterative loop strategy.
- `eval.py`: The immutable judge that scores the agent's output.

## Components & Roles

### 1. The Orchestrator (Claude Haiku 4.5 via Copilot)
- **Role:** Autonomous Developer and Version Controller.
- **Goal:** Iteratively write and improve `agent.py` up to 20 times.
- **Dynamic Testing:** The Orchestrator MUST test a DIFFERENT randomly selected corporate ticker in each iteration via `sys.argv`.

### 2. The Agent (`agent.py` - Senior Equity Analyst)
- **Role:** The target script dynamically built by the Orchestrator.
- **Goal:** Execute web research on a dynamic corporate entity and output a structured JSON report.
- **LLM Engine & Frameworks:** The Orchestrator is ENCOURAGED to use modern Agentic Frameworks (like CrewAI, Agno/Phidata, or LangChain) equipped with Web Search tools to build this agent efficiently. It must use the OpenRouter API (`meta-llama/llama-3.1-8b-instruct`).
- **ANTI-CHEAT RULE (CRITICAL):** MUST NOT contain pre-filled data dictionaries, mocked data, or hardcoded financial numbers. The agent must be a pure routing and scraping engine.

### 3. The Evaluator (`eval.py` - Fair Judge)
- **Role:** The Agentic Judge.
- **Goal:** Executes `agent.py <ticker>`, captures the output, and uses a LOCAL `llama3.2:3b` model to score the report based on Zero Hallucination, Factual Accuracy, and Completeness.