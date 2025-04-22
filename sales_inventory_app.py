import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Sales & Inventory Dashboard", layout="wide")

# Adding title using HTML <h1> tag
st.markdown(
    "<h1 style='text-align: center; color: #4CAF50;'>🛒 Simple Sales & Inventory Dashboard</h1>",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
    except:
        df = pd.DataFrame(columns=["Product", "Stock", "Sold", "Date"])
    return df


data = load_data()

# Top Section: Add New Sales Entry and Inventory Metrics
with st.container():
    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("➕ Add New Sales Entry")
        with st.form("entry_form", clear_on_submit=True):
            product = st.text_input("Product Name")
            stock = st.number_input("Stock", min_value=0, step=1)
            sold = st.number_input("Sold", min_value=0, step=1)
            date = st.date_input("Date")
            submitted = st.form_submit_button("Add Entry")

            if submitted and product:
                new_entry = {
                    "Product": product,
                    "Stock": stock,
                    "Sold": sold,
                    "Date": date,
                }
                data = pd.concat([data, pd.DataFrame([new_entry])], ignore_index=True)
                data.to_csv("data.csv", index=False)
                st.success(f"Added {product} record!")

    with col2:
        st.subheader("📊 Inventory Metrics")
        if not data.empty:
            total_sold = data["Sold"].sum()
            total_stock = data["Stock"].sum()
            remaining = total_stock - total_sold

            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric("Total Stocked", total_stock)
            mcol2.metric("Total Sold", total_sold)
            mcol3.metric("Remaining Stock", remaining)
        else:
            st.info("No data available.")

# Product Filter
st.subheader("🔍 Filter by Product")
product_filter = st.selectbox(
    "Choose a product", options=["All"] + sorted(data["Product"].unique())
)

filtered_data = data.copy()
if product_filter != "All":
    filtered_data = data[data["Product"] == product_filter]

# Graph and Table Side-by-Side (60% - 40%)
st.subheader("📊 Sales Overview")

gcol1, gcol2 = st.columns([3, 2])

with gcol1:
    if not filtered_data.empty:
        st.markdown("### 📈 Sales Over Time")
        filtered_data["Date"] = pd.to_datetime(filtered_data["Date"])
        daily_sales = filtered_data.groupby("Date")["Sold"].sum()

        fig, ax = plt.subplots(figsize=(8, 4))
        daily_sales.plot(kind="line", marker="o", ax=ax, color="green")
        ax.set_ylabel("Units Sold")
        ax.set_title("Daily Sales")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
    else:
        st.warning("No data available to display graph.")

with gcol2:
    st.markdown("### 🧾 Full Data Table")
    st.dataframe(filtered_data, use_container_width=True)

# Pie Chart Comparison Section
if not data.empty:
    st.subheader("🥧 Product-wise Sales Distribution")

    unique_products = sorted(data["Product"].unique())
    pie_selection = st.multiselect(
        "Select one or more products to compare (leave empty to show top 10)",
        unique_products,
    )

    pie_data = data.copy()

    # Limit to top 10 products by sales
    top_10_products = data.groupby("Product")["Sold"].sum().nlargest(10)

    if pie_selection:
        pie_data = pie_data[pie_data["Product"].isin(pie_selection)]
        sales_summary = pie_data.groupby("Product")["Sold"].sum()

        if not sales_summary.empty:
            fig2, ax2 = plt.subplots(
                figsize=(6, 6)
            )  # Adjust size for better visual balance
            sales_summary.plot(
                kind="pie",
                autopct="%1.1f%%",
                ax=ax2,
                startangle=90,
                fontsize=8,  # Smaller font for better readability
                labels=sales_summary.index,
                wedgeprops={
                    "width": 0.6
                },  # Adjust width of the wedges to make it more appealing
            )
            ax2.set_ylabel("")  # Remove label
            title = (
                "Sales Comparison"
                if len(pie_selection) > 1
                else f"Sales Share: {pie_selection[0]}"
            )
            ax2.set_title(title)
            ax2.set_aspect("equal")  # Ensure pie chart is circular
            # Move legend to the right, adjust font size
            ax2.legend(
                loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8, title="Products"
            )
            st.pyplot(fig2)
        else:
            st.info("No sales data available for selected product(s).")

    else:
        # Show top 10 product-wise pie chart
        if not top_10_products.empty:
            fig3, ax3 = plt.subplots(
                figsize=(6, 6)
            )  # Adjust size for better visual balance
            top_10_products.plot(
                kind="pie",
                autopct="%1.1f%%",
                ax=ax3,
                startangle=90,
                fontsize=8,
                wedgeprops={"width": 0.6},
            )
            ax3.set_ylabel("")  # Remove label
            ax3.set_title("Top 10 Products by Sales")
            ax3.set_aspect("equal")  # Ensure pie chart is circular
            # Move legend to the right, adjust font size
            ax3.legend(
                loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8, title="Products"
            )
            st.pyplot(fig3)
        else:
            st.info("No data available to show pie chart.")
else:
    st.info("No data available to show pie chart.")
