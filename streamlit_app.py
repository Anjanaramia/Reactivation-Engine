import streamlit as st
import pandas as pd
from Reactivation_Engine import process_crm  # your upgraded function

# ----------------------------
# 1️⃣ App Title
# ----------------------------
st.title("CRM Lead Reactivation Engine v2 🚀")
st.write("Upload your CRM CSV to analyze lead dormancy, reactivation score, and revenue potential.")

# ----------------------------
# 2️⃣ Upload CSV
# ----------------------------
uploaded_file = st.file_uploader("Upload your CRM CSV", type=['csv'])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # ----------------------------
    # 3️⃣ Sidebar Controls
    # ----------------------------
    st.sidebar.header("Settings")
    dormancy_days = st.sidebar.slider("Dormant after X days", 30, 180, 90)

    # Temperature thresholds
    hot_upper = st.sidebar.slider('Hot Upper Bound (days)', 1, 100, 30)
    warm_upper = st.sidebar.slider('Warm Upper Bound (days)', hot_upper + 1, 180, 90)
    cold_upper = st.sidebar.slider('Cold Upper Bound (days)', warm_upper + 1, 365, 180)
    temp_thresholds = [hot_upper, warm_upper, cold_upper]

    # Revenue inputs
    average_deal_value = st.sidebar.number_input("Average Deal Value ($)", 1000, 1000000, 50000)
    estimated_reactivation_rate = st.sidebar.slider("Estimated Reactivation Rate (%)", 1, 50, 5)

    # ----------------------------
    # 4️⃣ Process CRM
    # ----------------------------
    df_processed, buyer_dormant, seller_dormant, summary, follow_up_list = process_crm(
        df,
        dormancy_days=dormancy_days,
        temp_thresholds=temp_thresholds,
        average_deal_value=average_deal_value,
        estimated_reactivation_rate=estimated_reactivation_rate
    )

    # ----------------------------
    # 5️⃣ Display Processed Data
    # ----------------------------
    st.subheader("Processed CRM Data")
    st.dataframe(df_processed)

    # ----------------------------
    # 6️⃣ Follow-Up List
    # ----------------------------
    with st.expander("Follow-Up List (High + Medium Priority Leads)"):
        st.dataframe(follow_up_list[['Lead_Name','Lead_Type','Lead_Temperature','Reactivation_Score','Priority','Suggested_Action','Potential_Revenue']])

    # ----------------------------
    # 7️⃣ Top Leads by Reactivation Score
    # ----------------------------
    st.subheader("Top Leads by Reactivation Score")
    top_leads = follow_up_list.sort_values('Reactivation_Score', ascending=False).head(20)
    st.dataframe(top_leads[['Lead_Name','Lead_Type','Days_Since_Contact','Lead_Temperature','Reactivation_Score','Priority','Suggested_Action','Potential_Revenue']])

    # ----------------------------
    # 8️⃣ Summary Metrics
    # ----------------------------
    st.subheader("Summary Metrics")
    st.write(summary)

    # ----------------------------
    # 9️⃣ Charts
    # ----------------------------
    st.subheader("Lead Temperature Distribution")
    st.bar_chart(df_processed['Lead_Temperature'].value_counts())

    st.subheader("Lead Priority Distribution")
    st.bar_chart(df_processed['Priority'].value_counts())

    st.subheader("Revenue Opportunity Distribution")
    st.bar_chart(follow_up_list['Potential_Revenue'])

else:
    st.info("Please upload a CSV file to process your CRM leads.")
