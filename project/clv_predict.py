import pandas as pd
df = pd.read_csv("shopping_behavior_updated.csv")
def convert_frequency_to_number(str):
    if str == 'Annually':
        return 1
    elif str == "Bi-Weekly":
        return 104
    elif str == "Every 3 Months":
        return 4
    elif str == "Fortnightly":
        return 24
    elif str == "Monthly":
        return 12
    elif str == "Quarterly":
        return 4
    elif str == "Weekly":
        return 52
    else:
        return 0

df['purchase_frequency_num'] = df['Frequency of Purchases'].apply(convert_frequency_to_number)
df['use_period'] = df['purchase_frequency_num']/df['Previous Purchases']
df['CLV'] = (df['Purchase Amount (USD)']*df['purchase_frequency_num']-df['Promo Code Used'].apply(lambda x:30 if x=="Yes" else 0))+df['Review Rating'].apply(lambda x: x*300)+df['Subscription Status'].apply(lambda x : 500 if x=="Yes" else 0)
df['Subscription Status_num'] = df['Subscription Status'].apply(lambda x : 1 if x=="Yes" else 0)
df['Promo code Used_num'] = df['Promo Code Used'].apply(lambda x:1 if x=="Yes" else 0)
clv_percentiles = df['CLV'].quantile([0.33,0.66])
df['CLV_group'] = pd.cut(df['CLV'],bins=[df['CLV'].min(),clv_percentiles.iloc[0],clv_percentiles.iloc[1],df['CLV'].max()], labels = ['Low CLV','Medium CLV','High CLV'])
grouped_df = df.groupby('CLV_group').agg({
    'Purchase Amount (USD)': 'mean',
    'purchase_frequency_num': 'mean',
    'CLV': 'mean',
    'Review Rating' : 'mean',
    'use_period' : 'mean',
    'Subscription Status_num' : 'sum'
})

print(grouped_df)