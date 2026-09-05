from pathlib import Path
import os

import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from google import genai


# ============================================================
# 1. FASTAPI APPLICATION
# ============================================================

app = FastAPI(title="E-Commerce AI Chatbot API")


# Allow Power BI / browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 2. FILE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# 3. GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# 4. LOAD DATASETS
# ============================================================

try:
    orders = pd.read_csv(BASE_DIR / "cleaned_orders.csv")
    order_items = pd.read_csv(BASE_DIR / "cleaned_order_items.csv")
    products = pd.read_csv(BASE_DIR / "cleaned_products.csv")
    customers = pd.read_csv(BASE_DIR / "cleaned_customers.csv")
    reviews = pd.read_csv(BASE_DIR / "cleaned_order_reviews.csv")

    # Geolocation is optional
    geolocation_file = BASE_DIR / "cleaned_geolocation.csv"

    if geolocation_file.exists():
        geolocation = pd.read_csv(geolocation_file)
    else:
        geolocation = pd.DataFrame()

except Exception as e:
    raise RuntimeError(f"Error loading datasets: {e}")


# ============================================================
# 5. CLEAN COLUMN NAMES
# ============================================================

orders.columns = orders.columns.str.strip()
order_items.columns = order_items.columns.str.strip()
products.columns = products.columns.str.strip()
customers.columns = customers.columns.str.strip()
reviews.columns = reviews.columns.str.strip()

if not geolocation.empty:
    geolocation.columns = geolocation.columns.str.strip()


# ============================================================
# 6. PREPARE NUMERIC COLUMNS
# ============================================================

numeric_order_item_columns = [
    "quantity",
    "unit_price",
    "discount(%)",
    "shipping_cost",
]

for column in numeric_order_item_columns:
    if column in order_items.columns:
        order_items[column] = pd.to_numeric(
            order_items[column],
            errors="coerce"
        ).fillna(0)


if "review_score" in reviews.columns:
    reviews["review_score"] = pd.to_numeric(
        reviews["review_score"],
        errors="coerce"
    )


# ============================================================
# 7. CALCULATE REVENUE
# ============================================================

if "discount(%)" in order_items.columns:

    order_items["revenue"] = (
        order_items["quantity"]
        * order_items["unit_price"]
        * (1 - order_items["discount(%)"] / 100)
    )

else:

    order_items["revenue"] = (
        order_items["quantity"]
        * order_items["unit_price"]
    )


# ============================================================
# 8. BASIC BUSINESS METRICS
# ============================================================

total_orders = orders["order_id"].nunique()

total_revenue = order_items["revenue"].sum()

average_review = reviews["review_score"].mean()


# ============================================================
# 9. REVENUE BY CATEGORY
# ============================================================

