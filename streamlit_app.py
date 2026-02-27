import streamlit as st
from Reactivation_Engine import process_crm
import pandas as pd

# ----------------------------
# 1️⃣ App Title
# ----------------------------
st.title("CRM Lead Reactivation Engine 🚀")
st.write("Upload your CRM CSV to analyze lead dormancy, temperature, lead scoring, and follow-up actions.")

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

    # Hot < Warm < Cold
    hot_upper = st.sidebar.slider('Hot Upper Bound (days)', 1, 100, 30)
    warm_upper = st.sidebar.slider('Warm Upper Bound (days)', hot_upper + 1, 180, 90)
    cold_upper = st.sidebar.slider('Cold Upper Bound (days)', warm_upper + 1, 365, 180)
    temp_thresholds = [hot_upper, warm_upper, cold_upper]

    # ----------------------------
    # 4️⃣ Process CRM
    # ----------------------------
    df_processed, buyer_dormant, seller_dormant, summary, follow_up_list = process_crm(
        df,
        dormancy_days=dormancy_days,
        temp_thresholds=temp_thresholds
    )

    # ----------------------------
    # 5️⃣ Show Processed Data
    # ----------------------------
    st.subheader("Processed CRM Data")
    st.dataframe(df_processed)

    # ----------------------------
    # 6️⃣ Follow-Up List (Actionable Leads)
    # ----------------------------
    with st.expander("Follow-Up List (High + Medium Priority Leads)"):
        st.dataframe(follow_up_list[['Lead_Name','Lead_Type','Lead_Temperature','Lead_Score','Priority','Suggested_Action']])

    # ----------------------------
    # 7️⃣ Suggested Actions for Leads
    # ----------------------------
    with st.expander("Suggested Actions for Actionable Leads"):
        st.dataframe(follow_up_list[['Lead_Name','Lead_Type','Lead_Temperature','Priority','Suggested_Action']])

    # ----------------------------
    # 8️⃣ Lead Scoring / Top Leads
    # ----------------------------
    st.subheader("Top Leads by Lead Score")
    top_leads = df_processed.sort_values('Lead_Score', ascending=False).head(20)
    st.dataframe(top_leads[['Lead_Name','Lead_Type','Days_Since_Contact','Lead_Temperature','Lead_Score','Priority','Suggested_Action']])

    # ----------------------------
    # 9️⃣ Summary Metrics
    # ----------------------------
    st.subheader("Summary Metrics")
    st.write(summary)

    # ----------------------------
    # 🔟 Charts for Visual Insights
    # ----------------------------
    st.subheader("Lead Temperature Distribution")
    st.bar_chart(df_processed['Lead_Temperature'].value_counts())

    st.subheader("Lead Priority Distribution")
    st.bar_chart(df_processed['Priority'].value_counts())

else:
    st.info("Please upload a CSV file to process your CRM leads.")
