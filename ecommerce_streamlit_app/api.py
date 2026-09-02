from pathlib import Path
import os

import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from google import genai


# --------------------------------------------------
# App
# --------------------------------------------------

app = FastAPI(title="E-Commerce AI Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent


# --------------------------------------------------
# Gemini client
# --------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


# --------------------------------------------------
# Load data
# --------------------------------------------------

orders = pd.read_csv(BASE_DIR / "cleaned_orders.csv")
order_items = pd.read_csv(BASE_DIR / "cleaned_order_items.csv")
products = pd.read_csv(BASE_DIR / "cleaned_products.csv")
customers = pd.read_csv(BASE_DIR / "cleaned_customers.csv")
reviews = pd.read_csv(BASE_DIR / "cleaned_order_reviews.csv")


# --------------------------------------------------
# Metrics
# --------------------------------------------------

total_orders = orders["order_id"].nunique()

revenue = (
    order_items["quantity"]
    * order_items["unit_price"]
    * (1 - order_items["discount(%)"] / 100)
).sum()

average_review = reviews["review_score"].mean()


# --------------------------------------------------
# Home
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "E-Commerce AI Chatbot API is running"
    }


# --------------------------------------------------
# Health
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "gemini_configured": client is not None
    }


# --------------------------------------------------
# Chat
# --------------------------------------------------

@app.post("/chat")
async def chat(request: Request):

    try:
        if client is None:
            return {
                "answer": "Gemini API key is not configured on the server."
            }

        body = await request.json()

        print("REQUEST:", body)

        user_message = (
            body.get("message")
            or body.get("query")
            or body.get("prompt")
            or body.get("text")
            or ""
        )

        if not user_message and isinstance(body.get("messages"), list):
            for item in reversed(body["messages"]):
                if isinstance(item, dict):
                    content = item.get("content")
                    if isinstance(content, str):
                        user_message = content
                        break

        if not user_message:
            return {
                "answer": "Please enter a question."
            }

        prompt = f"""
You are an AI assistant for an e-commerce analytics dashboard.

Business metrics:

Total Orders: {total_orders}
Total Revenue: {revenue:.2f}
Average Review Score: {average_review:.2f}

Available tables:

Orders:
{list(orders.columns)}

Order Items:
{list(order_items.columns)}

Products:
{list(products.columns)}

Customers:
{list(customers.columns)}

Reviews:
{list(reviews.columns)}

User question:
{user_message}

Rules:
- Answer clearly and briefly.
- Do not invent numerical values.
- Use the available e-commerce information.
- If the requested information is unavailable, say so.
"""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        answer = response.text

        print("ANSWER:", answer)

        return {
            "answer": answer,
            "response": answer,
            "message": answer,
            "text": answer
        }

    except Exception as e:

        print("CHAT ERROR:", repr(e))

        return {
            "answer": "Sorry, I could not process your question.",
            "error": str(e)
        }