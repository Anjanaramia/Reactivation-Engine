import streamlit as st
from Reactivation_Engine import process_crm
import pandas as pd

#Streamlit app for lead reactivation insights

#asking user to upload csv format data file

uploaded_file=st.file_uploader("Upload your CRM CSV",type=['csv'])

#pass the datafile to pandas
if uploaded_file:
    df=pd.read_csv(uploaded_file)

    #determine app's sidebar controls
    dormancy_days=st.sidebar.slider("Dormant after X days",30,180,90)
    temp_thresholds=[st.sidebar.slider('Hot Upper Bound',1,100,30),
                 st.sidebar.slider('Warm Upper Bound',31,180,90),
                 st.sidebar.slider('Cold Upper Bound',91,365,180)]

    df_processed,buyer_dormant,seller_dormant,summary=process_crm(df,dormancy_days=dormancy_days,temp_thresholds=temp_thresholds)

    st.write("Processed Data:")
    st.dataframe(df_processed)

    st.write("Summary:")
    st.write(summary)
else:
    st.info("Please upload a CSV file to process:")




