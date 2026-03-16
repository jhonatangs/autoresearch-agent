import sys
import json
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from openai import OpenAI

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def search_financial_data(ticker):
    with DDGS() as ddgs:
        all_results = []
        queries = [
            f"{ticker} resultados financeiros 2024 4T24",
            f"{ticker} central de resultados 2024",
            f"{ticker} revenue net income 2024",
            f"{ticker} valor de mercado"
        ]
        for query in queries:
            results = list(ddgs.text(query, max_results=5))
            all_results.extend(results)
        
        return all_results

def process_with_llm(ticker, search_results):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    
    context = "\n".join([f"Source: {r['href']}\nContent: {r['body']}" for r in search_results])
    
    prompt = f"""
    You are a Senior Equity Analyst. Based on the following search results for the ticker {ticker}, extract the latest financial data for the year 2024.
    If 2024 annual data is not yet available, prioritize the most recent quarterly data from 2024 (e.g., 4T24 or 3T24).
    
    Search Results:
    {context}
    
    Requirements:
    1. Extract the official company name.
    2. Extract Revenue (Receita) in BRL. Format as "R$ X.X Billions" or "R$ X.X Millions".
    3. Extract Net Income (Lucro Líquido) in BRL. Format as "R$ X.X Billions" or "R$ X.X Millions".
    4. Extract Market Cap (Valor de Mercado) in BRL. Format as "R$ X.X Billions" or "R$ X.X Millions".
    5. Provide 3 key highlights from the 2024 results.
    6. Sources: You MUST cite where each piece of data came from using [SOURCE URL] next to the value.
    7. FINAL JSON: Include a "sources" list with all unique URLs used.
    
    If any specific metric is missing, state "Data not found in sources".
    Do not hallucinate. Use only the provided context.
    
    Output MUST be a valid JSON object with the following keys:
    {{
        "ticker": "{ticker}",
        "company_name": "...",
        "revenue_brl": "...",
        "net_income_brl": "...",
        "market_cap_brl": "...",
        "key_highlights": ["...", "...", "..."],
        "sources": ["...", "..."]
    }}
    
    Return ONLY the JSON object.
    """
    
    response = client.chat.completions.create(
        model="meta-llama/llama-3.1-8b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    return response.choices[0].message.content.strip()

def main():
    if len(sys.argv) < 2:
        print("Usage: python agent.py <ticker>")
        sys.exit(1)
        
    ticker = sys.argv[1]
    
    try:
        search_results = search_financial_data(ticker)
        json_output = process_with_llm(ticker, search_results)
        
        # Ensure it's valid JSON before printing
        # Sometimes LLMs add text around JSON
        try:
            # Try to find JSON block if LLM added markdown
            if "```json" in json_output:
                json_output = json_output.split("```json")[1].split("```")[0].strip()
            elif "```" in json_output:
                json_output = json_output.split("```")[1].split("```")[0].strip()
            
            # Parse and re-dump to ensure it's clean
            data = json.loads(json_output)
            print(json.dumps(data, indent=4))
        except:
            print(json_output) # Fallback to raw output if parsing fails, but eval might fail
            
    except Exception as e:
        # Fallback or error handling
        # For eval.py to work, we should output JSON even on error or state the error in JSON
        print(json.dumps({"error": str(e)}, indent=4))

if __name__ == "__main__":
    main()
