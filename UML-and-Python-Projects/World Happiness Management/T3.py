import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Load the data
df = pd.read_csv('world-happiness-report.csv')

# Check the data
print("Data columns:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())
print("\nYear range:", df['year'].min(), "to", df['year'].max())

# Create a figure with subplots
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# 1. BOX PLOT: Year vs Life Ladder
# Convert year to categorical for better visualization
df['year_cat'] = df['year'].astype(str)

# Filter to recent years for clearer visualization (last 10 years)
recent_years = sorted(df['year'].unique())[-10:]
df_recent = df[df['year'].isin(recent_years)]
df_recent['year_cat'] = df_recent['year'].astype(str)

# Box plot
sns.boxplot(data=df_recent, x='year_cat', y='Life Ladder', 
            palette='viridis', ax=axes[0])
axes[0].set_title('Distribution of Life Ladder Scores by Year (Box Plot)')
axes[0].set_xlabel('Year')
axes[0].set_ylabel('Life Ladder Score')
axes[0].tick_params(axis='x', rotation=45)
axes[0].grid(True, alpha=0.3)

# 2. VIOLIN PLOT: Year vs Life Ladder
sns.violinplot(data=df_recent, x='year_cat', y='Life Ladder', 
               palette='viridis', ax=axes[1])
axes[1].set_title('Distribution of Life Ladder Scores by Year (Violin Plot)')
axes[1].set_xlabel('Year')
axes[1].set_ylabel('Life Ladder Score')
axes[1].tick_params(axis='x', rotation=45)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# For better visualization with more categories, let's also create plots by country groups
# Since we don't have regions, let's group countries by their initial letters
df['country_group'] = df['Country name'].str[0].str.upper()

# Filter to common starting letters
common_letters = df['country_group'].value_counts().head(10).index.tolist()
df_filtered = df[df['country_group'].isin(common_letters)]

# Create another figure
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Box plot by country starting letter
sns.boxplot(data=df_filtered, x='country_group', y='Life Ladder', 
            palette='viridis', ax=axes[0], order=common_letters)
axes[0].set_title('Distribution of Life Ladder Scores by Country First Letter (Box Plot)')
axes[0].set_xlabel('Country First Letter')
axes[0].set_ylabel('Life Ladder Score')
axes[0].grid(True, alpha=0.3)

# Violin plot by country starting letter
sns.violinplot(data=df_filtered, x='country_group', y='Life Ladder', 
               palette='viridis', ax=axes[1], order=common_letters)
axes[1].set_title('Distribution of Life Ladder Scores by Country First Letter (Violin Plot)')
axes[1].set_xlabel('Country First Letter')
axes[1].set_ylabel('Life Ladder Score')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Create summary statistics
print("\n" + "="*60)
print("LIFE LADDER SCORE DISTRIBUTION ANALYSIS")
print("="*60)

# Overall statistics
print(f"\nOverall Statistics:")
print(f"Mean Life Ladder score: {df['Life Ladder'].mean():.3f}")
print(f"Median Life Ladder score: {df['Life Ladder'].median():.3f}")
print(f"Standard deviation: {df['Life Ladder'].std():.3f}")
print(f"Minimum: {df['Life Ladder'].min():.3f}")
print(f"Maximum: {df['Life Ladder'].max():.3f}")
print(f"Number of observations: {len(df)}")
print(f"Number of countries: {df['Country name'].nunique()}")
print(f"Year range: {df['year'].min()} - {df['year'].max()}")

# Year-wise statistics
print(f"\nYear-wise Statistics (for last 10 years):")
year_stats = df_recent.groupby('year_cat')['Life Ladder'].agg(['mean', 'median', 'std', 'count']).round(3)
print(year_stats)

# Country group statistics
print(f"\nStatistics by Country First Letter (top 10 letters):")
country_group_stats = df_filtered.groupby('country_group')['Life Ladder'].agg(['mean', 'median', 'std', 'count']).round(3)
print(country_group_stats)

# Create a density plot to show overall distribution
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='Life Ladder', kde=True, color='green', bins=30)
plt.title('Overall Distribution of Life Ladder Scores')
plt.xlabel('Life Ladder Score')
plt.ylabel('Frequency')
plt.grid(True, alpha=0.3)
plt.axvline(x=df['Life Ladder'].mean(), color='red', linestyle='--', label=f'Mean: {df["Life Ladder"].mean():.2f}')
plt.axvline(x=df['Life Ladder'].median(), color='blue', linestyle='--', label=f'Median: {df["Life Ladder"].median():.2f}')
plt.legend()
plt.show()