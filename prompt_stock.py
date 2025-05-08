import streamlit as st
import yfinance as yf
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from fpdf import FPDF
from plots import plot_forecast_scenarios
import json
# --- Load environment variables ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# --- LangChain LLM setup ---
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    openai_api_key=api_key
)


def generate_analysis(ticker, stock_data, asset_type):
    base_prompt = f"""
You are a financial analyst. Provide a future-oriented investment analysis for the {asset_type.lower()} '{ticker}' using the following data:

- Summary: {stock_data['summary']}
- PE Ratio: {stock_data['pe_ratio']}
- Total Debt: {stock_data['total_debt']}
- Cash: {stock_data['cash']}
- Revenue Growth: {stock_data['revenue_growth']}
- Current Price (May 2025): ${stock_data['price']}

Include in your analysis:

1. PE ratio context vs historical and sector average  
2. Balance sheet strengths and risks  
3. Growth opportunities (company- and sector-level)  
4. 2-Year Price Forecast:  
   - Expected price by December 2026  
   - Expected price by December 2027  
   - Key factors influencing the forecasts  
   - Confidence level for each estimate  
5. 10-Year Outlook (to 2035):  
   - Bullish, neutral, and bearish return projections  
   - Expected CAGR under each scenario
"""

    if asset_type == "ETF":
        base_prompt += "\n   - Compare to S&P 500 (7% historical CAGR baseline)"

    base_prompt += f"""
6. Final Investment Thesis: Is this {asset_type.lower()} likely to outperform the S&P 500 over the next decade?

---

At the end of your analysis, return a JSON block in this exact structure (surrounded by triple backticks and tagged as `json`):

```json
{{
  "expected_price_2026": 123.45,
  "expected_price_2027": 137.89,
  "bull_case_2035_cagr": 0.12,
  "base_case_2035_cagr": 0.08,
  "bear_case_2035_cagr": 0.03,
  "base_price": {stock_data['price']}
}}
"""
    response = llm([HumanMessage(content=base_prompt)])
    return response.content
