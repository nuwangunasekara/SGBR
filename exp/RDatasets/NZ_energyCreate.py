import pandas as pd
from sklearn.preprocessing import MinMaxScaler


# Create DataFrame from the string (in practice, you'd use pd.read_csv('filename.csv'))
df = pd.read_csv("NZ_energy_RAW.csv")

# Get min and max year for normalization
min_year = df['Year'].min()
max_year = df['Year'].max()

# Normalize the Year column using min-max normalization
scaler = MinMaxScaler()
df['Year'] = scaler.fit_transform(df[['Year']])

# Keep the original field order
original_columns = df.columns.tolist()

# Print the normalized data with original field order
print(df[original_columns].to_csv(index=False))

df[original_columns].to_csv('NZ_energy.csv', index=False)