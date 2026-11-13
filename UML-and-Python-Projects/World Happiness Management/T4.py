import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Load the data
df = pd.read_csv('world-happiness-report.csv')

# Create country groups based on first letter (as proxy for regions since we don't have regional data)
df['Country Group'] = df['Country name'].str[0].str.upper()

# Group letters into meaningful clusters for better visualization
# Let's create 5 groups based on common patterns
def create_country_group(letter):
    if letter in ['A', 'B', 'C', 'D']:
        return 'Group A-D'
    elif letter in ['E', 'F', 'G', 'H']:
        return 'Group E-H'
    elif letter in ['I', 'J', 'K', 'L']:
        return 'Group I-L'
    elif letter in ['M', 'N', 'O', 'P']:
        return 'Group M-P'
    else:
        return 'Group Q-Z'

df['Country Group'] = df['Country name'].str[0].str.upper().apply(create_country_group)

# Create a scatter plot: Log GDP per capita vs Life Ladder score
plt.figure(figsize=(14, 8))

# Scatter plot with color by country group
scatter = sns.scatterplot(data=df, x='Log GDP per capita', y='Life Ladder', 
                          hue='Country Group', palette='viridis', 
                          s=80, alpha=0.7, edgecolor='black', linewidth=0.5)

# Add a regression line for overall trend
sns.regplot(data=df, x='Log GDP per capita', y='Life Ladder', 
            scatter=False, color='red', line_kws={'linewidth': 2, 'linestyle': '--'})

# Customize the plot
plt.title('Relationship between GDP per capita and Life Ladder Score by Country Group', 
          fontsize=16, fontweight='bold')
plt.xlabel('Log GDP per capita (Logarithmic Scale)', fontsize=12)
plt.ylabel('Life Ladder Score (Happiness)', fontsize=12)
plt.grid(True, alpha=0.3, linestyle='--')

# Add correlation coefficient
correlation = df['Log GDP per capita'].corr(df['Life Ladder'])
plt.text(0.02, 0.98, f'Correlation: {correlation:.3f}', 
         transform=plt.gca().transAxes, fontsize=12,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Add count of observations
plt.text(0.02, 0.92, f'Total Observations: {len(df)}', 
         transform=plt.gca().transAxes, fontsize=10,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.legend(title='Country Group', title_fontsize=12, fontsize=10, 
           loc='lower right', framealpha=0.9)

plt.tight_layout()
plt.show()

# Create a second plot: Grouped bar chart showing average factor contributions
# Select key factors for analysis
factors = ['Social support', 'Freedom to make life choices', 'Generosity', 
           'Perceptions of corruption', 'Healthy life expectancy at birth']

# Calculate average for each factor by country group
group_means = df.groupby('Country Group')[factors].mean()

# Create grouped bar chart
fig, ax = plt.subplots(figsize=(14, 8))
x = np.arange(len(group_means.index))
width = 0.15

colors = plt.cm.viridis(np.linspace(0, 1, len(factors)))

for i, factor in enumerate(factors):
    ax.bar(x + i*width, group_means[factor], width, label=factor, color=colors[i], alpha=0.8)

# Customize the plot
ax.set_xlabel('Country Group', fontsize=12)
ax.set_ylabel('Average Score', fontsize=12)
ax.set_title('Average Factor Contributions by Country Group', fontsize=16, fontweight='bold')
ax.set_xticks(x + width * (len(factors)-1)/2)
ax.set_xticklabels(group_means.index)
ax.legend(title='Happiness Factors', fontsize=10, title_fontsize=11)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.show()

# Create analysis and insights
print("="*70)
print("CONDITIONAL ANALYSIS: GDP vs HAPPINESS RELATIONSHIP")
print("="*70)

# Calculate statistics by country group
print("\n1. AVERAGE LIFE LADDER SCORES BY COUNTRY GROUP:")
group_stats = df.groupby('Country Group').agg({
    'Life Ladder': ['mean', 'median', 'std', 'count'],
    'Log GDP per capita': ['mean', 'median']
}).round(3)

print(group_stats)

print("\n2. CORRELATION ANALYSIS:")
print(f"Overall correlation between GDP and Happiness: {correlation:.3f}")

# Correlation by group
print("\nCorrelation by Country Group:")
for group in df['Country Group'].unique():
    group_data = df[df['Country Group'] == group]
    group_corr = group_data['Log GDP per capita'].corr(group_data['Life Ladder'])
    print(f"  {group}: {group_corr:.3f}")

print("\n3. FACTOR CONTRIBUTIONS SUMMARY:")
print("Average factor scores by country group:")
for factor in factors:
    print(f"\n{factor}:")
    for group in group_means.index:
        print(f"  {group}: {group_means.loc[group, factor]:.3f}")

# Top 5 countries by Life Ladder score
print("\n4. TOP 5 COUNTRIES BY LIFE LADDER SCORE (all years):")
top_countries = df.groupby('Country name')['Life Ladder'].mean().sort_values(ascending=False).head(5)
for i, (country, score) in enumerate(top_countries.items(), 1):
    print(f"{i}. {country}: {score:.3f}")

# Bottom 5 countries by Life Ladder score
print("\n5. BOTTOM 5 COUNTRIES BY LIFE LADDER SCORE (all years):")
bottom_countries = df.groupby('Country name')['Life Ladder'].mean().sort_values().head(5)
for i, (country, score) in enumerate(bottom_countries.items(), 1):
    print(f"{i}. {country}: {score:.3f}")

# Create density plot for GDP distribution
plt.figure(figsize=(12, 6))

# Create subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# GDP distribution by group
for group in df['Country Group'].unique():
    group_data = df[df['Country Group'] == group]['Log GDP per capita']
    sns.kdeplot(group_data, label=group, ax=ax1, fill=True, alpha=0.3)

ax1.set_title('GDP Distribution by Country Group', fontsize=14)
ax1.set_xlabel('Log GDP per capita')
ax1.set_ylabel('Density')
ax1.legend(title='Country Group')
ax1.grid(True, alpha=0.3)

# Life Ladder distribution by group
for group in df['Country Group'].unique():
    group_data = df[df['Country Group'] == group]['Life Ladder']
    sns.kdeplot(group_data, label=group, ax=ax2, fill=True, alpha=0.3)

ax2.set_title('Life Ladder Score Distribution by Country Group', fontsize=14)
ax2.set_xlabel('Life Ladder Score')
ax2.set_ylabel('Density')
ax2.legend(title='Country Group')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()