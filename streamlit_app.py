import streamlit as st
import pandas as pd
from Reactivation_Engine import process_crm

st.set_page_config(page_title="CRM Reactivation Engine V3", layout="wide")

st.title("🚀 CRM Lead Reactivation Engine V3")

st.sidebar.header("Settings")

dormancy_days = st.sidebar.slider("Dormant After X Days", 30, 365, 90)
hot_upper = st.sidebar.slider("Hot Upper Bound (days)", 1, 60, 30)
warm_upper = st.sidebar.slider("Warm Upper Bound (days)", 30, 180, 90)
cold_upper = st.sidebar.slider("Cold Upper Bound (days)", 90, 365, 180)

average_deal_value = st.sidebar.number_input(
    "Average Deal Value ($)", value=50000
)

estimated_reactivation_rate = st.sidebar.slider(
    "Estimated Reactivation Rate (%)", 1, 20, 5
)

uploaded_file = st.file_uploader("Upload your CRM CSV", type=["csv"])

if uploaded_file:

    try:
        df = pd.read_csv(uploaded_file)

        df_processed, buyer_dormant, seller_dormant, summary, follow_up_list = process_crm(
            df,
            dormancy_days=dormancy_days,
            hot_upper=hot_upper,
            warm_upper=warm_upper,
            cold_upper=cold_upper,
            average_deal_value=average_deal_value,
            estimated_reactivation_rate=estimated_reactivation_rate
        )

        st.success("CRM Processed Successfully ✅")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Leads", summary["Total_Leads"])
        col2.metric("Dormant Leads", summary["Dormant_Leads"])
        col3.metric("Projected Reactivations", summary["Projected_Reactivations"])
        col4.metric("Projected Revenue ($)", summary["Projected_Revenue"])

        st.subheader("📋 Follow-Up Priority List")
        st.dataframe(follow_up_list)

        st.subheader("🟢 Dormant Buyers")
        st.dataframe(buyer_dormant)

        st.subheader("🔵 Dormant Sellers")
        st.dataframe(seller_dormant)

    except Exception as e:
        st.error("An error occurred while processing the CRM.")
        st.exception(e)

