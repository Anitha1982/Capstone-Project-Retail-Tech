import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="E-Commerce Sales & Customer Insights",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 E-Commerce Sales & Customer Insights Dashboard")
st.caption("E-Commerce Analytics | 2021–2025")

@st.cache_data
def load_data():
    customers = pd.read_csv("cleaned_customers.csv")
    orders = pd.read_csv("cleaned_orders.csv")
    items = pd.read_csv("cleaned_order_items.csv")
    reviews = pd.read_csv("cleaned_order_reviews.csv")
    products = pd.read_csv("cleaned_products.csv")

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"], errors="coerce"
    )
    orders["year"] = orders["order_purchase_timestamp"].dt.year
    orders["month"] = orders["order_purchase_timestamp"].dt.to_period("M").astype(str)

    items["quantity"] = pd.to_numeric(items["quantity"], errors="coerce").fillna(0)
    items["unit_price"] = pd.to_numeric(items["unit_price"], errors="coerce").fillna(0)
    items["discount(%)"] = pd.to_numeric(items["discount(%)"], errors="coerce").fillna(0)

    # Revenue after discount
    items["revenue"] = (
        items["unit_price"] * items["quantity"] *
        (1 - items["discount(%)"] / 100)
    )

    sales = (
        items.merge(
            orders[["order_id", "customer_id", "order_status", "payment_type",
                    "order_purchase_timestamp", "year", "month"]],
            on="order_id", how="left"
        )
        .merge(
            customers[["customer_id", "gender", "age_group", "customer_segment"]],
            on="customer_id", how="left"
        )
        .merge(
            products[["product_id", "Category_name", "sub_category_name",
                      "brand", "selling_price", "stock_availability"]],
            on="product_id", how="left"
        )
    )
    return customers, orders, items, reviews, products, sales

customers, orders, items, reviews, products, sales = load_data()

# Sidebar filters
st.sidebar.header("🔎 Filters")

years = sorted(sales["year"].dropna().unique().tolist())
selected_years = st.sidebar.multiselect("Year", years, default=years)

categories = sorted(sales["Category_name"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Category", categories, default=categories
)

segments = sorted(sales["customer_segment"].dropna().unique().tolist())
selected_segments = st.sidebar.multiselect(
    "Customer Segment", segments, default=segments
)

payments = sorted(sales["payment_type"].dropna().unique().tolist())
selected_payments = st.sidebar.multiselect(
    "Payment Type", payments, default=payments
)

statuses = sorted(sales["order_status"].dropna().unique().tolist())
selected_statuses = st.sidebar.multiselect(
    "Order Status", statuses, default=statuses
)

filtered = sales[
    sales["year"].isin(selected_years)
    & sales["Category_name"].isin(selected_categories)
    & sales["customer_segment"].isin(selected_segments)
    & sales["payment_type"].isin(selected_payments)
    & sales["order_status"].isin(selected_statuses)
].copy()

# KPI calculations
total_revenue = filtered["revenue"].sum()
total_orders = filtered["order_id"].nunique()
total_quantity = filtered["quantity"].sum()
aov = total_revenue / total_orders if total_orders else 0
avg_discount = filtered["discount(%)"].mean() if len(filtered) else 0

delivered = filtered.loc[
    filtered["order_status"].str.lower().eq("delivered"), "order_id"
].nunique()
cancelled = filtered.loc[
    filtered["order_status"].str.lower().eq("cancelled"), "order_id"
].nunique()
shipped = filtered.loc[
    filtered["order_status"].str.lower().eq("shipped"), "order_id"
].nunique()
returned = filtered.loc[
    filtered["order_status"].str.lower().eq("returned"), "order_id"
].nunique()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
c2.metric("Total Orders", f"{total_orders:,}")
c3.metric("Average Order Value", f"₹{aov:,.0f}")
c4.metric("Quantity Sold", f"{total_quantity:,.0f}")
c5.metric("Avg Discount", f"{avg_discount:.2f}%")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview", "📦 Sales & Products", "👥 Customers", "⭐ Reviews & Data"
])

