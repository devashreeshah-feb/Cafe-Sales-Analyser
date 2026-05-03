from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data and models at startup
try:
    df = pd.read_csv('processed_sales_data.csv')
    rf_model = joblib.load('rf_model.joblib')
except FileNotFoundError:
    print("Warning: Model or data not found. Please run train_model.py first.")
    df = pd.DataFrame()
    rf_model = None

# Cost estimates based on PRD margins to calculate profit
margin_map = {
    'Coffee': 0.70,
    'Tea': 0.70,
    'Smoothie': 0.55,
    'Juice': 0.50,
    'Cake': 0.50,
    'Salad': 0.45,
    'Sandwich': 0.40,
    'Cookie': 0.60
}

if not df.empty:
    df['margin'] = df['item'].map(margin_map).fillna(0)
    df['estimated_profit'] = df['total_spent'] * df['margin']

@app.get("/api/dashboard/overview")
def get_overview():
    total_revenue = float(df['total_spent'].sum())
    gross_profit = float(df['estimated_profit'].sum())
    avg_txn_value = float(df['total_spent'].mean())
    
    # Data quality score: percentage of rows without missing/UNKNOWN/ERROR
    # As per PRD, 90.3% is baseline completeness.
    invalid_mask = (df['item'] == 'UNKNOWN') | (df['item'] == 'ERROR') | \
                   (df['location'] == 'UNKNOWN') | (df['payment_method'] == 'UNKNOWN') | \
                   (df['payment_method'] == 'ERROR')
    data_quality_score = float(1 - (invalid_mask.sum() / len(df))) * 100
    
    # Revenue by month
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    monthly_rev = df.groupby(df['transaction_date'].dt.strftime('%b'))['total_spent'].sum()
    months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_revenue = []
    for m in months_order:
        if m in monthly_rev:
            monthly_revenue.append({"month": m, "revenue": float(monthly_rev[m])})
        else:
            monthly_revenue.append({"month": m, "revenue": 0})
            
    # Revenue by item
    item_rev = df.groupby('item')['total_spent'].sum().reset_index()
    item_revenue = [{"item": row['item'], "revenue": float(row['total_spent'])} for _, row in item_rev.iterrows() if row['item'] not in ['UNKNOWN', 'ERROR']]
    item_revenue = sorted(item_revenue, key=lambda x: x['revenue'], reverse=True)

    return {
        "kpis": {
            "totalRevenue": total_revenue,
            "grossProfit": gross_profit,
            "avgTransactionValue": avg_txn_value,
            "dataQualityScore": data_quality_score
        },
        "monthlyRevenue": monthly_revenue,
        "itemRevenue": item_revenue
    }

@app.get("/api/dashboard/profitability")
def get_profitability():
    # Item-level profitability matrix
    metrics = df.groupby('item').agg(
        revenue=('total_spent', 'sum'),
        profit=('estimated_profit', 'sum'),
        transactions=('transaction_id', 'count')
    ).reset_index()
    
    items = []
    for _, row in metrics.iterrows():
        item = row['item']
        if item in ['UNKNOWN', 'ERROR']:
            continue
        margin = margin_map.get(item, 0)
        
        # Assign rank based on PRD logic roughly
        if margin >= 0.7:
            rank = "S - Best Margin"
        elif margin >= 0.55:
            rank = "A - Profitable"
        elif margin >= 0.45:
            rank = "A - High Rev" if row['revenue'] > 15000 else "B - Mid Tier"
        else:
            rank = "B - Low Margin"
            
        items.append({
            "item": item,
            "revenue": float(row['revenue']),
            "profit": float(row['profit']),
            "margin": float(margin * 100),
            "transactions": int(row['transactions']),
            "rank": rank
        })
    
    # Sort by revenue descending
    items = sorted(items, key=lambda x: x['revenue'], reverse=True)
    return items

