from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from google import genai
from pathlib import Path

# --------------------------------------------------
# FastAPI
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
# Gemini
# --------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set.")

client = genai.Client(api_key=GEMINI_API_KEY)

# --------------------------------------------------
# Load cleaned datasets
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

orders = pd.read_csv(BASE_DIR / "cleaned_orders.csv")
order_items = pd.read_csv(BASE_DIR / "cleaned_order_items.csv")
products = pd.read_csv(BASE_DIR / "cleaned_products.csv")
customers = pd.read_csv(BASE_DIR / "cleaned_customers.csv")
reviews = pd.read_csv(BASE_DIR / "cleaned_order_reviews.csv")

# --------------------------------------------------
# Calculate basic metrics
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
# Health check
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "gemini_configured": True
    }

# --------------------------------------------------
# Chat
# --------------------------------------------------

@app.post("/chat")
async def chat(request: Request):

    try:
        # Read request from Power BI / browser
        body = await request.json()

        print("REQUEST FROM CLIENT:", body)

        # Try common chatbot field names
        user_message = (
            body.get("message")
            or body.get("query")
            or body.get("prompt")
            or body.get("text")
            or ""
        )

        # Handle messages array
        if not user_message and isinstance(body.get("messages"), list):

            for msg in reversed(body["messages"]):

                if isinstance(msg, dict):

                    content = msg.get("content")

                    if isinstance(content, str):
                        user_message = content
                        break

        if not user_message:

            return {
                "answer": "Please enter a question."
            }

        # --------------------------------------------------
        # Prompt for Gemini
        # --------------------------------------------------

        prompt = f"""
You are an AI assistant for an e-commerce analytics dashboard.

Use the following business information to answer the user's question.

Total Orders: {total_orders}

Total Revenue: {revenue:.2f}

Average Review Score: {average_review:.2f}

Available datasets:

Orders columns:
{list(orders.columns)}

Order Items columns:
{list(order_items.columns)}

Products columns:
{list(products.columns)}

Customers columns:
{list(customers.columns)}

Reviews columns:
{list(reviews.columns)}

Rules:

1. Answer clearly and briefly.
2. Use the available e-commerce information.
3. Do not invent numerical values.
4. If the requested information is not available, say so.
5. Give a business-focused explanation when appropriate.

User question:
{user_message}
"""

        # --------------------------------------------------
        # Gemini request
        # --------------------------------------------------

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        answer = response.text

        print("GEMINI ANSWER:", answer)

        # --------------------------------------------------
        # Return multiple common response fields
        # --------------------------------------------------

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