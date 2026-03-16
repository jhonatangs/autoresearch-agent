# Auto-Research Program Rules

## Objective
Develop a Python script (`agent.py`) that acts as a Senior Equity Analyst. The agent must research publicly traded companies provided via command-line arguments (e.g., "PETR4", "VALE3") and output a structured financial JSON report.

## Strict Constraints
1. **Framework & Engine:** `agent.py` MUST use the OpenRouter API (`meta-llama/llama-3.1-8b-instruct`). You are ENCOURAGED to use Agentic Frameworks and their native Tool Calling capabilities for web scraping.
2. **OpenRouter Integration:** Configure frameworks to hit `https://openrouter.ai/api/v1` using the `OPENROUTER_API_KEY` loaded via `python-dotenv`. Include `"Authorization": f"Bearer {OPENROUTER_API_KEY}"` in headers.
3. **Structured Output (CRITICAL):** The FINAL output printed to standard output (stdout) MUST be a valid JSON object. 
4. **Citation Syntax:** The agent must cite sources for ALL financial data. 
5. **Zero Hallucination:** The agent must strictly rely on retrieved data. If a specific metric is missing, it MUST state "Data not found in sources".
6. **AGNOSTIC:** The `agent.py` MUST be 100% dynamic. Do not hardcode specific tickers or companies in the script.
7. **ZERO HARDCODING (ANTI-REWARD HACKING):** You are STRICTLY FORBIDDEN from creating dictionaries, lists, or IF/ELSE statements containing pre-fetched or estimated financial data (e.g., `company_data = {'PETR4': {'revenue': '424.5B'}}`). ALL data MUST be fetched dynamically at runtime via live web search.

## The Autonomous Loop Strategy
1. **Develop:** Modify `agent.py` based on feedback.
2. **Evaluate (Dynamic):** Execute `python eval.py <Random Ticker>` in the terminal.
3. **Analyze:** Read `.last_score` and `actionable_feedback`.
4. **Version Control:** Commit improvements or revert regressions using Git.