import plotly.graph_objects as go
import json

import plotly.graph_objects as go

def plot_forecast_scenarios(base_price, price_2026, price_2027, cagr_bull, cagr_base, cagr_bear):
    years = [2025, 2026, 2027, 2035]
    
    def future_price(start_price, cagr, years_forward):
        return start_price * ((1 + cagr) ** years_forward)
    
    bull_prices = [base_price, price_2026, price_2027, future_price(base_price, cagr_bull, 10)]
    base_prices = [base_price, price_2026, price_2027, future_price(base_price, cagr_base, 10)]
    bear_prices = [base_price, price_2026, price_2027, future_price(base_price, cagr_bear, 10)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=bull_prices, name='Bull Case', mode='lines+markers', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=years, y=base_prices, name='Base Case', mode='lines+markers', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=years, y=bear_prices, name='Bear Case', mode='lines+markers', line=dict(color='red')))

    fig.update_layout(
        title="Forecasted Price Scenarios (2025–2035)",
        xaxis_title="Year",
        yaxis_title="Price (USD)",
        legend_title="Scenario",
        template="plotly_white"
    )
    return fig


