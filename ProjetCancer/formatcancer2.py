import pandas as pd

file_path = 'updated_cancerSEER.csv'
seer_data = pd.read_csv(file_path)

seer_data['Age'] = seer_data['Age'].astype(str).replace({'90+ years': '90'})

seer_data['Age'] = seer_data['Age'].str.extract(r'(\d+)').astype(int)

seer_data = seer_data[['Age', 'Sex', 'Type', 'Lifestatus', 'Race']]

seer_data.to_csv('final_cancerSEER.csv', index=False)

print("Data cleaning and formatting completed. Saved as 'final_cancerSEER.csv'.")
