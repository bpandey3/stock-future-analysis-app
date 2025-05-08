import streamlit as st
import yfinance as yf
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from fpdf import FPDF
from plots import plot_forecast_scenarios
import json
from prompt_stock import generate_analysis
# --- Load environment variables ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# --- Streamlit UI ---
st.set_page_config(page_title="Future ETF/Stock Analyzer", layout="wide")
st.title("📈 AI Stock/ETF Forecast")
# --- LangChain LLM setup ---
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    openai_api_key=api_key
)

# --- Debugging ---
print("API Key Loaded: ", "Yes" if api_key else "No")

asset_type = st.selectbox("Select Asset Type:", ["Stock", "ETF", "Mutual Fund"])

if asset_type == "Mutual Fund":
    st.warning("❌ Mutual fund analysis is not currently supported.")
    st.stop()

if asset_type == "ETF":
    ticker = st.text_input("Enter ETF ticker symbol (e.g., VOO, QQQ):", value="VOO")
if asset_type == "Stock":
    ticker = st.text_input("Enter stock ticker symbol (e.g., TSL, AAPL, LLY):", value="AAPL")



# --- Fetch Stock or ETF Data ---
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "summary": info.get("longBusinessSummary", "N/A"),
        "pe_ratio": info.get("trailingPE", "N/A"),
        "total_debt": info.get("totalDebt", "N/A"),
        "cash": info.get("totalCash", "N/A"),
        "revenue_growth": info.get("revenueGrowth", "N/A"),
        "price": stock.history(period="1d")["Close"].iloc[-1] if not stock.history(period="1d").empty else "N/A"
    }

# --- Save PDF locally ---
def save_pdf_locally(content, ticker):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for line in content.split('\n'):
        pdf.multi_cell(0, 10, line)

    # Create 'results' directory if it doesn't exist
    results_dir = os.path.join(os.getcwd(), "results")
    os.makedirs(results_dir, exist_ok=True)

    filename = f"{ticker.upper()}.pdf"
    output_path = os.path.join(results_dir, filename)
    pdf.output(output_path)
    return output_path




if st.button("Analyze"):
    with st.spinner("Fetching data and generating analysis..."):
        stock_data = get_stock_data(ticker)
        #analysis = generate_analysis(ticker, stock_data)
        analysis = generate_analysis(ticker, stock_data, asset_type)

        print(analysis)
        # Save analysis to PDF
        pdf_path = save_pdf_locally(analysis, ticker)

    st.markdown("## 🧠 AI Forecast & Investment Analysis")
    st.write(analysis)
    #st.success(f"📄 PDF saved locally as: `{pdf_path}`")

    # Try to extract the structured forecast
    try:
        forecast_data = json.loads(analysis.split("```json")[1].split("```")[0])
        fig = plot_forecast_scenarios(
            base_price=forecast_data["base_price"],
            price_2026=forecast_data["expected_price_2026"],
            price_2027=forecast_data["expected_price_2027"],
            cagr_bull=forecast_data["bull_case_2035_cagr"],
            cagr_base=forecast_data["base_case_2035_cagr"],
            cagr_bear=forecast_data["bear_case_2035_cagr"]
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error generating forecast chart: {e}")



    # Optional link to Finchat
   # st.markdown(f"[🔗 View detailed metrics on Finchat.io](https://finchat.io/{ticker.lower()})")
