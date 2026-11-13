import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the data
df = pd.read_csv('world-happiness-report.csv')

# Task A.2: Line plot for time/trend analysis
# Calculate average ladder score by year
average_by_year = df.groupby('year')['Life Ladder'].mean().reset_index()

# Plot 1: Global average trend
plt.figure(figsize=(12, 6))
plt.plot(average_by_year['year'], average_by_year['Life Ladder'], 
         marker='o', linewidth=2, markersize=8, color='steelblue')
plt.title('Global Average Life Ladder Score Over Time (2005-2020)', fontsize=16, fontweight='bold')
plt.xlabel('Year', fontsize=14)
plt.ylabel('Average Life Ladder Score', fontsize=14)
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Plot 2: Select specific countries for comparison
selected_countries = ['United States', 'Canada', 'United Kingdom', 'Germany', 'France', 'Japan', 'Australia']

# Filter for selected countries (adjusting for potential naming differences)
available_countries = [c for c in selected_countries if c in df['Country name'].unique()]
if not available_countries:
    # If those exact names aren't available, let's use some that are
    available_countries = ['United States', 'Canada', 'Germany', 'France', 'Japan', 'Australia']
    # Filter to countries that actually exist in the dataset
    available_countries = [c for c in available_countries if c in df['Country name'].unique()]

if len(available_countries) == 0:
    # Use some countries from the dataset
    available_countries = df['Country name'].unique()[:6]

plt.figure(figsize=(14, 7))
for country in available_countries:
    country_data = df[df['Country name'] == country].sort_values('year')
    plt.plot(country_data['year'], country_data['Life Ladder'], 
             marker='o', linewidth=2, markersize=6, label=country)

plt.title('Life Ladder Score Trends for Selected Countries', fontsize=16, fontweight='bold')
plt.xlabel('Year', fontsize=14)
plt.ylabel('Life Ladder Score', fontsize=14)
plt.legend(title='Countries', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Plot 3: Regional comparison (grouping countries by approximate regions)
# Since we don't have region data, let's create some groupings based on geography
european_countries = ['Germany', 'France', 'United Kingdom', 'Italy', 'Spain', 'Netherlands']
asian_countries = ['Japan', 'China', 'India', 'South Korea', 'Indonesia']
american_countries = ['United States', 'Canada', 'Brazil', 'Mexico', 'Argentina']

# Filter to countries that exist in our dataset
european_data = df[df['Country name'].isin(european_countries)].groupby('year')['Life Ladder'].mean()
asian_data = df[df['Country name'].isin(asian_countries)].groupby('year')['Life Ladder'].mean()
american_data = df[df['Country name'].isin(american_countries)].groupby('year')['Life Ladder'].mean()

plt.figure(figsize=(14, 7))
plt.plot(european_data.index, european_data.values, marker='s', linewidth=2, 
         markersize=8, color='blue', label='European Countries (Avg)')
plt.plot(asian_data.index, asian_data.values, marker='^', linewidth=2, 
         markersize=8, color='green', label='Asian Countries (Avg)')
plt.plot(american_data.index, american_data.values, marker='D', linewidth=2, 
         markersize=8, color='red', label='American Countries (Avg)')

plt.title('Regional Comparison of Average Life Ladder Scores Over Time', fontsize=16, fontweight='bold')
plt.xlabel('Year', fontsize=14)
plt.ylabel('Average Life Ladder Score', fontsize=14)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Create a summary statistics table
print("=" * 70)
print("TIME SERIES TREND ANALYSIS SUMMARY")
print("=" * 70)
print("\nGlobal Average Life Ladder Score by Year:")
print(average_by_year.to_string(index=False))

print("\n" + "=" * 70)
print("Key Statistics:")
print("=" * 70)
print(f"Overall global average: {df['Life Ladder'].mean():.3f}")
print(f"Highest global average: {average_by_year['Life Ladder'].max():.3f} in {average_by_year.loc[average_by_year['Life Ladder'].idxmax(), 'year']}")
print(f"Lowest global average: {average_by_year['Life Ladder'].min():.3f} in {average_by_year.loc[average_by_year['Life Ladder'].idxmin(), 'year']}")

# Calculate trend (slope) for global average
from scipy import stats
x = average_by_year['year'].values
y = average_by_year['Life Ladder'].values
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
print(f"\nGlobal trend slope: {slope:.4f} (positive = increasing trend)")
print(f"R-squared: {r_value**2:.4f}")
print(f"P-value: {p_value:.4f}")

if p_value < 0.05:
    if slope > 0:
        print("Interpretation: Statistically significant increasing trend in global happiness")
    else:
        print("Interpretation: Statistically significant decreasing trend in global happiness")
else:
    print("Interpretation: No statistically significant trend in global happiness")