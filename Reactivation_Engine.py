import pandas as pd
import numpy as np


def standardize_columns(df):
    """
    Automatically maps common CRM column variations
    to required internal column names.
    """

    column_map = {
        'lead_name': 'Lead_Name',
        'name': 'Lead_Name',
        'full_name': 'Lead_Name',

        'lead_type': 'Lead_Type',
        'type': 'Lead_Type',

        'last_contact_date': 'Last_Contact_Date',
        'last_contact': 'Last_Contact_Date',
        'contact_date': 'Last_Contact_Date'
    }

    df.columns = df.columns.str.strip().str.lower()

    for col in df.columns:
        if col in column_map:
            df.rename(columns={col: column_map[col]}, inplace=True)

    return df


def process_crm(
    df,
    dormancy_days=90,
    hot_upper=30,
    warm_upper=90,
    cold_upper=180,
    average_deal_value=50000,
    estimated_reactivation_rate=5
):
    df = standardize_columns(df)

    required_cols = ['Lead_Name', 'Lead_Type', 'Last_Contact_Date']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df['Last_Contact_Date'] = pd.to_datetime(df['Last_Contact_Date'], errors='coerce')
    today = pd.to_datetime("today")
    df['Days_Since_Contact'] = (today - df['Last_Contact_Date']).dt.days.clip(lower=0)

    # Temperature Classification
    def classify(days):
        if pd.isna(days):
            return "Unknown"
        elif days <= hot_upper:
            return "Hot"
        elif days <= warm_upper:
            return "Warm"
        elif days <= cold_upper:
            return "Cold"
        else:
            return "Dormant"

    df['Temperature'] = df['Days_Since_Contact'].apply(classify)

    # Next Action Recommendations
    def recommend_action(temp):
        if temp == 'Hot':
            return 'Call / Personalized Email'
        elif temp == 'Warm':
            return 'Email / SMS Follow-up'
        elif temp == 'Cold':
            return 'Nurture via Drip Campaign'
        elif temp == 'Dormant':
            return 'Skip for Now'
        else:
            return 'Check Lead Info'

    df['Next_Action'] = df['Temperature'].apply(recommend_action)

    # Dormancy flag
    df['Is_Dormant'] = df['Days_Since_Contact'] > dormancy_days

    # Revenue Opportunity Calculation
    dormant_count = df['Is_Dormant'].sum()
    projected_reactivations = dormant_count * (estimated_reactivation_rate / 100)
    projected_revenue = projected_reactivations * average_deal_value

    summary = {
        "Total_Leads": len(df),
        "Dormant_Leads": int(dormant_count),
        "Projected_Reactivations": int(projected_reactivations),
        "Projected_Revenue": int(projected_revenue)
    }

    # Buyer / Seller Split
    buyer_dormant = df[(df['Lead_Type'].str.lower() == 'buyer') & df['Is_Dormant']]
    seller_dormant = df[(df['Lead_Type'].str.lower() == 'seller') & df['Is_Dormant']]

    # Follow-up priority list (sorted by longest inactivity)
    follow_up_list = df[df['Is_Dormant']].sort_values(by='Days_Since_Contact', ascending=False)

    # Hot Leads for campaigns
    hot_leads = df[df['Temperature'] == 'Hot']

    # Return all enriched outputs
    return df, buyer_dormant, seller_dormant, summary, follow_up_list, hot_leads