@app.get("/api/dashboard/data-quality")
def get_data_quality():
    # Field-level completeness audit table
    total_records = len(df)
    item_missing = int((df['item'].isin(['UNKNOWN', 'ERROR'])).sum())
    payment_missing = int((df['payment_method'].isin(['UNKNOWN', 'ERROR'])).sum())
    location_missing = int((df['location'] == 'UNKNOWN').sum())
    
    # Actually Date missing was filled in train_model. We'll use approx original count 4.6%
    # We can check if date matches median for approximation, but returning static based on PRD or actual calculated
    
    completeness = [
        {"field": "Item", "missing": item_missing, "missingPercentage": item_missing / total_records * 100},
        {"field": "Payment Method", "missing": payment_missing, "missingPercentage": payment_missing / total_records * 100},
        {"field": "Location", "missing": location_missing, "missingPercentage": location_missing / total_records * 100},
    ]
    
    # Revenue at risk
    risk_mask = df['item'].isin(['UNKNOWN', 'ERROR'])
    revenue_at_risk = float(df[risk_mask]['total_spent'].sum())
    
    # Anomaly feed
    anomalies = df[df['is_anomaly'] == True].head(50).to_dict('records')
    # Filter to only needed fields
    anomaly_feed = []
    for a in anomalies:
        anomaly_feed.append({
            "transactionId": a['transaction_id'],
            "date": str(a['transaction_date']),
            "item": a['item'],
            "actualSpent": float(a['total_spent']),
            "predictedSpent": float(a['predicted_spent']),
            "difference": float(a['residual'])
        })
        
    return {
        "completeness": completeness,
        "revenueAtRisk": revenue_at_risk,
        "anomalyFeed": anomaly_feed
    }

class ChatMessage(BaseModel):
    message: str

@app.post("/api/chat")
def chat_with_data(chat: ChatMessage):
    msg = chat.message.lower()
    
    # AI-powered response if API key is provided
    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            
            # Prepare data context
            total_rev = df['total_spent'].sum() if not df.empty else 0
            top_item = df.groupby('item')['total_spent'].sum().idxmax() if not df.empty else "N/A"
            
            context = f"""
            You are Barista AI, an expert assistant analyzing a cafe's sales data.
            Key Insights from the dataset:
            - Total Revenue: £{total_rev:,.2f}
            - Top Selling Item (by revenue): {top_item}
            - High Margin Items: Coffee and Tea (70% margin)
            - Low Margin Items: Sandwiches (40% margin)
            - Data Quality Issues: ~9.6% of revenue is tied to 'UNKNOWN' or 'ERROR' items. ~39.6% transactions missing location data.
            
            Based on this context, answer the user's question concisely and helpfully. Do not invent data outside of this context.
            User: {chat.message}
            """
            response = model.generate_content(context)
            return {"response": response.text}
        except Exception as e:
            print(f"Gemini API error: {e}")
            # Fallback to rule-based if API fails
            pass
            
    # Rule-based fallback
    if "why are sales low" in msg or "sales low" in msg:
        return {"response": "While overall sales reached £86,606, there is a significant data quality issue. About 9.6% of revenue (£8,271) is tied to 'UNKNOWN' or 'ERROR' items. Additionally, high-volume items like Sandwiches have the lowest margin (40%)."}
    
    elif "highest selling" in msg or "best selling" in msg or "top product" in msg or "most popular" in msg:
        return {"response": "Salad is the highest revenue-generating product, bringing in £16,423 across 1,148 transactions. However, its margin is only 45%."}
        
    elif "highest margin" in msg or "most profitable" in msg:
        return {"response": "Coffee and Tea have the highest margins at 70%. Despite this, they only represent about 14% of total revenue. Promoting these items could significantly boost gross profit!"}
        
    elif "lowest margin" in msg or "least profitable" in msg:
        return {"response": "Sandwiches have the lowest margin at 40%, despite being the second highest in total volume. Introducing premium variants could help raise this margin."}
        
    elif "hello" in msg or "hi" in msg or "hey" in msg:
        return {"response": "Hello! I am Barista AI. I have analyzed all 10,000 transactions from your cafe. You can ask me about top products, margins, or why sales might be struggling."}
        
    elif "data quality" in msg or "error" in msg:
        return {"response": "Our ML model found that 39.6% of transactions are missing location data, and almost 10% of items are completely unknown. Fixing your POS system will give you much clearer insights."}
        
    else:
        return {"response": "That's a great question! Based on my analysis, I recommend focusing on upselling high-margin items like Coffee and Smoothies, and fixing your POS system to reduce the 'UNKNOWN' item errors. Ask me about your 'highest selling product' or 'profitability'! (Add GEMINI_API_KEY to your .env file to enable smart AI responses!)"}

# Serve frontend static files
frontend_dist = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    
    @app.exception_handler(404)
    async def custom_404_handler(_, __):
        return FileResponse(os.path.join(frontend_dist, 'index.html'))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
