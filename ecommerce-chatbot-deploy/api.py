from pathlib import Path
import os

import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from google import genai


# ============================================================
# APP
# ============================================================

app = FastAPI(title="E-Commerce AI Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# GEMINI CLIENT
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# LOAD DATA
# ============================================================

orders = pd.read_csv(BASE_DIR / "cleaned_orders.csv")
order_items = pd.read_csv(BASE_DIR / "cleaned_order_items.csv")
products = pd.read_csv(BASE_DIR / "cleaned_products.csv")
customers = pd.read_csv(BASE_DIR / "cleaned_customers.csv")
reviews = pd.read_csv(BASE_DIR / "cleaned_order_reviews.csv")


# ============================================================
# DATA TYPES
# ============================================================

order_items["quantity"] = pd.to_numeric(
    order_items["quantity"], errors="coerce"
).fillna(0)

order_items["unit_price"] = pd.to_numeric(
    order_items["unit_price"], errors="coerce"
).fillna(0)

order_items["discount(%)"] = pd.to_numeric(
    order_items["discount(%)"], errors="coerce"
).fillna(0)

reviews["review_score"] = pd.to_numeric(
    reviews["review_score"], errors="coerce"
)


# ============================================================
# REVENUE
# ============================================================

order_items["revenue"] = (
    order_items["quantity"]
    * order_items["unit_price"]
    * (1 - order_items["discount(%)"] / 100)
)


# ============================================================
# BASIC METRICS
# ============================================================

total_orders = orders["order_id"].nunique()

total_revenue = order_items["revenue"].sum()

average_review = reviews["review_score"].mean()


# ============================================================
# CATEGORY REVENUE
# ============================================================

category_data = order_items.merge(
    products[["product_id", "Category_name"]],
    on="product_id",
    how="left"
)

category_revenue = (
    category_data
    .groupby("Category_name", dropna=False)["revenue"]
    .sum()
    .sort_values(ascending=False)
)


# ============================================================
# SUB-CATEGORY REVENUE
# ============================================================

subcategory_data = order_items.merge(
    products[["product_id", "sub_category_name"]],
    on="product_id",
    how="left"
)

subcategory_revenue = (
    subcategory_data
    .groupby("sub_category_name", dropna=False)["revenue"]
    .sum()
    .sort_values(ascending=False)
)


# ============================================================
# BRAND REVENUE
# ============================================================

brand_data = order_items.merge(
    products[["product_id", "brand"]],
    on="product_id",
    how="left"
)

brand_revenue = (
    brand_data
    .groupby("brand", dropna=False)["revenue"]
    .sum()
    .sort_values(ascending=False)
)


# ============================================================
# PRODUCT REVENUE
# ============================================================

product_revenue = (
    order_items
    .groupby("product_id")["revenue"]
    .sum()
    .sort_values(ascending=False)
)


# ============================================================
# ORDER STATUS
# ============================================================

status_summary = (
    orders
    .groupby("order_status")["order_id"]
    .nunique()
    .sort_values(ascending=False)
)


# ============================================================
# PAYMENT TYPE
# ============================================================

payment_summary = (
    orders
    .groupby("payment_type")["order_id"]
    .nunique()
    .sort_values(ascending=False)
)


# ============================================================
# CUSTOMER SEGMENT REVENUE
# ============================================================

segment_data = (
    orders[["order_id", "customer_id"]]
    .merge(
        customers[["customer_id", "customer_segment"]],
        on="customer_id",
        how="left"
    )
    .merge(
        order_items[["order_id", "revenue"]],
        on="order_id",
        how="left"
    )
)

segment_revenue = (
    segment_data
    .groupby("customer_segment", dropna=False)["revenue"]
    .sum()
    .sort_values(ascending=False)
)


# ============================================================
# AGE GROUP REVENUE
# ============================================================

age_data = (
    orders[["order_id", "customer_id"]]
    .merge(
        customers[["customer_id", "age_group"]],
        on="customer_id",
        how="left"
    )
    .merge(
        order_items[["order_id", "revenue"]],
        on="order_id",
        how="left"
    )
)

age_group_revenue = (
    age_data
    .groupby("age_group", dropna=False)["revenue"]
    .sum()
    .sort_values(ascending=False)
)


# ============================================================
# GENDER REVENUE
# ============================================================

gender_data = (
    orders[["order_id", "customer_id"]]
    .merge(
        customers[["customer_id", "gender"]],
        on="customer_id",
        how="left"
    )
    .merge(
        order_items[["order_id", "revenue"]],
        on="order_id",
        how="left"
    )
)

gender_revenue = (
    gender_data
    .groupby("gender", dropna=False)["revenue"]
    .sum()
    .sort_values(ascending=False)
)


# ============================================================
# CATEGORY REVIEW SCORE
# ============================================================

category_review_data = (
    order_items[["order_id", "product_id"]]
    .merge(
        products[["product_id", "Category_name"]],
        on="product_id",
        how="left"
    )
    .merge(
        reviews[["order_id", "review_score"]],
        on="order_id",
        how="left"
    )
)

category_review = (
    category_review_data
    .groupby("Category_name", dropna=False)["review_score"]
    .mean()
    .sort_values(ascending=False)
)


# ============================================================
# BUSINESS CONTEXT FOR GEMINI
# ============================================================

business_context = f"""

E-COMMERCE ANALYTICS DATA
=========================

BASIC METRICS
-------------
Total Orders: {total_orders}
Total Revenue: {total_revenue:.2f}
Average Review Score: {average_review:.2f}


REVENUE BY CATEGORY
-------------------
{category_revenue.to_string()}


REVENUE BY SUB-CATEGORY
-----------------------
{subcategory_revenue.head(30).to_string()}


REVENUE BY BRAND
----------------
{brand_revenue.head(30).to_string()}


TOP PRODUCTS BY REVENUE
-----------------------
{product_revenue.head(30).to_string()}


ORDERS BY ORDER STATUS
----------------------
{status_summary.to_string()}


ORDERS BY PAYMENT TYPE
----------------------
{payment_summary.to_string()}


REVENUE BY CUSTOMER SEGMENT
---------------------------
{segment_revenue.to_string()}


REVENUE BY AGE GROUP
--------------------
{age_group_revenue.to_string()}


REVENUE BY GENDER
-----------------
{gender_revenue.to_string()}


AVERAGE REVIEW SCORE BY CATEGORY
--------------------------------
{category_review.to_string()}


AVAILABLE TABLES
================

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
"""


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "E-Commerce AI Chatbot API is running"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "gemini_configured": client is not None
    }

