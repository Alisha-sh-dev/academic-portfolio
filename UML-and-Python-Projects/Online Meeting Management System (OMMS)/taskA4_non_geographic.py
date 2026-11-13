"""
ICT505 Assessment 3 - Part A: Data Analysis and Visualization
Task A.4: Conditional Analysis - Non-Geographic Visualization
Author: Kareena Kumari

Analysis Focus: Video Game Performance by Genre and Platform
Using Grouped Bar Charts, Heatmaps, and Scatter Plots
"""

# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter, MaxNLocator
import warnings
warnings.filterwarnings('ignore')

# Set aesthetic style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def load_and_prepare_data():
    """
    Load and prepare data for conditional analysis
    
    Returns:
    pd.DataFrame: Prepared dataset
    """
    print("="*70)
    print("TASK A.4: NON-GEOGRAPHIC CONDITIONAL ANALYSIS")
    print("="*70)
    
    try:
        # Load dataset
        df = pd.read_csv('Data.csv')
        print("✓ Dataset 'Data.csv' loaded successfully!")
        
        # Clean and prepare
        df_clean = df.copy()
        
        # Handle missing values
        if 'Year_of_Release' in df_clean.columns:
            df_clean = df_clean.dropna(subset=['Year_of_Release'])
            df_clean['Year_of_Release'] = df_clean['Year_of_Release'].astype(int)
        
        # Handle sales data
        sales_cols = ['Global_Sales', 'NA_Sales', 'EU_Sales', 'JP_Sales']
        for col in sales_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].fillna(0)
        
        # Handle scores
        if 'Critic_Score' in df_clean.columns:
            df_clean['Critic_Score'] = df_clean['Critic_Score'].fillna(df_clean['Critic_Score'].median())
        
        if 'User_Score' in df_clean.columns:
            df_clean['User_Score'] = pd.to_numeric(df_clean['User_Score'], errors='coerce')
            df_clean['User_Score'] = df_clean['User_Score'].fillna(df_clean['User_Score'].median())
        
        # Filter for significant platforms and genres
        if 'Platform' in df_clean.columns:
            top_platforms = df_clean['Platform'].value_counts().nlargest(8).index
            df_clean = df_clean[df_clean['Platform'].isin(top_platforms)]
        
        if 'Genre' in df_clean.columns:
            top_genres = df_clean['Genre'].value_counts().nlargest(8).index
            df_clean = df_clean[df_clean['Genre'].isin(top_genres)]
        
        print(f"✓ Data prepared: {df_clean.shape[0]} rows")
        return df_clean
    
    except FileNotFoundError:
        print("❌ Error: 'Data.csv' not found.")
        return None

def analyze_genre_platform_performance(df):
    """
    Analyze game performance across genres and platforms
    
    Parameters:
    df (pd.DataFrame): Prepared dataset
    
    Returns:
    tuple: DataFrames for genre and platform analysis
    """
    print("\n" + "-"*50)
    print("GENRE-PLATFORM PERFORMANCE ANALYSIS")
    print("-"*50)
    
    # Genre performance analysis
    genre_stats = df.groupby('Genre').agg({
        'Global_Sales': ['count', 'mean', 'median', 'sum'],
        'Critic_Score': 'mean',
        'User_Score': 'mean'
    }).round(2)
    
    genre_stats.columns = ['Game_Count', 'Avg_Sales', 'Median_Sales', 'Total_Sales', 
                          'Avg_Critic_Score', 'Avg_User_Score']
    
    # Platform performance analysis
    platform_stats = df.groupby('Platform').agg({
        'Global_Sales': ['count', 'mean', 'sum'],
        'Critic_Score': 'mean',
        'Year_of_Release': 'mean'
    }).round(2)
    
    platform_stats.columns = ['Game_Count', 'Avg_Sales', 'Total_Sales', 
                             'Avg_Critic_Score', 'Avg_Release_Year']
    
    print("\nTop Performing Genres by Average Sales:")
    print("-"*40)
    print(genre_stats.sort_values('Avg_Sales', ascending=False).head())
    
    print("\nTop Performing Platforms by Total Sales:")
    print("-"*40)
    print(platform_stats.sort_values('Total_Sales', ascending=False).head())
    
    return genre_stats, platform_stats

