import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="E-Commerce Retail Tech | Integrated Analytics",
    page_icon="🛒",
    layout="wide"
)

# -----------------------------
# Data loading
# -----------------------------
@st.cache_data
def load_data():
    customers = pd.read_csv(BASE_DIR / "cleaned_customers.csv")
    geolocation = pd.read_csv(BASE_DIR / "cleaned_geolocation.csv") if (BASE_DIR / "cleaned_geolocation.csv").exists() else pd.DataFrame()
    orders = pd.read_csv(BASE_DIR / "cleaned_orders.csv")
    items = pd.read_csv(BASE_DIR / "cleaned_order_items.csv")
    reviews = pd.read_csv(BASE_DIR / "cleaned_order_reviews.csv")
    products = pd.read_csv(BASE_DIR / "cleaned_products.csv")

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"], errors="coerce"
    )
    orders["year"] = orders["order_purchase_timestamp"].dt.year
    orders["month"] = orders["order_purchase_timestamp"].dt.to_period("M").astype(str)

    for col in ["quantity", "unit_price", "discount(%)", "shipping_cost"]:
        if col in items.columns:
            items[col] = pd.to_numeric(items[col], errors="coerce").fillna(0)

    if "discount(%)" not in items.columns:
        items["discount(%)"] = 0

    items["revenue"] = (
        items["unit_price"] * items["quantity"]
        * (1 - items["discount(%)"] / 100)
    )

    sales = (
        items.merge(
            orders[
                ["order_id", "customer_id", "order_status", "payment_type",
                 "order_purchase_timestamp", "year", "month"]
            ],
            on="order_id", how="left"
        )
        .merge(
            customers[["customer_id", "gender", "age_group", "customer_segment"]],
            on="customer_id", how="left"
        )
        .merge(
            products[
                ["product_id", "Category_name", "sub_category_name", "brand",
                 "selling_price", "stock_availability", "cost_price"]
            ],
            on="product_id", how="left"
        )
    )

    sales["price_category"] = pd.cut(
        sales["unit_price"],
        bins=[-float("inf"), sales["unit_price"].median(), float("inf")],
        labels=["Low Price", "High Price"],
        include_lowest=True
    )
    sales["discount_level"] = pd.cut(
        sales["discount(%)"],
        bins=[-float("inf"), 10, 20, float("inf")],
        labels=["Low Discount", "Medium Discount", "High Discount"],
        include_lowest=True
    )
    sales["revenue_category"] = pd.cut(
        sales["revenue"],
        bins=[-float("inf"), sales["revenue"].median(), float("inf")],
        labels=["Low Revenue", "High Revenue"],
        include_lowest=True
    )

    return customers, geolocation, orders, items, reviews, products, sales


try:
    customers, geolocation, orders, items, reviews, products, sales = load_data()
except Exception as e:
    st.error("Unable to load the cleaned CSV files.")
    st.exception(e)
    st.stop()

# -----------------------------
# Header
# -----------------------------
st.title("🛒 E-Commerce Retail Tech — Integrated Analytics Dashboard")
st.caption("Capstone Analytics | Phases 3–9 + Power BI + AI Business Assistant")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("📚 Project Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Executive Overview",
        "📋 Phase 3 — Business Questions",
        "📊 Phase 4 — Excel Dashboard",
        "🔎 Phase 5 — Python EDA",
        "🗄️ Phase 6 — SQL Analysis",
        "⚙️ Phase 7 — Feature Engineering",
        "📐 Phase 8 — Statistical Validation",
        "🤖 Phase 9 — Machine Learning",
        "📈 Power BI Dashboard",
        "💡 Insights & Recommendations",
        "🤖 AI Business Assistant",
    ]
)

st.sidebar.divider()
st.sidebar.header("🔎 Filters")

def options(col):
    return sorted(sales[col].dropna().unique().tolist())

years = options("year")
selected_years = st.sidebar.multiselect("Year", years, default=years)
categories = options("Category_name")
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
segments = options("customer_segment")
selected_segments = st.sidebar.multiselect("Customer Segment", segments, default=segments)
payments = options("payment_type")
selected_payments = st.sidebar.multiselect("Payment Type", payments, default=payments)
statuses = options("order_status")
selected_statuses = st.sidebar.multiselect("Order Status", statuses, default=statuses)