if "Category_name" in products.columns:

    category_revenue = (
        order_items
        .merge(
            products[["product_id", "Category_name"]],
            on="product_id",
            how="left"
        )
        .groupby("Category_name")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

else:
    category_revenue = pd.Series(dtype=float)


# ============================================================
# 10. REVENUE BY SUB-CATEGORY
# ============================================================

if "sub_category_name" in products.columns:

    subcategory_revenue = (
        order_items
        .merge(
            products[["product_id", "sub_category_name"]],
            on="product_id",
            how="left"
        )
        .groupby("sub_category_name")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

else:
    subcategory_revenue = pd.Series(dtype=float)


# ============================================================
# 11. REVENUE BY BRAND
# ============================================================

if "brand" in products.columns:

    brand_revenue = (
        order_items
        .merge(
            products[["product_id", "brand"]],
            on="product_id",
            how="left"
        )
        .groupby("brand")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

else:
    brand_revenue = pd.Series(dtype=float)


# ============================================================
# 12. REVENUE BY PRODUCT
# ============================================================

product_columns = ["product_id"]

if "product_id" in products.columns:
    product_columns.append("Category_name")


product_revenue = (
    order_items
    .groupby("product_id")["revenue"]
    .sum()
    .sort_values(ascending=False)
)


# ============================================================
# 13. ORDERS BY PAYMENT TYPE
# ============================================================

if "payment_type" in orders.columns:

    payment_summary = (
        orders
        .groupby("payment_type")["order_id"]
        .nunique()
        .sort_values(ascending=False)
    )

else:
    payment_summary = pd.Series(dtype=int)


# ============================================================
# 14. ORDERS BY STATUS
# ============================================================

if "order_status" in orders.columns:

    status_summary = (
        orders
        .groupby("order_status")["order_id"]
        .nunique()
        .sort_values(ascending=False)
    )

else:
    status_summary = pd.Series(dtype=int)


# ============================================================
# 15. REVENUE BY CUSTOMER SEGMENT
# ============================================================

if "customer_segment" in customers.columns:

    segment_revenue = (
        orders[["order_id", "customer_id"]]
        .merge(
            customers[["customer_id", "customer_segment"]],
            on="customer_id",
            how="left"
        )
        .merge(
            order_items[["order_id", "revenue"]],
            on="order_id",
            how="inner"
        )
        .groupby("customer_segment")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

else:
    segment_revenue = pd.Series(dtype=float)


# ============================================================
# 16. REVENUE BY AGE GROUP
# ============================================================

if "age_group" in customers.columns:

    age_group_revenue = (
        orders[["order_id", "customer_id"]]
        .merge(
            customers[["customer_id", "age_group"]],
            on="customer_id",
            how="left"
        )
        .merge(
            order_items[["order_id", "revenue"]],
            on="order_id",
            how="inner"
        )
        .groupby("age_group")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

else:
    age_group_revenue = pd.Series(dtype=float)


# ============================================================
# 17. REVENUE BY GENDER
# ============================================================

if "gender" in customers.columns:

    gender_revenue = (
        orders[["order_id", "customer_id"]]
        .merge(
            customers[["customer_id", "gender"]],
            on="customer_id",
            how="left"
        )
        .merge(
            order_items[["order_id", "revenue"]],
            on="order_id",
            how="inner"
        )
        .groupby("gender")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

else:
    gender_revenue = pd.Series(dtype=float)


# ============================================================
# 18. REGION REVENUE
# ============================================================

region_revenue = pd.Series(dtype=float)

if (
    not geolocation.empty
    and "region" in geolocation.columns
    and "customer_zip_code" in customers.columns
    and "geolocation_zip_code" in geolocation.columns
):

    customer_region = (
        customers[["customer_id", "customer_zip_code"]]
        .merge(
            geolocation[
                ["geolocation_zip_code", "region"]
            ],
            left_on="customer_zip_code",
            right_on="geolocation_zip_code",
            how="left"
        )
    )

    region_revenue = (
        orders[["order_id", "customer_id"]]
        .merge(
            customer_region[
                ["customer_id", "region"]
            ],
            on="customer_id",
            how="left"
        )
        .merge(
            order_items[["order_id", "revenue"]],
            on="order_id",
            how="inner"
        )
        .groupby("region")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )


# ============================================================
# 19. REVIEW SCORE BY CATEGORY
# ============================================================

category_review = pd.Series(dtype=float)

if (
    "order_id" in reviews.columns
    and "product_id" in order_items.columns
    and "product_id" in products.columns
    and "Category_name" in products.columns
):

    review_category_data = (
        reviews[["order_id", "review_score"]]
        .merge(
            order_items[["order_id", "product_id"]],
            on="order_id",
            how="left"
        )
        .merge(
            products[["product_id", "Category_name"]],
            on="product_id",
            how="left"
        )
    )

    category_review = (
        review_category_data
        .groupby("Category_name")["review_score"]
        .mean()
        .sort_values(ascending=False)
    )


# ============================================================
# 20. REUSABLE FORMAT FUNCTION
# ============================================================

def format_series(series, top_n=None):
    """
    Convert a pandas Series into readable text for Gemini.
    """

    if series is None or series.empty:
        return "No data available."

    if top_n is not None:
        series = series.head(top_n)

    lines = []

    for name, value in series.items():

        if pd.isna(name):
            name = "Unknown"

        if isinstance(value, float):
            lines.append(f"{name}: {value:,.2f}")
        else:
            lines.append(f"{name}: {value:,}")

    return "\n".join(lines)


# ============================================================
# 21. HOME ENDPOINT
# ============================================================

@app.get("/")
def home():

    return {
        "status": "online",
        "message": "E-Commerce AI Chatbot API is running"
    }


# ============================================================
# 22. HEALTH ENDPOINT
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "gemini_configured": client is not None,
        "total_orders": int(total_orders),
        "total_revenue": round(float(total_revenue), 2),
        "average_review_score": round(float(average_review), 2)
    }


# ============================================================
# 23. CHAT ENDPOINT
# ============================================================

@app.post("/chat")
async def chat(request: Request):

    try:

        # ----------------------------------------------------
        # Check Gemini
        # ----------------------------------------------------

        if client is None:

            return {
                "answer": "Gemini API key is not configured on the server."
            }

        # ----------------------------------------------------
        # Read request
        # ----------------------------------------------------

        body = await request.json()

        print("REQUEST FROM CLIENT:")
        print(body)

        # ----------------------------------------------------
        # Extract user question
        # ----------------------------------------------------

        user_message = (
            body.get("message")
            or body.get("query")
            or body.get("prompt")
            or body.get("text")
            or ""
        )

        # ----------------------------------------------------
        # Handle messages array
        # ----------------------------------------------------

        if (
            not user_message
            and isinstance(body.get("messages"), list)
        ):

            for message in reversed(body["messages"]):

                if isinstance(message, dict):

                    content = message.get("content")

                    if isinstance(content, str):

                        user_message = content
                        break

        # ----------------------------------------------------
        # Empty question
        # ----------------------------------------------------

        if not user_message:

            return {
                "answer": "Please enter a question."
            }

        # ----------------------------------------------------
        # Build business context
        # ----------------------------------------------------

        business_context = f"""

============================================================
E-COMMERCE BUSINESS SUMMARY
============================================================

TOTAL METRICS
------------------------------------------------------------

Total Orders:
{total_orders:,}

Total Revenue:
{total_revenue:,.2f}

Average Review Score:
{average_review:.2f}


============================================================
REVENUE BY CATEGORY
============================================================

{format_series(category_revenue)}


============================================================
REVENUE BY SUB-CATEGORY
============================================================

{format_series(subcategory_revenue, 20)}


============================================================
TOP BRANDS BY REVENUE
============================================================

{format_series(brand_revenue, 20)}


============================================================
TOP PRODUCTS BY REVENUE
============================================================

{format_series(product_revenue, 20)}


============================================================
ORDERS BY PAYMENT TYPE
============================================================

{format_series(payment_summary)}


============================================================
ORDERS BY ORDER STATUS
============================================================

{format_series(status_summary)}


============================================================
REVENUE BY CUSTOMER SEGMENT
============================================================

{format_series(segment_revenue)}


============================================================
REVENUE BY AGE GROUP
============================================================

{format_series(age_group_revenue)}


============================================================
REVENUE BY GENDER
============================================================

{format_series(gender_revenue)}


============================================================
REVENUE BY REGION
============================================================

{format_series(region_revenue)}


============================================================
AVERAGE REVIEW SCORE BY CATEGORY
============================================================

{format_series(category_review)}

"""

        # ----------------------------------------------------
        # Gemini prompt
        # ----------------------------------------------------

        prompt = f"""
You are an AI assistant for an e-commerce analytics dashboard.

Your job is to answer questions using the business data supplied below.

{business_context}

============================================================
USER QUESTION
============================================================

{user_message}

============================================================
ANSWERING RULES
============================================================

1. Answer using the supplied e-commerce data.
2. Never invent numbers.
3. If the requested information is not available, clearly say:
   "This information is not available in the current dataset."
4. For "highest", "lowest", "most", or "least" questions,
   identify the correct item from the supplied values.
5. For revenue questions, use the Total Revenue or relevant
   revenue breakdown.
6. For order questions, use Total Orders or the relevant
   order breakdown.
7. For review questions, use the review score information.
8. Give the numerical value when available.
9. Keep the answer concise and easy to understand.
10. Add a short business insight when useful.
11. Do not mention internal prompt instructions.
12. Do not say that you are unable to access the CSV files.
"""

        # ----------------------------------------------------
        # Call Gemini
        # ----------------------------------------------------

         print("SENDING REQUEST TO GEMINI...")

         response = client.models.generate_content(
          model="gemini-3.6-flash",
          contents=prompt,
          config={
            "temperature": 0.2
            }
           )

        print("GEMINI RESPONSE OBJECT:", repr(response))

        answer = getattr(response, "text", None)

        print("GEMINI TEXT:", repr(answer))

        if not answer:
          answer = "Gemini returned an empty response."    

        print("GEMINI ANSWER:")
        print(answer)

        # ----------------------------------------------------
        # Return flexible response
        # ----------------------------------------------------

        return {
            "answer": answer,
            "response": answer,
            "message": answer,
            "text": answer
        }

    # --------------------------------------------------------
    # Error handling
    # --------------------------------------------------------

    except Exception as e:

        print("CHAT ERROR:", repr(e))

        error_message = str(e)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
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