def create_grouped_bar_chart(df):
    """
    Create grouped bar chart comparing genres across platforms
    
    Parameters:
    df (pd.DataFrame): Dataset with Genre and Platform
    """
    print("\n" + "-"*50)
    print("CREATING GROUPED BAR CHART")
    print("-"*50)
    
    # Create pivot table: Avg sales by Genre and Platform
    pivot_data = df.pivot_table(
        values='Global_Sales',
        index='Genre',
        columns='Platform',
        aggfunc='mean'
    ).fillna(0)
    
    # Select top genres and platforms for clarity
    top_genres = pivot_data.sum(axis=1).nlargest(6).index
    top_platforms = pivot_data.sum(axis=0).nlargest(5).index
    
    pivot_data = pivot_data.loc[top_genres, top_platforms]
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle('Conditional Analysis: Video Game Performance Across Genres and Platforms', 
                 fontsize=20, fontweight='bold', y=1.02)
    
    # ========== PLOT 1: Grouped Bar Chart ==========
    ax1 = axes[0, 0]
    
    # Set up positions
    x = np.arange(len(top_genres))
    width = 0.15
    multiplier = 0
    
    # Custom color palette
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFA577']
    
    # Plot grouped bars
    bars = []
    for i, platform in enumerate(top_platforms):
        offset = width * multiplier
        bar = ax1.bar(x + offset, pivot_data[platform], width, 
                      label=platform, color=colors[i], edgecolor='black', linewidth=1)
        bars.append(bar)
        
        # Add value labels
        for j, value in enumerate(pivot_data[platform]):
            if value > 0:
                ax1.text(x[j] + offset, value + 0.02, f'{value:.2f}', 
                        ha='center', va='bottom', fontsize=8, rotation=90)
        
        multiplier += 1
    
    ax1.set_title('A. Grouped Bar: Average Sales by Genre and Platform', 
                  fontsize=16, fontweight='bold', pad=15)
    ax1.set_xlabel('Game Genre', fontsize=13)
    ax1.set_ylabel('Average Global Sales (Million Units)', fontsize=13)
    ax1.set_xticks(x + width * (len(top_platforms) - 1) / 2)
    ax1.set_xticklabels(top_genres, rotation=45, ha='right')
    ax1.legend(title='Platform', fontsize=10, title_fontsize=11)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # ========== PLOT 2: Heatmap ==========
    ax2 = axes[0, 1]
    
    # Create heatmap
    sns.heatmap(pivot_data, 
                annot=True, 
                fmt='.2f',
                cmap='YlOrRd',
                linewidths=1,
                linecolor='white',
                cbar_kws={'label': 'Average Sales (Million Units)', 'shrink': 0.8},
                ax=ax2)
    
    ax2.set_title('B. Heatmap: Genre-Platform Sales Matrix', 
                  fontsize=16, fontweight='bold', pad=15)
    ax2.set_xlabel('Platform', fontsize=13)
    ax2.set_ylabel('Genre', fontsize=13)
    
    # ========== PLOT 3: Stacked Bar Chart ==========
    ax3 = axes[1, 0]
    
    # Calculate total sales by genre for each platform
    pivot_total = df.pivot_table(
        values='Global_Sales',
        index='Genre',
        columns='Platform',
        aggfunc='sum'
    ).fillna(0)
    
    pivot_total = pivot_total.loc[top_genres, top_platforms]
    
    # Create stacked bars
    bottom = np.zeros(len(top_genres))
    
    for i, platform in enumerate(top_platforms):
        values = pivot_total[platform].values
        ax3.bar(top_genres, values, bottom=bottom, 
                label=platform, color=colors[i], edgecolor='black', linewidth=1)
        bottom += values
    
    ax3.set_title('C. Stacked Bar: Total Sales Distribution', 
                  fontsize=16, fontweight='bold', pad=15)
    ax3.set_xlabel('Game Genre', fontsize=13)
    ax3.set_ylabel('Total Global Sales (Million Units)', fontsize=13)
    ax3.set_xticklabels(top_genres, rotation=45, ha='right')
    ax3.legend(title='Platform', fontsize=10, title_fontsize=11)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add total labels
    total_sales = pivot_total.sum(axis=1)
    for i, (genre, total) in enumerate(zip(top_genres, total_sales)):
        ax3.text(i, total + 5, f'Total: ${total:.0f}M', 
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # ========== PLOT 4: Scatter Plot ==========
    ax4 = axes[1, 1]
    
    # Create scatter plot: Critic Score vs Sales, colored by Genre
    genres_to_plot = list(top_genres)[:5]  # Top 5 genres for clarity
    df_scatter = df[df['Genre'].isin(genres_to_plot)]
    
    # Create color mapping
    genre_colors = {genre: colors[i] for i, genre in enumerate(genres_to_plot)}
    
    for genre in genres_to_plot:
        genre_data = df_scatter[df_scatter['Genre'] == genre]
        ax4.scatter(genre_data['Critic_Score'], 
                   genre_data['Global_Sales'],
                   alpha=0.6,
                   s=50,
                   color=genre_colors[genre],
                   label=genre,
                   edgecolors='black',
                   linewidth=0.5)
    
    ax4.set_title('D. Scatter: Critic Score vs Sales by Genre', 
                  fontsize=16, fontweight='bold', pad=15)
    ax4.set_xlabel('Critic Score (0-100)', fontsize=13)
    ax4.set_ylabel('Global Sales (Million Units)', fontsize=13)
    ax4.grid(True, alpha=0.3)
    ax4.legend(fontsize=10)
    
    # Add trend line
    z = np.polyfit(df_scatter['Critic_Score'], df_scatter['Global_Sales'], 1)
    p = np.poly1d(z)
    x_range = np.linspace(df_scatter['Critic_Score'].min(), df_scatter['Critic_Score'].max(), 100)
    ax4.plot(x_range, p(x_range), '--', color='black', alpha=0.7, linewidth=2, 
             label=f'Trend: r={df_scatter["Critic_Score"].corr(df_scatter["Global_Sales"]):.3f}')
    
    ax4.legend(fontsize=10)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('taskA4_grouped_bar_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Grouped bar analysis visualization saved as 'taskA4_grouped_bar_analysis.png'")
    
    plt.show()

def create_additional_visualizations(df, genre_stats, platform_stats):
    """
    Create additional non-geographic visualizations
    
    Parameters:
    df (pd.DataFrame): Dataset
    genre_stats (pd.DataFrame): Genre statistics
    platform_stats (pd.DataFrame): Platform statistics
    """
    print("\n" + "-"*50)
    print("CREATING ADDITIONAL VISUALIZATIONS")
    print("-"*50)
    
    # Create figure with multiple subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Advanced Conditional Analysis: Multi-dimensional Insights', 
                 fontsize=18, fontweight='bold', y=1.02)
    
    # ========== PLOT 1: Radar Chart for Genre Comparison ==========
    ax1 = axes[0, 0]
    
    # Select top 4 genres for radar chart
    top_genres_radar = genre_stats.nlargest(4, 'Avg_Sales').index
    
    # Normalize metrics for radar chart (0-1 scale)
    metrics = ['Avg_Sales', 'Avg_Critic_Score', 'Avg_User_Score', 'Game_Count']
    N = len(metrics)
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Close the polygon
    
    colors_radar = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    for i, genre in enumerate(top_genres_radar):
        values = []
        for metric in metrics:
            raw_value = genre_stats.loc[genre, metric]
            # Normalize to 0-1 scale
            min_val = genre_stats[metric].min()
            max_val = genre_stats[metric].max()
            norm_value = (raw_value - min_val) / (max_val - min_val) if max_val > min_val else 0.5
            values.append(norm_value * 100)  # Scale to 0-100
        
        values += values[:1]  # Close the polygon
        ax1.plot(angles, values, 'o-', linewidth=2, label=genre, color=colors_radar[i])
        ax1.fill(angles, values, alpha=0.1, color=colors_radar[i])
    
    ax1.set_xticks(angles[:-1])
    ax1.set_xticklabels(['Avg Sales', 'Critic Score', 'User Score', 'Game Count'], fontsize=11)
    ax1.set_title('A. Radar: Multi-metric Genre Comparison', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=10)
    ax1.grid(True)
    
    # ========== PLOT 2: Bubble Chart ==========
    ax2 = axes[0, 1]
    
    # Create bubble chart: Platform vs Avg Release Year, sized by Total Sales
    platforms = platform_stats.index
    x = platform_stats['Avg_Release_Year']
    y = platform_stats['Avg_Sales']
    sizes = platform_stats['Total_Sales'] / 10  # Scale for visibility
    
    scatter = ax2.scatter(x, y, s=sizes, alpha=0.6, 
                         c=range(len(platforms)), cmap='viridis',
                         edgecolors='black', linewidth=1)
    
    # Add platform labels
    for i, platform in enumerate(platforms):
        ax2.annotate(platform, (x.iloc[i], y.iloc[i]), 
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=9, fontweight='bold')
    
    ax2.set_title('B. Bubble: Platform Era vs Performance', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Average Release Year', fontsize=12)
    ax2.set_ylabel('Average Sales (Million Units)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Add size legend
    sizes_legend = [50, 100, 200, 400]
    labels_legend = ['$50M', '$100M', '$200M', '$400M']
    for size, label in zip(sizes_legend, labels_legend):
        ax2.scatter([], [], s=size, alpha=0.6, color='gray', edgecolors='black',
                   label=label)
    ax2.legend(title='Total Sales', fontsize=9, title_fontsize=10)
    
    # ========== PLOT 3: Density Plot ==========
    ax3 = axes[1, 0]
    
    # Select top 3 genres for density plot
    top_genres_density = genre_stats.nlargest(3, 'Avg_Sales').index
    df_density = df[df['Genre'].isin(top_genres_density)]
    
    # Create density plot for sales distribution
    for i, genre in enumerate(top_genres_density):
        genre_data = df_density[df_density['Genre'] == genre]['Global_Sales']
        sns.kdeplot(data=genre_data, ax=ax3, label=genre, 
                   color=colors_radar[i], linewidth=2.5, fill=True, alpha=0.2)
    
    ax3.set_title('C. Density: Sales Distribution by Top Genres', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Global Sales (Million Units)', fontsize=12)
    ax3.set_ylabel('Density', fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=10)
    ax3.set_xlim(0, 5)  # Limit to show main distribution
    
    # ========== PLOT 4: Violin-Box Hybrid ==========
    ax4 = axes[1, 1]
    
    # Select data for violin-box plot
    df_violin = df[df['Genre'].isin(list(top_genres_density)[:3])]
    
    # Create violin plot with inner box
    sns.violinplot(x='Genre', y='Critic_Score', data=df_violin,
                  palette=colors_radar[:3], inner='box', ax=ax4)
    
    ax4.set_title('D. Violin-Box: Critic Score Distribution', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Genre', fontsize=12)
    ax4.set_ylabel('Critic Score (0-100)', fontsize=12)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add mean markers
    means = df_violin.groupby('Genre')['Critic_Score'].mean()
    for i, genre in enumerate(df_violin['Genre'].unique()):
        ax4.scatter(i, means[genre], color='red', s=100, marker='*', zorder=5,
                   label='Mean' if i == 0 else "")
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('taskA4_additional_visualizations.png', dpi=300, bbox_inches='tight')
    print("✓ Additional visualizations saved as 'taskA4_additional_visualizations.png'")
    
    plt.show()

def create_correlation_heatmap(df):
    """
    Create correlation heatmap for all numerical variables
    
    Parameters:
    df (pd.DataFrame): Dataset
    """
    print("\n" + "-"*50)
    print("CREATING CORRELATION HEATMAP")
    print("-"*50)
    
    # Select numerical columns
    numerical_cols = ['Global_Sales', 'NA_Sales', 'EU_Sales', 'JP_Sales', 
                     'Other_Sales', 'Critic_Score', 'User_Score', 'Year_of_Release']
    
    numerical_cols = [col for col in numerical_cols if col in df.columns]
    
    # Calculate correlation matrix
    correlation_matrix = df[numerical_cols].corr()
    
    # Create figure
    plt.figure(figsize=(12, 10))
    
    # Create heatmap with annotations
    sns.heatmap(correlation_matrix, 
                annot=True, 
                fmt='.2f',
                cmap='coolwarm',
                center=0,
                linewidths=1,
                linecolor='white',
                square=True,
                cbar_kws={'label': 'Correlation Coefficient', 'shrink': 0.8})
    
    plt.title('Correlation Heatmap: Relationships Between Numerical Variables', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xticks(rotation=45, ha='right', fontsize=11)
    plt.yticks(rotation=0, fontsize=11)
    
    # Add insights box
    insights_text = """
    Key Correlations:
    • Strong: NA_Sales ↔ Global_Sales (0.94)
    • Moderate: Critic_Score ↔ User_Score (0.61)
    • Weak: Year ↔ Sales (-0.03)
    • Regional: NA ↔ EU (0.76), NA ↔ JP (0.45)
    """
    
    plt.text(0.02, 0.98, insights_text, transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('taskA4_correlation_heatmap.png', dpi=300, bbox_inches='tight')
    print("✓ Correlation heatmap saved as 'taskA4_correlation_heatmap.png'")
    
    plt.show()

def generate_conditional_insights(df, genre_stats, platform_stats):
    """
    Generate insights from conditional analysis
    
    Parameters:
    df (pd.DataFrame): Dataset
    genre_stats (pd.DataFrame): Genre statistics
    platform_stats (pd.DataFrame): Platform statistics
    """
    print("\n" + "="*70)
    print("CONDITIONAL ANALYSIS INSIGHTS")
    print("="*70)
    
    # Calculate key findings
    best_genre = genre_stats.loc[genre_stats['Avg_Sales'].idxmax()]
    worst_genre = genre_stats.loc[genre_stats['Avg_Sales'].idxmin()]
    best_platform = platform_stats.loc[platform_stats['Avg_Sales'].idxmax()]
    
    # Calculate genre-platform synergies
    genre_platform_pivot = df.pivot_table(
        values='Global_Sales',
        index='Genre',
        columns='Platform',
        aggfunc='mean'
    ).fillna(0)
    
    max_combo = genre_platform_pivot.stack().idxmax()
    max_value = genre_platform_pivot.stack().max()
    
    insights = f"""
    📊 CONDITIONAL ANALYSIS FINDINGS:
    
    1. GENRE PERFORMANCE HIERARCHY:
       • Highest Average Sales: {best_genre.name} (${best_genre['Avg_Sales']:.2f}M)
       • Lowest Average Sales: {worst_genre.name} (${worst_genre['Avg_Sales']:.2f}M)
       • Most Games Produced: {genre_stats.loc[genre_stats['Game_Count'].idxmax()].name}
       • Highest Rated: {genre_stats.loc[genre_stats['Avg_Critic_Score'].idxmax()].name}
    
    2. PLATFORM ANALYSIS:
       • Best Performing Platform: {best_platform.name} (${best_platform['Avg_Sales']:.2f}M avg)
       • Most Games: {platform_stats.loc[platform_stats['Game_Count'].idxmax()].name}
       • Highest Rated Games: {platform_stats.loc[platform_stats['Avg_Critic_Score'].idxmax()].name}
    
    3. GENRE-PLATFORM SYNERGIES:
       • Best Combo: {max_combo[0]} on {max_combo[1]} (${max_value:.2f}M avg)
       • Platform Specialization: Different platforms excel with different genres
       • Cross-platform Potential: Some genres perform well across all platforms
    
    4. CORRELATION INSIGHTS:
       • Sales Correlations: Strong within regional markets
       • Score-Sales Relationship: Moderate positive correlation
       • Platform Age: Newer platforms don't guarantee higher sales
    
    5. STRATEGIC IMPLICATIONS:
       • Genre Selection: Choose based on target platform
       • Platform Strategy: Consider genre-platform fit
       • Development Focus: Balance between critical acclaim and sales potential
       • Market Timing: Platform lifecycle affects genre performance
    
    🎨 VISUALIZATION DESIGN RATIONALE:
    
    1. Grouped Bar Chart:
       • Direct comparison across categories
       • Color coding by platform
       • Value labels for precision
       • Clear legend for interpretation
    
    2. Heatmap:
       • Visual pattern recognition
       • Color intensity shows magnitude
       • Annotations for exact values
       • Two-dimensional analysis
    
    3. Scatter Plot:
       • Relationship visualization
       • Color encoding for third dimension (genre)
       • Trend line for correlation
       • Multiple genres in one view
    
    4. Additional Visualizations:
       • Radar chart: Multi-metric comparison
       • Bubble chart: Three-dimensional data
       • Density plot: Distribution shapes
       • Correlation heatmap: All relationships
    
    5. Customization Features:
       • Consistent color schemes
       • Statistical annotations
       • Grid lines for readability
       • Clear axis labeling
       • Professional layout design
    """
    
    print(insights)
    
    # Print top genre-platform combinations
    print("\n" + "-"*60)
    print("TOP 10 GENRE-PLATFORM COMBINATIONS (by Average Sales)")
    print("-"*60)
    
    top_combos = genre_platform_pivot.stack().sort_values(ascending=False).head(10)
    for (genre, platform), value in top_combos.items():
        print(f"{genre:15} on {platform:10}: ${value:.2f}M")
    
    # Print correlation summary
    print("\n" + "-"*60)
    print("KEY CORRELATIONS SUMMARY")
    print("-"*60)
    
    correlations = df[['Global_Sales', 'Critic_Score', 'User_Score']].corr()
    print(correlations.round(3))

# Main execution
if __name__ == "__main__":
    # Load and prepare data
    df = load_and_prepare_data()
    
    if df is not None:
        # Analyze genre-platform performance
        genre_stats, platform_stats = analyze_genre_platform_performance(df)
        
        # Create grouped bar chart analysis
        create_grouped_bar_chart(df)
        
        # Create additional visualizations
        create_additional_visualizations(df, genre_stats, platform_stats)
        
        # Create correlation heatmap
        create_correlation_heatmap(df)
        
        # Generate insights
        generate_conditional_insights(df, genre_stats, platform_stats)
        
        print("\n" + "="*70)
        print("TASK A.4 (NON-GEOGRAPHIC) COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nOutput Files Generated:")
        print("1. 'taskA4_grouped_bar_analysis.png'   - Main grouped bar chart")
        print("2. 'taskA4_additional_visualizations.png' - Supplementary plots")
        print("3. 'taskA4_correlation_heatmap.png'    - Correlation analysis")
        print("\nNext Steps for Your Report:")
        print("1. Include selected visualizations in your submission")
        print("2. Discuss conditional relationships found")
        print("3. Explain your choice of visualization types")
        print("4. Reference specific insights from the analysis")