@app.post("/")
async def powerbi_chat_root(request: Request):

    try:
        body = await request.json()

        print("POWER BI ROOT REQUEST:")
        print(body)

        return {
            "answer": "Backend reached successfully. Root POST received."
        }

    except Exception as e:

        print("ROOT ERROR:", repr(e))

        return {
            "answer": "Root endpoint received the request."
        }

# ============================================================
# CHAT
# ============================================================

@app.post("/chat")
async def chat(request: Request):

    try:

        if client is None:
            return {
                "answer": "Gemini API key is not configured on the server."
            }

        body = await request.json()
        print("POWER BI CHAT REQUEST:")
        print(body)

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


        # ========================================================
        # GEMINI PROMPT
        # ========================================================

        prompt = f"""

You are an AI assistant for an E-Commerce Analytics Dashboard.

Use ONLY the information provided in the business data below.

{business_context}


USER QUESTION
=============
{user_message}


RULES
=====

1. Answer the user's question directly and clearly.

2. Use the business data provided above.

3. Do not invent numbers, categories, brands, customers, or other facts.

4. If the user asks which category has the highest revenue,
   use REVENUE BY CATEGORY and identify the highest value.

5. If the user asks about sub-categories,
   use REVENUE BY SUB-CATEGORY.

6. If the user asks about brands,
   use REVENUE BY BRAND.

7. If the user asks about products,
   use TOP PRODUCTS BY REVENUE.

8. If the user asks about order status,
   use ORDERS BY ORDER STATUS.

9. If the user asks about payment methods,
   use ORDERS BY PAYMENT TYPE.

10. If the user asks about customer segments,
    use REVENUE BY CUSTOMER SEGMENT.

11. If the user asks about age groups,
    use REVENUE BY AGE GROUP.

12. If the user asks about gender,
    use REVENUE BY GENDER.

13. If the user asks about reviews,
    use the average review data provided.

14. If the requested information is not available,
    clearly say that it is not available.

15. Keep the answer concise and business-friendly.

16. When appropriate, provide the value and one short business insight.
"""


        # ========================================================
        # GEMINI
        # ========================================================

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

        error_message = str(e)

        if (
            "429" in error_message
            or "RESOURCE_EXHAUSTED" in error_message
        ):
            answer = (
                "The AI service has temporarily reached its request limit. "
                "Please try again later."
            )

        else:
            answer = (
                "Sorry, I could not process your question. "
                "Please try again."
            )

        return {
            "answer": answer
        }