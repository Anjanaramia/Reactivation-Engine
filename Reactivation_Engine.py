import pandas as pd
import numpy as np

def process_crm(
    df: pd.DataFrame,
    dormancy_days: int = 90,
    temp_thresholds: list = [30, 90, 180],
    average_deal_value: float = 50000,
    estimated_reactivation_rate: float = 5
):
    """
    Process CRM DataFrame for advanced lead reactivation.

    Returns:
        df_processed: Original df with additional columns
        buyer_dormant: Dormant buyers
        seller_dormant: Dormant sellers
        summary: Summary metrics
        follow_up_list: Leads needing immediate action
    """

    # ----------------------------
    # 1️⃣ Convert dates & handle missing
    # ----------------------------
    df['Last_Contact_Date'] = pd.to_datetime(df['Last_Contact_Date'], errors='coerce')
    today = pd.Timestamp.today()
    df['Days_Since_Contact'] = (today - df['Last_Contact_Date']).dt.days
    df['Days_Since_Contact'] = df['Days_Since_Contact'].fillna(9999)  # Treat missing as extremely dormant

    # Dormancy
    df['Dormant'] = df['Days_Since_Contact'] > dormancy_days

    # ----------------------------
    # 2️⃣ Lead Temperature
    # ----------------------------
    temp_conditions = [
        df['Days_Since_Contact'] <= temp_thresholds[0],  # Hot
        (df['Days_Since_Contact'] > temp_thresholds[0]) & (df['Days_Since_Contact'] <= temp_thresholds[1]),  # Warm
        (df['Days_Since_Contact'] > temp_thresholds[1]) & (df['Days_Since_Contact'] <= temp_thresholds[2]),  # Cold
        df['Days_Since_Contact'] > temp_thresholds[2]  # Frozen
    ]
    temp_choices = ['Hot', 'Warm', 'Cold', 'Frozen']
    df['Lead_Temperature'] = np.select(temp_conditions, temp_choices, default='Unknown')

    # ----------------------------
    # 3️⃣ Reactivation Score (Weighted)
    # ----------------------------
    lead_type_lower = df['Lead_Type'].str.lower()
    seller_mask = lead_type_lower == "seller"
    buyer_mask = lead_type_lower == "buyer"
    dormant_mask = df['Dormant']

    df['Reactivation_Score'] = 0

    # Dormancy-based weighting
    df.loc[df['Days_Since_Contact'] > 365, 'Reactivation_Score'] += 20  # Frozen
    df.loc[df['Days_Since_Contact'] > 180, 'Reactivation_Score'] += 10  # Cold

    # Lead type weighting
    df.loc[seller_mask, 'Reactivation_Score'] += 10
    df.loc[buyer_mask, 'Reactivation_Score'] += 5

    # Dormant bonus
    df.loc[dormant_mask, 'Reactivation_Score'] += 10

    # Optional: more weighting (deal value, tags) can be added here

    # ----------------------------
    # 4️⃣ Priority Logic
    # ----------------------------
    df['Priority'] = 'Low Priority'
    df.loc[df['Reactivation_Score'] >= 40, 'Priority'] = 'High Priority'
    df.loc[(df['Reactivation_Score'] >= 20) & (df['Reactivation_Score'] < 40), 'Priority'] = 'Medium Priority'

    # ----------------------------
    # 5️⃣ Suggested Actions
    # ----------------------------
    action_conditions = [
        seller_mask & dormant_mask & (df['Lead_Temperature'] == "Hot"),
        seller_mask & dormant_mask & (df['Lead_Temperature'] == "Warm"),
        seller_mask & dormant_mask & (df['Lead_Temperature'] == "Cold"),
        seller_mask & dormant_mask & (df['Lead_Temperature'] == "Frozen"),

        buyer_mask & dormant_mask & (df['Lead_Temperature'] == "Hot"),
        buyer_mask & dormant_mask & (df['Lead_Temperature'] == "Warm"),
        buyer_mask & dormant_mask & (df['Lead_Temperature'] == "Cold"),
        buyer_mask & dormant_mask & (df['Lead_Temperature'] == "Frozen"),
    ]
    action_choices = [
        "Call Immediately - Listing Opportunity",
        "Personal Check-in Call",
        "Send Market Update Email",
        "Add to Long-Term Seller Nurture",

        "Send Active Listings + Call",
        "Check Budget & Timeline",
        "Send 'Still Searching?' Email",
        "Add to Monthly Buyer Digest",
    ]
    df['Suggested_Action'] = np.select(action_conditions, action_choices, default="General Follow-Up")

    # ----------------------------
    # 6️⃣ Follow-Up List
    # ----------------------------
    follow_up_list = df[df['Priority'] != "Low Priority"].copy()

    # ----------------------------
    # 7️⃣ Revenue Opportunity Estimate
    # ----------------------------
    follow_up_list['Potential_Revenue'] = (
        follow_up_list['Reactivation_Score'] / 100 *
        average_deal_value *
        (estimated_reactivation_rate / 100)
    )

    # ----------------------------
    # 8️⃣ Segment Dormant Buyers & Sellers
    # ----------------------------
    buyer_dormant = df[buyer_mask & dormant_mask]
    seller_dormant = df[seller_mask & dormant_mask]

    # ----------------------------
    # 9️⃣ Summary Metrics
    # ----------------------------
    temperature_counts = df['Lead_Temperature'].value_counts().to_dict()
    summary = {
        "Total Leads": len(df),
        "Total Dormant": int(dormant_mask.sum()),
        "Dormant Buyers": len(buyer_dormant),
        "Dormant Sellers": len(seller_dormant),
        "High Priority Leads": int((df['Priority'] == "High Priority").sum()),
        "Lead Temperature Breakdown": temperature_counts,
        "Estimated Revenue Opportunity": follow_up_list['Potential_Revenue'].sum()
    }

    return df, buyer_dormant, seller_dormant, summary, follow_up_list
