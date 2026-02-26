import pandas as pd
import numpy as np

#Merging the lead temperature and dormany logic into single reactivation engine while following best practices - vectorization, parameterization and modularization

#defing function that categoriez leads into diff temperatures and dormancy

"""
Process CRM DataFrame for lead reactivation.

    Parameters:
        df (pd.DataFrame): CRM data with 'Last_Contact_Date' and 'Lead_Type' columns
        dormancy_days (int): Days after which a lead is considered dormant
        temp_thresholds (list[int]): Upper bounds for Hot, Warm, Cold leads
                                     Example: [30, 90, 180]

    Returns:
        df_processed (pd.DataFrame): Original df with added columns:
                                     'Days_Since_Contact', 'Dormant', 'Lead_Temperature'
        buyer_dormant (pd.DataFrame): Dormant buyers
        seller_dormant (pd.DataFrame): Dormant sellers
        summary (dict): Summary metrics
"""

def process_crm(df: pd.DataFrame, dormancy_days: int=90,temp_thresholds: list=[30,90,180]):
    #Convert Last_Contact_date to datetime
    df['Last_Contact_Date']=pd.to_datetime(df['Last_Contact_Date'],errors='coerce')

    #Calculate days since last contact
    today=pd.Timestamp.today() #pulling today's date
    df['Days_Since_Contact']=(today-df['Last_Contact_Date']).dt.days#implementing date property and days sub-property

    #Determine Dormancy
    df['Dormant']=df['Days_Since_Contact']>dormancy_days

    #Determine Lead Temperature
    conditions=[
        df['Days_Since_Contact']<=temp_thresholds[0],#hot
        (df['Days_Since_Contact']>temp_thresholds[0]) & (df['Days_Since_Contact']<=temp_thresholds[1]),#warm
        (df['Days_Since_Contact']>temp_thresholds[1]) & (df['Days_Since_Contact']<=temp_thresholds[2]),#cold
        df['Days_Since_Contact']>temp_thresholds[2]#frozen
    ]

    choices=['Hot','Warm','Cold','Frozen']

    df['Lead_Temperature']=np.select(conditions,choices,default='Unknown')#using np.select for vectorized lead temperature assignment, defaulting to 'Unknown' for any edge cases

    #Segment dormant buyers and sellers
    buyer_mask=df['Lead_Type'].str.contains('Buyer',case=False,na=False) #using str.contains for case insensitivity and handling NaN
    seller_mask=df['Lead_Type'].str.contains('Seller',case=False,na=False)

    buyer_dormant=df[buyer_mask &df['Dormant']]
    seller_dormant=df[seller_mask &df['Dormant']]

    #Summary Metrics, using .sum for calculating total dormant as that table stores boolean values, this way it will ignore the 0s and count only the 1s
    summary={"total leads":len(df),"total dormant":int(df['Dormant'].sum()),"dormant buyers":len('buyer_dormant'),"dormant seller":len('seller_dormant')}

    return df,buyer_dormant,seller_dormant,summary








