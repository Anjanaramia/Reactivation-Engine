import pandas as pd
import numpy as np

def process_crm(
    df: pd.DataFrame,
    dormancy_days: int = 90,
    temp_thresholds: list = [30, 90, 180],
    score_thresholds: list = [30, 90, 180],
    score_values: list = [80, 60, 40, 20]
):
    """
    Process CRM DataFrame for lead reactivation.

    Parameters:
        df (pd.DataFrame): CRM data with 'Last_Contact_Date' and 'Lead_Type' columns
        dormancy_days (int): Days after which a lead is considered dormant
        temp_thresholds (list[int]): Upper bounds for Hot, Warm, Cold leads
                                     Example: [30, 90, 180]
        score_thresholds (list[int]): Upper bounds for Lead Score calculation
        score_values (list[int]): Lead Score values corresponding to thresholds

    Returns:
        df_processed (pd.DataFrame): Original df with added columns:
                                     'Days_Since_Contact', 'Dormant', 
                                     'Lead_Temperature', 'Lead_Score',
                                     'Priority', 'Suggested_Action'
        buyer_dormant (pd.DataFrame): Dormant buyers
        seller_dormant (pd.DataFrame): Dormant sellers
        summary (dict): Summary metrics including lead temperature breakdown
        follow_up_list (pd.DataFrame): Leads that need immediate follow-up
    """

    # ----------------------------
    # 1️⃣ Convert dates & calculate inactivity
    # ----------------------------
    df['Last_Contact_Date'] = pd.to_datetime(df['Last_Contact_Date'], errors='coerce')
    today = pd.Timestamp.today()
    df['Days_Since_Contact'] = (today - df['Last_Contact_Date']).dt.days

    # Determine Dormancy
    df['Dormant'] = df['Days_Since_Contact'] > dormancy_days

    # ----------------------------
    # 2️⃣ Lead Temperature (Hot/Warm/Cold/Frozen)
    # ----------------------------
    temp_conditions = [
        df['Days_Since_Contact'] <= temp_thresholds[0],  # Hot
        (df['Days_Since_Contact'] > temp_thresholds[0]) & (df['Days_Since_Contact'] <= temp_thresholds[1]),  # Warm
        (df['Days_Since_Contact'] > temp_thresholds[1]) & (df['Days_Since_Contact'] <= temp_thresholds[2]),  # Cold
        df['Days_Since_Contact'] > temp_thresholds[2]   # Frozen
    ]
    temp_choices = ['Hot', 'Warm', 'Cold', 'Frozen']
    df['Lead_Temperature'] = np.select(temp_conditions, temp_choices, default='Unknown')

    # ----------------------------
    # 3️⃣ Lead Score (Vectorized)
    # ----------------------------
    score_conditions = [
        df['Days_Since_Contact'] <= score_thresholds[0],
        (df['Days_Since_Contact'] > score_thresholds[0]) & (df['Days_Since_Contact'] <= score_thresholds[1]),
        (df['Days_Since_Contact'] > score_thresholds[1]) & (df['Days_Since_Contact'] <= score_thresholds[2]),
        df['Days_Since_Contact'] > score_thresholds[2]
    ]
    df['Lead_Score'] = np.select(score_conditions, score_values, default=0)

    # ----------------------------
    # 4️⃣ Masks for vectorization
    # ----------------------------
    lead_type_lower = df['Lead_Type'].str.lower()
    seller_mask = lead_type_lower == "seller"
    buyer_mask = lead_type_lower == "buyer"
    dormant_mask = df['Dormant']

    # ----------------------------
    # 5️⃣ Priority Logic
    # ----------------------------
    priority_conditions = [
        seller_mask & dormant_mask,  # Dormant Sellers
        dormant_mask                 # Dormant Buyers
    ]
    priority_choices = [
        "High Priority",
        "Medium Priority"
    ]
    df['Priority'] = np.select(priority_conditions, priority_choices, default="Low Priority")

    # ----------------------------
    # 6️⃣ Suggested Action (Lifecycle-Aware)
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
    # 7️⃣ Follow-Up List (Actionable Leads)
    # ----------------------------
    follow_up_list = df[df['Priority'] != "Low Priority"]

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
        "Lead Temperature Breakdown": temperature_counts
    }

    return df, buyer_dormant, seller_dormant, summary, follow_up_list
