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
            f"{ticker} resultados financeiros 4T24 2024",
            f"{ticker} lucro líquido receita 2024",
            f"{ticker} valor de mercado market cap",
            f"{ticker} investor relations IR results"
        ]
        for query in queries:
            results = list(ddgs.text(query, max_results=10))
            all_results.extend(results)
        
        # Deduplicate and sort by potential relevance (simple heuristic)
        unique_results = {r['href']: r for r in all_results}.values()
        return list(unique_results)

def process_with_llm(ticker, search_results):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    
    context = "\n".join([f"Source: {r['href']}\nContent: {r['body']}" for r in search_results[:25]])
    
    prompt = f"""
    You are a Senior Equity Analyst. Your task is to extract the latest 2024 financial data for {ticker}.
    
    IMPORTANT: 
    - Check if the source snippet is ACTUALLY about {ticker}. 
    - If data is from 2024 (e.g., 4T24, 3T24, 2T24, 1T24 or Annual), prioritize it.
    - You MUST populate 'revenue_brl', 'net_income_brl', and 'market_cap_brl' if the data is present anywhere in the search results.
    
    Search Results:
    {context}
    
    Requirements:
    1. Company Name: Full official name for {ticker}.
    2. Revenue (Receita): The most recent 2024 value found. Format: "R$ X.X Billions/Millions [URL]".
    3. Net Income (Lucro Líquido): The most recent 2024 value found. Format: "R$ X.X Billions/Millions [URL]".
    4. Market Cap: The most recent value found. Format: "R$ X.X Billions/Millions [URL]".
    5. Highlights: 3 key points from 2024 results, each MUST have a [URL].
    6. Sources: Comprehensive list of all unique URLs used.
    
    If a specific metric is missing, use "Data not found in sources".
    
    Output MUST be a valid JSON object:
    {{
        "ticker": "{ticker}",
        "company_name": "...",
        "revenue_brl": "...",
        "net_income_brl": "...",
        "market_cap_brl": "...",
        "key_highlights": ["... [URL]", "... [URL]", "... [URL]"],
        "sources": ["URL1", "URL2"]
    }}
    
    Return ONLY JSON.
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