filtered = sales[
    sales["year"].isin(selected_years)
    & sales["Category_name"].isin(selected_categories)
    & sales["customer_segment"].isin(selected_segments)
    & sales["payment_type"].isin(selected_payments)
    & sales["order_status"].isin(selected_statuses)
].copy()

total_revenue = filtered["revenue"].sum()
total_orders = filtered["order_id"].nunique()
total_quantity = filtered["quantity"].sum()
aov = total_revenue / total_orders if total_orders else 0
avg_discount = filtered["discount(%)"].mean() if len(filtered) else 0

status_lower = filtered["order_status"].astype(str).str.lower()
delivered = filtered.loc[status_lower.eq("delivered"), "order_id"].nunique()
cancelled = filtered.loc[status_lower.eq("cancelled"), "order_id"].nunique()
shipped = filtered.loc[status_lower.eq("shipped"), "order_id"].nunique()
returned = filtered.loc[status_lower.eq("returned"), "order_id"].nunique()

# -----------------------------
# Executive Overview
# -----------------------------
if page == "🏠 Executive Overview":
    st.header("🏠 Executive Overview")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    c2.metric("Total Orders", f"{total_orders:,}")
    c3.metric("Average Order Value", f"₹{aov:,.0f}")
    c4.metric("Quantity Sold", f"{total_quantity:,.0f}")
    c5.metric("Avg Discount", f"{avg_discount:.2f}%")

    st.divider()
    a, b, c, d = st.columns(4)
    a.metric("Delivered", f"{delivered:,}")
    b.metric("Cancelled", f"{cancelled:,}")
    c.metric("Shipped", f"{shipped:,}")
    d.metric("Returned", f"{returned:,}")

    left, right = st.columns(2)

    with left:
        monthly = filtered.groupby("month", as_index=False)["revenue"].sum().sort_values("month")
        fig = px.line(monthly, x="month", y="revenue", markers=True,
                      title="Monthly Revenue Trend",
                      labels={"month": "Month", "revenue": "Revenue (₹)"})
        st.plotly_chart(fig, use_container_width=True)

    with right:
        cat_df = filtered.groupby("Category_name", as_index=False)["revenue"].sum()\
                         .sort_values("revenue", ascending=False).head(10)
        fig = px.bar(cat_df, x="revenue", y="Category_name", orientation="h",
                     title="Top Categories by Revenue",
                     labels={"Category_name": "Category", "revenue": "Revenue (₹)"})
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        pay_df = filtered.groupby("payment_type", as_index=False)["revenue"].sum()\
                         .sort_values("revenue", ascending=False)
        fig = px.bar(pay_df, x="payment_type", y="revenue",
                     title="Revenue by Payment Type",
                     labels={"payment_type": "Payment Type", "revenue": "Revenue (₹)"})
        st.plotly_chart(fig, use_container_width=True)

    with right:
        segment_df = filtered.groupby("customer_segment", as_index=False)["revenue"].sum()\
                             .sort_values("revenue", ascending=False)
        fig = px.bar(segment_df, x="customer_segment", y="revenue",
                     title="Revenue by Customer Segment",
                     labels={"customer_segment": "Customer Segment", "revenue": "Revenue (₹)"})
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Phase 3
# -----------------------------
elif page == "📋 Phase 3 — Business Questions":
    st.header("📋 Phase 3 — Business Questions & Hypotheses")
    st.write(
        "Analyze e-commerce sales, customer, product, payment, order and review data "
        "to identify revenue drivers and support evidence-based decisions."
    )

    questions = [
        "Does customer segment have a significant relationship with revenue?",
        "Does payment type have a significant relationship with order value?",
        "Does product price have a significant relationship with revenue?",
        "Does review score have a significant relationship with revenue?",
        "Does product category have a significant relationship with revenue?",
        "Does discount level have a significant relationship with revenue?",
    ]

    st.subheader("Key Business Questions")
    for q in questions:
        st.write("• " + q)

    hdf = pd.DataFrame({
        "Hypothesis": ["H1", "H2", "H3", "H4", "H5", "H6"],
        "Independent Variable": [
            "Customer Segment", "Payment Type", "Product Price",
            "Review Score", "Product Category", "Discount Level"
        ],
        "Dependent Variable": [
            "Revenue", "Order Value", "Revenue",
            "Revenue", "Revenue", "Revenue"
        ],
        "Test": [
            "Welch t-test", "Welch t-test", "Chi-square",
            "Chi-square", "Chi-square", "Welch t-test"
        ]
    })
    st.subheader("Hypothesis Framework")
    st.dataframe(hdf, use_container_width=True, hide_index=True)

