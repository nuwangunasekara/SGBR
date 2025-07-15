import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv("DemandF.csv")

# Map normalized_year to actual years
year_mapping = {0.0: 2011, 0.5: 2012, 1.0: 2013}
df['year'] = df['normalized_year'].map(year_mapping)

# Combine year and week into datetime format
df['time'] = pd.to_datetime(df['year'].astype(str) + '-W' + df['week_number'].astype(str) + '-1', format='%Y-W%W-%w')

# Group by time and sum units_sold
units_sold_over_time = df.groupby('time')['units_sold'].sum().reset_index()

# Plot
plt.figure(figsize=(14, 6))
plt.plot(units_sold_over_time['time'], units_sold_over_time['units_sold'], marker='o')
plt.title('Units Sold Over Time')
plt.xlabel('Time (Year-Week)')
plt.ylabel('Units Sold')
plt.grid(True)
plt.tight_layout()
plt.show()