with tab1:
    st.subheader("Order Status Summary")
    a, b, c, d = st.columns(4)
    a.metric("Delivered", f"{delivered:,}")
    b.metric("Cancelled", f"{cancelled:,}")
    c.metric("Shipped", f"{shipped:,}")
    d.metric("Returned", f"{returned:,}")

    left, right = st.columns(2)

    with left:
        monthly = (
            filtered.groupby("month", as_index=False)["revenue"]
            .sum()
            .sort_values("month")
        )
        fig = px.line(
            monthly, x="month", y="revenue",
            markers=True,
            title="Monthly Revenue Trend",
            labels={"month": "Month", "revenue": "Revenue (₹)"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        status_df = (
            filtered.groupby("order_status", as_index=False)["order_id"]
            .nunique()
            .sort_values("order_id", ascending=False)
        )
        fig = px.bar(
            status_df, x="order_status", y="order_id",
            title="Orders by Status",
            labels={"order_status": "Order Status", "order_id": "Orders"}
        )
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:
        pay_df = (
            filtered.groupby("payment_type", as_index=False)["revenue"]
            .sum()
            .sort_values("revenue", ascending=False)
        )
        fig = px.bar(
            pay_df, x="payment_type", y="revenue",
            title="Revenue by Payment Type",
            labels={"payment_type": "Payment Type", "revenue": "Revenue (₹)"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        cat_df = (
            filtered.groupby("Category_name", as_index=False)["revenue"]
            .sum()
            .sort_values("revenue", ascending=False)
            .head(10)
        )
        fig = px.bar(
            cat_df, x="revenue", y="Category_name",
            orientation="h",
            title="Top Categories by Revenue",
            labels={"Category_name": "Category", "revenue": "Revenue (₹)"}
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Sales & Product Performance")

    left, right = st.columns(2)

    with left:
        brand_df = (
            filtered.groupby("brand", as_index=False)["revenue"]
            .sum()
            .sort_values("revenue", ascending=False)
            .head(10)
        )
        fig = px.bar(
            brand_df, x="revenue", y="brand",
            orientation="h",
            title="Top 10 Brands by Revenue",
            labels={"brand": "Brand", "revenue": "Revenue (₹)"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        subcat_df = (
            filtered.groupby("sub_category_name", as_index=False)["revenue"]
            .sum()
            .sort_values("revenue", ascending=False)
            .head(10)
        )
        fig = px.bar(
            subcat_df, x="revenue", y="sub_category_name",
            orientation="h",
            title="Top 10 Sub-Categories by Revenue",
            labels={"sub_category_name": "Sub-Category", "revenue": "Revenue (₹)"}
        )
        st.plotly_chart(fig, use_container_width=True)

    scatter_df = (
        filtered.groupby("product_id", as_index=False)
        .agg(
            quantity=("quantity", "sum"),
            revenue=("revenue", "sum"),
            unit_price=("unit_price", "mean")
        )
    )
    fig = px.scatter(
        scatter_df, x="quantity", y="revenue",
        size="unit_price",
        hover_data=["product_id"],
        title="Quantity vs Revenue",
        labels={"quantity": "Quantity Sold", "revenue": "Revenue (₹)"}
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Customer Insights")

    segment_df = (
        filtered.groupby("customer_segment", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )
    fig = px.bar(
        segment_df, x="customer_segment", y="revenue",
        title="Revenue by Customer Segment",
        labels={"customer_segment": "Customer Segment", "revenue": "Revenue (₹)"}
    )
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:
        gender_df = (
            filtered.groupby("gender", as_index=False)["revenue"]
            .sum()
            .sort_values("revenue", ascending=False)
        )
        fig = px.pie(
            gender_df, names="gender", values="revenue",
            title="Revenue by Gender"
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        age_df = (
            filtered.groupby("age_group", as_index=False)["revenue"]
            .sum()
            .sort_values("revenue", ascending=False)
        )
        fig = px.bar(
            age_df, x="age_group", y="revenue",
            title="Revenue by Age Group",
            labels={"age_group": "Age Group", "revenue": "Revenue (₹)"}
        )
        st.plotly_chart(fig, use_container_width=True)

    customer_summary = (
        filtered.groupby(["customer_id", "customer_segment"], as_index=False)
        .agg(
            total_spending=("revenue", "sum"),
            orders=("order_id", "nunique"),
            quantity=("quantity", "sum")
        )
        .sort_values("total_spending", ascending=False)
    )
    st.subheader("Top Customers by Spending")
    st.dataframe(customer_summary.head(20), use_container_width=True)

with tab4:
    st.subheader("Review Analysis")

    review_sales = reviews.merge(
        filtered[["order_id"]].drop_duplicates(),
        on="order_id", how="inner"
    )
    review_sales["review_score"] = pd.to_numeric(
        review_sales["review_score"], errors="coerce"
    )

    score_df = (
        review_sales.groupby("review_score", as_index=False)["order_id"]
        .nunique()
        .sort_values("review_score")
    )
    fig = px.bar(
        score_df, x="review_score", y="order_id",
        title="Review Score Distribution",
        labels={"review_score": "Review Score", "order_id": "Orders"}
    )
    st.plotly_chart(fig, use_container_width=True)

    st.metric(
        "Average Review Score",
        f"{review_sales['review_score'].mean():.2f}" if len(review_sales) else "N/A"
    )

    st.subheader("Dataset Summary")
    summary = pd.DataFrame({
        "Dataset": [
            "Customers", "Geolocation", "Orders",
            "Order Items", "Order Reviews", "Products"
        ],
        "Rows": [
            len(customers), 155545, len(orders),
            len(items), len(reviews), len(products)
        ]
    })
    st.dataframe(summary, use_container_width=True)

st.divider()
st.caption(
    "Built for the E-Commerce Customer Analytics Capstone Project. "
    "Revenue is calculated as unit price × quantity after discount."
)