# -----------------------------
# Phase 4
# -----------------------------
elif page == "📊 Phase 4 — Excel Dashboard":
    st.header("📊 Phase 4 — Excel Dashboard View")
    st.info(
        "Key Excel-dashboard views are reproduced here so the complete capstone "
        "can be demonstrated from one Streamlit application."
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Revenue", f"₹{total_revenue:,.0f}")
    c2.metric("Orders", f"{total_orders:,}")
    c3.metric("Delivered", f"{delivered:,}")
    c4.metric("Cancelled", f"{cancelled:,}")
    c5.metric("AOV", f"₹{aov:,.0f}")

    left, right = st.columns(2)
    with left:
        df = filtered.groupby("Category_name", as_index=False)["revenue"].sum()\
                     .sort_values("revenue", ascending=False).head(10)
        fig = px.bar(df, x="revenue", y="Category_name", orientation="h",
                     title="Top Categories by Revenue")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        df = filtered.groupby("customer_segment", as_index=False)["revenue"].sum()\
                     .sort_values("revenue", ascending=False)
        fig = px.bar(df, x="customer_segment", y="revenue",
                     title="Revenue by Customer Segment")
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Phase 5
# -----------------------------
elif page == "🔎 Phase 5 — Python EDA":
    st.header("🔎 Phase 5 — Python Exploratory Data Analysis")

    monthly = filtered.groupby("month", as_index=False)["revenue"].sum().sort_values("month")
    fig = px.line(monthly, x="month", y="revenue", markers=True,
                  title="Monthly Revenue Trend")
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        df = filtered.groupby("brand", as_index=False)["revenue"].sum()\
                     .sort_values("revenue", ascending=False).head(10)
        fig = px.bar(df, x="revenue", y="brand", orientation="h",
                     title="Top 10 Brands by Revenue")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        df = filtered.groupby("sub_category_name", as_index=False)["revenue"].sum()\
                     .sort_values("revenue", ascending=False).head(10)
        fig = px.bar(df, x="revenue", y="sub_category_name", orientation="h",
                     title="Top 10 Sub-Categories by Revenue")
        st.plotly_chart(fig, use_container_width=True)

    numeric_cols = [c for c in ["quantity", "unit_price", "discount(%)",
                                "shipping_cost", "revenue"] if c in filtered.columns]
    if len(numeric_cols) >= 2:
        st.subheader("Correlation Analysis")
        fig = px.imshow(filtered[numeric_cols].corr(), text_auto=".2f",
                        aspect="auto", title="Correlation Matrix")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Key EDA Findings")
    for text in [
        "Furniture is a major revenue-generating category in the project analysis.",
        "UPI is a prominent payment method in the observed transactions.",
        "New customers contribute substantial revenue.",
        "Selected products and brands contribute strongly to revenue.",
        "Review score and revenue show little/no linear correlation in the observed data.",
        "Unit price and revenue show a strong positive relationship."
    ]:
        st.write("• " + text)

# -----------------------------
# Phase 6
# -----------------------------
elif page == "🗄️ Phase 6 — SQL Analysis":
    st.header("🗄️ Phase 6 — SQL Analysis")
    st.info(
        "The SQL analysis was performed in MySQL. This page presents representative "
        "queries and the corresponding results using the cleaned data."
    )

    sql_options = {
        "Top Categories by Revenue": """SELECT p.Category_name,
SUM(oi.unit_price * oi.quantity * (1 - oi.`discount(%)` / 100)) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.Category_name
ORDER BY revenue DESC;""",
        "Revenue by Customer Segment": """SELECT c.customer_segment,
SUM(oi.unit_price * oi.quantity * (1 - oi.`discount(%)` / 100)) AS revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_segment
ORDER BY revenue DESC;""",
        "Revenue by Payment Type": """SELECT o.payment_type,
SUM(oi.unit_price * oi.quantity * (1 - oi.`discount(%)` / 100)) AS revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
GROUP BY o.payment_type
ORDER BY revenue DESC;"""
    }

    choice = st.selectbox("Select SQL analysis", list(sql_options.keys()))
    st.code(sql_options[choice], language="sql")

    if choice == "Top Categories by Revenue":
        result = filtered.groupby("Category_name", as_index=False)["revenue"].sum()\
                         .sort_values("revenue", ascending=False)
    elif choice == "Revenue by Customer Segment":
        result = filtered.groupby("customer_segment", as_index=False)["revenue"].sum()\
                         .sort_values("revenue", ascending=False)
    else:
        result = filtered.groupby("payment_type", as_index=False)["revenue"].sum()\
                         .sort_values("revenue", ascending=False)

    st.subheader("Query Result")
    st.dataframe(result, use_container_width=True, hide_index=True)

    st.subheader("SQL Techniques Demonstrated")
    for x in ["JOINs", "GROUP BY", "Aggregate functions", "ORDER BY",
              "Derived revenue calculation", "Business filtering"]:
        st.write("• " + x)

# -----------------------------
# Phase 7
# -----------------------------
elif page == "⚙️ Phase 7 — Feature Engineering":
    st.header("⚙️ Phase 7 — Feature Engineering & Data Preparation")

    feature_df = pd.DataFrame({
        "Feature": [
            "Revenue", "Price Category", "Discount Level",
            "Revenue Category", "Year", "Month"
        ],
        "Logic": [
            "Unit Price × Quantity × (1 − Discount/100)",
            "Unit price split using median",
            "Low ≤10%, Medium 10–20%, High >20%",
            "Revenue split using median",
            "Timestamp → year",
            "Timestamp → month"
        ],
        "Purpose": [
            "Business performance / target",
            "Price segmentation",
            "Discount segmentation",
            "Revenue classification",
            "Trend analysis",
            "Time analysis"
        ]
    })
    st.dataframe(feature_df, use_container_width=True, hide_index=True)

    cols = [c for c in [
        "order_id", "product_id", "quantity", "unit_price",
        "discount(%)", "revenue", "price_category",
        "discount_level", "revenue_category"
    ] if c in filtered.columns]

    st.subheader("Engineered Feature Preview")
    st.dataframe(filtered[cols].head(30), use_container_width=True, hide_index=True)

    feature = st.selectbox("Distribution", ["revenue", "unit_price", "quantity", "discount(%)"])
    fig = px.histogram(filtered, x=feature, nbins=40, title=f"Distribution of {feature}")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Phase 8
# -----------------------------
elif page == "📐 Phase 8 — Statistical Validation":
    st.header("📐 Phase 8 — Statistical Validation")
    st.write("Significance level: α = 0.05")

    stats_results = pd.DataFrame({
        "Hypothesis": [
            "H1: Customer Segment vs Revenue",
            "H2: Payment Type vs Order Value",
            "H3: Product Price vs Revenue",
            "H4: Review Score vs Revenue",
            "H5: Product Category vs Revenue",
            "H6: Discount Level vs Revenue"
        ],
        "Test": [
            "Welch t-test", "Welch t-test", "Chi-square",
            "Chi-square", "Chi-square", "Welch t-test"
        ],
        "Statistic": [
            1.426573, 1.182982, 4481.265350,
            0.902324, 4200.145137, -57.713971
        ],
        "P_Value": [
            0.153722, 0.236825, 0.000000,
            0.636888, 0.000000, 0.000000
        ],
        "Decision": [
            "Fail to reject H0", "Fail to reject H0", "Reject H0",
            "Fail to reject H0", "Reject H0", "Reject H0"
        ]
    })

    display_stats = stats_results.copy()
    display_stats["P_Value"] = display_stats["P_Value"].apply(
        lambda x: "< 0.001" if x == 0 else f"{x:.6f}"
    )
    st.dataframe(display_stats, use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Significant", "3 / 6")
    c2.metric("Not Significant", "3 / 6")
    c3.metric("Alpha", "0.05")

    st.success(
        "Significant: Product Price vs Revenue, Product Category vs Revenue, "
        "and Discount Level vs Revenue."
    )
    st.info(
        "Not significant: Customer Segment vs Revenue, Payment Type vs Order Value, "
        "and Review Score vs Revenue."
    )
    st.caption(
        "P-values reported as 0.000000 in the supplied summary are displayed as < 0.001."
    )

# -----------------------------
# Phase 9
# -----------------------------
elif page == "🤖 Phase 9 — Machine Learning":
    st.header("🤖 Phase 9 — Machine Learning & Model Evaluation")

    ml_results = pd.DataFrame({
        "Model": ["Linear Regression", "Decision Tree", "Random Forest"],
        "Train R²": [0.981835, 0.999988, 0.999999],
        "Validation R²": [0.982107, 0.999987, 0.999999],
        "Test R²": [0.984327, 0.999987, 0.999998],
        "Train RMSE": [1651.093985, 47.121376, 16.249275],
        "Validation RMSE": [1695.303206, 44.387574, 13.902307],
        "Test RMSE": [1730.005827, 46.500309, 15.743998],
        "Train MAE": [822.223033, 31.917545, 8.708007],
        "Validation MAE": [838.653833, 30.952835, 8.108302],
        "Test MAE": [854.128815, 31.915552, 8.569764]
    })

    st.dataframe(
        ml_results.style.format({
            "Train R²": "{:.6f}", "Validation R²": "{:.6f}", "Test R²": "{:.6f}",
            "Train RMSE": "{:,.2f}", "Validation RMSE": "{:,.2f}", "Test RMSE": "{:,.2f}",
            "Train MAE": "{:,.2f}", "Validation MAE": "{:,.2f}", "Test MAE": "{:,.2f}"
        }),
        use_container_width=True, hide_index=True
    )

    best_idx = ml_results["Test RMSE"].idxmin()
    best_model = ml_results.loc[best_idx, "Model"]
    best_r2 = ml_results.loc[best_idx, "Test R²"]
    best_rmse = ml_results.loc[best_idx, "Test RMSE"]
    best_mae = ml_results.loc[best_idx, "Test MAE"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Best Model", best_model)
    c2.metric("Test R²", f"{best_r2:.6f}")
    c3.metric("Test RMSE", f"{best_rmse:,.2f}")

    left, right = st.columns(2)
    with left:
        fig = px.bar(ml_results, x="Model", y="Test R²",
                     title="Test R² Comparison", text_auto=".6f")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.bar(ml_results, x="Model", y="Test RMSE",
                     title="Test RMSE Comparison", text_auto=".2f")
        st.plotly_chart(fig, use_container_width=True)

    st.success(
        f"Random Forest has the strongest reported test performance: "
        f"R² = {best_r2:.6f}, RMSE = {best_rmse:,.2f}, MAE = {best_mae:,.2f}."
    )
    st.warning(
        "Because the reported R² values are extremely high, review the feature "
        "engineering and validation setup for target leakage before operational use."
    )

# -----------------------------
# Power BI
# -----------------------------
elif page == "📈 Power BI Dashboard":
    st.header("📈 Power BI Dashboard")
    st.write(
        "Paste a Power BI Publish-to-web/embed URL to display your existing Power BI dashboard here."
    )

    secret_url = ""
    try:
        secret_url = st.secrets.get("POWER_BI_URL", "")
    except Exception:
        pass

    powerbi_url = st.text_input(
        "Power BI Publish-to-web URL",
        value=secret_url,
        placeholder="https://app.powerbi.com/view?r=..."
    )

    st.caption(
        "A public/embeddable Power BI URL is required. A normal private report URL "
        "generally requires sign-in and will not work as a public iframe."
    )

    if powerbi_url.strip().startswith("http"):
        html = f"""
        <iframe
            width="100%"
            height="760"
            src="{powerbi_url}"
            frameborder="0"
            allowFullScreen="true">
        </iframe>
        """
        components.html(html, height=780, scrolling=True)
    else:
        st.info("Enter the Power BI URL above to display the dashboard.")

# -----------------------------
# Insights
# -----------------------------
elif page == "💡 Insights & Recommendations":
    st.header("💡 Business Insights & Strategic Recommendations")

    data = [
        ("Revenue Drivers",
         "Product price, product category and discount level showed statistically significant relationships with revenue."),
        ("Category Performance",
         "Furniture is a major revenue-generating category in the project analysis."),
        ("Payment Behavior",
         "UPI is a prominent payment method in the observed transactions."),
        ("Customer Behavior",
         "New customers contribute substantial revenue, while H1 did not establish a statistically significant customer-segment effect."),
        ("Reviews",
         "Review score did not show a statistically significant relationship with revenue."),
        ("Machine Learning",
         "Random Forest produced the strongest reported model performance among the evaluated models.")
    ]

    for title, text in data:
        with st.expander(title, expanded=True):
            st.write(text)

    st.subheader("Strategic Recommendations")
    for r in [
        "Prioritize high-performing categories and brands in inventory and campaign planning.",
        "Use pricing and discount strategies carefully because price and discount level are statistically associated with revenue.",
        "Continue supporting preferred digital payment methods while monitoring conversion and order value.",
        "Use segmentation for targeting, but validate segment-level effects with statistical evidence.",
        "Treat review scores as a service-quality indicator rather than assuming a direct revenue impact.",
        "Perform further leakage checks and controlled validation before deploying the Random Forest model operationally."
    ]:
        st.write("• " + r)

    st.subheader("Overall Business Value")
    st.success(
        "The project combines BI reporting, Python EDA, SQL, feature engineering, "
        "statistical validation and machine learning into one decision-support workflow."
    )

# -----------------------------
# AI Assistant
# -----------------------------
elif page == "🤖 AI Business Assistant":
    st.header("🤖 AI Business Assistant")
    st.write(
        "Ask a business question about the currently filtered data. "
        "This assistant provides rule-based analytical answers from your dataset."
    )

    question = st.text_input(
        "Ask a question",
        placeholder="Which category has the highest revenue?"
    )

    if question:
        q = question.lower()

        if "highest revenue" in q and "categor" in q:
            x = filtered.groupby("Category_name")["revenue"].sum().sort_values(ascending=False)
            if len(x):
                st.success(f"Top category: {x.index[0]} — ₹{x.iloc[0]:,.0f}")

        elif "payment" in q and any(w in q for w in ["most", "highest", "used"]):
            x = filtered.groupby("payment_type")["order_id"].nunique().sort_values(ascending=False)
            if len(x):
                st.success(f"Most used payment type: {x.index[0]} — {x.iloc[0]:,} orders")

        elif "customer segment" in q and "revenue" in q:
            x = filtered.groupby("customer_segment")["revenue"].sum().sort_values(ascending=False)
            if len(x):
                st.success(f"Highest-revenue segment: {x.index[0]} — ₹{x.iloc[0]:,.0f}")

        elif "review" in q:
            rs = reviews.merge(filtered[["order_id"]].drop_duplicates(), on="order_id", how="inner")
            rs["review_score"] = pd.to_numeric(rs["review_score"], errors="coerce")
            avg = rs["review_score"].mean()
            st.success(f"Average review score: {avg:.2f}" if pd.notna(avg) else "No review data available.")

        elif "statistical" in q or "hypothesis" in q or "significant" in q:
            st.info(
                "3 of 6 hypotheses were statistically significant at α = 0.05: "
                "Product Price vs Revenue, Product Category vs Revenue, and Discount Level vs Revenue."
            )

        elif "model" in q or "random forest" in q:
            st.success(
                "Random Forest is the best reported model: Test R² = 0.999998, "
                "Test RMSE = 15.74, Test MAE = 8.57."
            )

        elif "revenue" in q:
            st.success(f"Revenue for the selected filters: ₹{total_revenue:,.0f}")

        elif "order" in q:
            st.success(f"Orders for the selected filters: {total_orders:,}")

        else:
            st.info(
                "Try asking about revenue, categories, payment types, customer segments, "
                "reviews, hypotheses, or the best ML model."
            )

st.divider()
st.caption(
    "E-Commerce Customer Analytics Capstone | Revenue = Unit Price × Quantity × (1 − Discount/100)"
)
