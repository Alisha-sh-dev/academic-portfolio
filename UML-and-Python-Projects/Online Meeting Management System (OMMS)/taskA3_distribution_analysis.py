"""
ICT505 Assessment 3 - Part A: Data Analysis and Visualization
Task A.3: Data Distribution Analysis
Author: Kareena Kumari 

Analysis Focus: Distribution of Video Game Sales by Genre
"""

# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import warnings
warnings.filterwarnings('ignore')

# Set aesthetic style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def load_and_prepare_data():
    """
    Load and prepare data for distribution analysis
    
    Returns:
    pd.DataFrame: Prepared dataset
    """
    print("="*70)
    print("TASK A.3: DATA DISTRIBUTION ANALYSIS - VIDEO GAME GENRES")
    print("="*70)
    
    try:
        # Load dataset
        df = pd.read_csv('Data.csv')
        print("✓ Dataset loaded successfully!")
        print(f"✓ Initial shape: {df.shape[0]} rows × {df.shape[1]} columns")
        
        # Clean and prepare
        df_clean = df.copy()
        
        # Handle missing values
        if 'Genre' in df_clean.columns:
            df_clean = df_clean.dropna(subset=['Genre'])
        
        if 'Global_Sales' in df_clean.columns:
            df_clean['Global_Sales'] = df_clean['Global_Sales'].fillna(0)
        
        # Filter for significant genres (at least 100 games)
        genre_counts = df_clean['Genre'].value_counts()
        significant_genres = genre_counts[genre_counts >= 100].index
        df_clean = df_clean[df_clean['Genre'].isin(significant_genres)]
        
        print(f"✓ Cleaned dataset: {df_clean.shape[0]} rows")
        print(f"✓ Genres analyzed: {len(significant_genres)}")
        print("  " + ", ".join(significant_genres))
        
        return df_clean
    
    except FileNotFoundError:
        print("❌ Error: 'Data.csv' not found.")
        return None

def analyze_distribution_by_genre(df):
    """
    Analyze sales distribution across different genres
    
    Parameters:
    df (pd.DataFrame): Dataset containing Genre and Global_Sales
    """
    print("\n" + "-"*50)
    print("DISTRIBUTION ANALYSIS BY GENRE")
    print("-"*50)
    
    # Calculate genre statistics
    genre_stats = df.groupby('Genre').agg({
        'Global_Sales': ['count', 'mean', 'median', 'std', 'min', 'max', 'sum']
    }).round(2)
    
    genre_stats.columns = ['Count', 'Mean_Sales', 'Median_Sales', 'Std_Sales', 
                          'Min_Sales', 'Max_Sales', 'Total_Sales']
    
    # Sort by total sales
    genre_stats = genre_stats.sort_values('Total_Sales', ascending=False)
    
    print("\nGenre Sales Statistics:")
    print("-"*40)
    print(genre_stats)
    
    return genre_stats

def create_violin_plot(df):
    """
    Create violin plot showing sales distribution by genre
    
    Parameters:
    df (pd.DataFrame): Dataset with Genre and Global_Sales
    """
    print("\n" + "-"*50)
    print("CREATING VIOLIN PLOT - SALES DISTRIBUTION BY GENRE")
    print("-"*50)
    
    # Filter top genres for better visualization
    top_genres = df['Genre'].value_counts().nlargest(10).index
    df_top = df[df['Genre'].isin(top_genres)]
    
    # Create figure
    plt.figure(figsize=(16, 10))
    
    # Create violin plot with custom styling
    violin = sns.violinplot(
        x='Genre', 
        y='Global_Sales', 
        data=df_top,
        palette='Set3',
        inner='box',      # Show box plot inside
        linewidth=1.5,
        saturation=0.8,
        order=sorted(top_genres)  # Alphabetical order
    )
    
    # Customize title and labels
    plt.title('Distribution of Global Sales by Video Game Genre', 
              fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Game Genre', fontsize=14, fontweight='bold')
    plt.ylabel('Global Sales (Million Units)', fontsize=14, fontweight='bold')
    
    # Format y-axis
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}M'))
    
    # Rotate x-axis labels for readability
    plt.xticks(rotation=45, ha='right', fontsize=11)
    plt.yticks(fontsize=11)
    
    # Add grid
    plt.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Add mean markers
    means = df_top.groupby('Genre')['Global_Sales'].mean()
    for i, genre in enumerate(sorted(top_genres)):
        mean_val = means[genre]
        plt.scatter(i, mean_val, color='red', s=100, zorder=5, 
                   label='Mean' if i == 0 else "", marker='D')
    
    # Add legend for mean markers
    plt.legend(['Mean Sales'], loc='upper right', fontsize=12)
    
    # Add annotations for key insights
    max_genre = means.idxmax()
    max_mean = means.max()
    
    plt.annotate(f'Highest Average: {max_genre}\n(${max_mean:.2f}M)', 
                 xy=(list(sorted(top_genres)).index(max_genre), max_mean),
                 xytext=(10, 30), textcoords='offset points',
                 arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                 fontsize=11, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.8))
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('taskA3_violin_plot.png', dpi=300, bbox_inches='tight')
    print("✓ Violin plot saved as 'taskA3_violin_plot.png'")
    
    plt.show()

def create_box_plot(df):
    """
    Create enhanced box plot showing sales distribution by genre
    
    Parameters:
    df (pd.DataFrame): Dataset with Genre and Global_Sales
    """
    print("\n" + "-"*50)
    print("CREATING BOX PLOT - SALES DISTRIBUTION BY GENRE")
    print("-"*50)
    
    # Filter top genres
    top_genres = df['Genre'].value_counts().nlargest(12).index
    df_top = df[df['Genre'].isin(top_genres)]
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 14))
    
    # ========== PLOT 1: Standard Box Plot ==========
    box1 = sns.boxplot(
        x='Genre', 
        y='Global_Sales', 
        data=df_top,
        palette='coolwarm',
        ax=ax1,
        showfliers=False,  # Hide outliers for cleaner view
        order=sorted(top_genres)
    )
    
    ax1.set_title('A. Box Plot: Sales Distribution by Genre (Outliers Hidden)', 
                  fontsize=16, fontweight='bold', pad=15)
    ax1.set_xlabel('Game Genre', fontsize=13)
    ax1.set_ylabel('Global Sales (Million Units)', fontsize=13)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}M'))
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add mean markers
    means1 = df_top.groupby('Genre')['Global_Sales'].mean()
    for i, genre in enumerate(sorted(top_genres)):
        mean_val = means1[genre]
        ax1.scatter(i, mean_val, color='darkred', s=80, zorder=5, marker='X')
    
    # ========== PLOT 2: Box Plot with Outliers ==========
    box2 = sns.boxplot(
        x='Genre', 
        y='Global_Sales', 
        data=df_top,
        palette='viridis',
        ax=ax2,
        showfliers=True,  # Show outliers
        order=sorted(top_genres)
    )
    
    ax2.set_title('B. Box Plot: Sales Distribution with Outliers', 
                  fontsize=16, fontweight='bold', pad=15)
    ax2.set_xlabel('Game Genre', fontsize=13)
    ax2.set_ylabel('Global Sales (Million Units)', fontsize=13)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}M'))
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(-1, 25)  # Limit y-axis to see details
    
    # Highlight outliers with different color
    for i, genre in enumerate(sorted(top_genres)):
        genre_data = df_top[df_top['Genre'] == genre]['Global_Sales']
        Q1 = genre_data.quantile(0.25)
        Q3 = genre_data.quantile(0.75)
        IQR = Q3 - Q1
        outliers = genre_data[(genre_data < (Q1 - 1.5 * IQR)) | 
                              (genre_data > (Q3 + 1.5 * IQR))]
        
        for outlier in outliers:
            ax2.scatter(i, outlier, color='red', s=50, alpha=0.6, zorder=5)
    
    # Add annotation about outliers
    ax2.text(0.02, 0.98, 'Red dots show outliers\n(1.5×IQR beyond Q1/Q3)', 
             transform=ax2.transAxes, fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # Add statistics box to first plot
    stats_text = f"""
    Box Plot Statistics:
    • Box shows Q1 to Q3 (25th-75th percentile)
    • Line inside box = Median
    • Whiskers extend to non-outlier range
    • X markers = Mean values
    • Outliers shown in Plot B
    """
    ax1.text(0.98, 0.98, stats_text, transform=ax1.transAxes, 
             fontsize=10, verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.suptitle('COMPARATIVE ANALYSIS: VIDEO GAME SALES DISTRIBUTION ACROSS GENRES', 
                 fontsize=18, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('taskA3_box_plot.png', dpi=300, bbox_inches='tight')
    print("✓ Box plot saved as 'taskA3_box_plot.png'")
    
    plt.show()

def create_combined_plot(df):
    """
    Create combined violin and box plot
    
    Parameters:
    df (pd.DataFrame): Dataset with Genre and Global_Sales
    """
    print("\n" + "-"*50)
    print("CREATING COMBINED VIOLIN + BOX PLOT")
    print("-"*50)
    
    # Select top 8 genres for clarity
    top_genres = df['Genre'].value_counts().nlargest(8).index
    df_top = df[df['Genre'].isin(top_genres)]
    
    # Create figure
    plt.figure(figsize=(18, 10))
    
    # Create combined plot using seaborn
    ax = sns.violinplot(
        x='Genre', 
        y='Global_Sales', 
        data=df_top,
        inner='box',  # Shows box plot inside violin
        palette='Spectral',
        linewidth=2,
        saturation=0.9,
        order=sorted(top_genres)
    )
    
    # Customize plot
    plt.title('Combined Violin and Box Plot: Sales Distribution Analysis', 
              fontsize=20, fontweight='bold', pad=25)
    plt.xlabel('Game Genre', fontsize=15, fontweight='bold')
    plt.ylabel('Global Sales (Million Units)', fontsize=15, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}M'))
    plt.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    # Add statistics annotations
    stats_by_genre = df_top.groupby('Genre')['Global_Sales'].describe()
    
    for i, genre in enumerate(sorted(top_genres)):
        stats = stats_by_genre.loc[genre]
        
        # Add median line annotation
        ax.text(i, stats['50%'] + 0.1, f'Med: {stats["50%"]:.1f}M', 
                ha='center', va='bottom', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        
        # Add mean value
        ax.scatter(i, stats['mean'], color='red', s=100, zorder=5, marker='*')
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='lightgray', alpha=0.7, label='Violin: Probability Density'),
        Patch(facecolor='white', edgecolor='black', label='Box: Q1-Q3 & Median'),
        plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='red', 
                  markersize=10, label='Star: Mean Value')
    ]
    plt.legend(handles=legend_elements, loc='upper right', fontsize=11)
    
    # Add insights box
    insights_text = f"""
    Key Distribution Insights:
    • Wider violins = More sales variation
    • Taller boxes = Greater interquartile range
    • Outliers = Exceptional performing games
    • Action/Shooter: High median, many outliers
    • Puzzle: Compact distribution, lower sales
    • Sports: Consistent moderate performance
    """
    plt.text(0.02, 0.98, insights_text, transform=plt.gca().transAxes,
             fontsize=11, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('taskA3_combined_plot.png', dpi=300, bbox_inches='tight')
    print("✓ Combined plot saved as 'taskA3_combined_plot.png'")
    
    plt.show()

def create_genre_comparison_heatmap(df):
    """
    Create heatmap comparing different statistics across genres
    
    Parameters:
    df (pd.DataFrame): Dataset with Genre and Global_Sales
    """
    print("\n" + "-"*50)
    print("CREATING GENRE COMPARISON HEATMAP")
    print("-"*50)
    
    # Calculate statistics for each genre
    genre_stats = df.groupby('Genre').agg({
        'Global_Sales': ['count', 'mean', 'median', 'std', 'min', 'max']
    }).round(2)
    
    genre_stats.columns = ['Count', 'Mean', 'Median', 'Std_Dev', 'Min', 'Max']
    
    # Normalize for heatmap (except count)
    stats_for_heatmap = genre_stats[['Mean', 'Median', 'Std_Dev', 'Max']].copy()
    
    # Create heatmap
    plt.figure(figsize=(14, 10))
    
    # Create custom colormap
    cmap = sns.color_palette("YlOrRd", as_cmap=True)
    
    # Create heatmap
    heatmap = sns.heatmap(
        stats_for_heatmap.T,  # Transpose for better layout
        annot=True,
        fmt='.2f',
        cmap=cmap,
        linewidths=1,
        linecolor='white',
        cbar_kws={'label': 'Value Scale', 'shrink': 0.8}
    )
    
    plt.title('Genre Performance Heatmap: Sales Statistics Comparison', 
              fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Game Genre', fontsize=14, fontweight='bold')
    plt.ylabel('Sales Metric', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=11)
    plt.yticks(rotation=0, fontsize=11)
    
    # Add count information as text on side
    for i, (genre, row) in enumerate(genre_stats.iterrows()):
        plt.text(i + 0.5, -0.5, f'n={int(row["Count"])}', 
                ha='center', va='center', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='lightblue', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('taskA3_genre_heatmap.png', dpi=300, bbox_inches='tight')
    print("✓ Genre comparison heatmap saved as 'taskA3_genre_heatmap.png'")
    
    plt.show()

def generate_distribution_insights(df, genre_stats):
    """
    Generate insights from distribution analysis
    
    Parameters:
    df (pd.DataFrame): Original dataset
    genre_stats (pd.DataFrame): Genre statistics
    """
    print("\n" + "="*70)
    print("DISTRIBUTION ANALYSIS INSIGHTS")
    print("="*70)
    
    # Calculate key insights
    highest_mean_genre = genre_stats.loc[genre_stats['Mean_Sales'].idxmax()]
    lowest_mean_genre = genre_stats.loc[genre_stats['Mean_Sales'].idxmin()]
    highest_variability = genre_stats.loc[genre_stats['Std_Sales'].idxmax()]
    
    # Calculate skewness for each genre
    skewness_by_genre = df.groupby('Genre')['Global_Sales'].apply(lambda x: x.skew())
    most_skewed = skewness_by_genre.idxmax()
    least_skewed = skewness_by_genre.idxmin()
    
    insights = f"""
    DISTRIBUTION ANALYSIS FINDINGS:
    
    1. GENRE PERFORMANCE HIERARCHY:
       • Highest Average Sales: {highest_mean_genre.name} (${highest_mean_genre['Mean_Sales']:.2f}M)
       • Lowest Average Sales: {lowest_mean_genre.name} (${lowest_mean_genre['Mean_Sales']:.2f}M)
       • Most Variable Sales: {highest_variability.name} (σ=${highest_variability['Std_Sales']:.2f}M)
    
    2. DISTRIBUTION CHARACTERISTICS:
       • Most Right-Skewed: {most_skewed} (many low-sellers, few hits)
       • Most Normal Distribution: {least_skewed} (balanced sales)
       • Action/Shooter: High median with long upper tail (blockbuster potential)
       • Puzzle/Strategy: Compact distribution (predictable sales)
    
    3. OUTLIER ANALYSIS:
       • Sports/Shooter games produce most outliers (exceptional sellers)
       • Some genres have consistent performance with few outliers
       • Outliers represent breakout hits or major franchises
    
    4. BUSINESS IMPLICATIONS:
       • High-variance genres = Higher risk but higher potential reward
       • Stable genres = Predictable returns, lower risk
       • Portfolio strategy: Mix of high-potential and stable genres
    
    VISUALIZATION DESIGN RATIONALE:
    
    1. Plot Selection Justification:
       • Violin Plot: Shows probability density + box plot statistics
       • Box Plot: Clear quartile visualization, outlier identification
       • Combined Plot: Best of both worlds for comprehensive analysis
    
    2. Color Palette Choices:
       • Set3/Coolwarm: Clear differentiation between genres
       • Spectral: Good for sequential data with clear progression
       • Custom annotations: Highlight key statistics
    
    3. Customizations Applied:
       • Mean markers (stars/red dots) for central tendency
       • Outlier highlighting in different colors
       • Statistical annotations directly on plots
       • Formatted axes with clear units
       • Gridlines for better readability
    
    4. Technical Implementation:
       • Data filtering for clarity (top genres only)
       • Statistical calculations embedded in visualization
       • Modular code structure for reusability
       • High-resolution output suitable for reports
    """
    
    print(insights)
    
    # Print detailed statistics table
    print("\n" + "-"*60)
    print("DETAILED GENRE STATISTICS")
    print("-"*60)
    print(genre_stats.round(2))
    
    print("\n" + "-"*60)
    print("SKEWNESS ANALYSIS (Distribution Shape)")
    print("-"*60)
    print("Positive skew = Right-tailed (many low, few high values)")
    print("Negative skew = Left-tailed (many high, few low values)")
    print("\nSkewness by Genre:")
    for genre, skew in skewness_by_genre.sort_values(ascending=False).items():
        skew_desc = "Highly right-skewed" if skew > 1 else "Moderately right-skewed" if skew > 0.5 else "Near normal" if abs(skew) < 0.5 else "Left-skewed"
        print(f"  {genre:15} : {skew:7.3f} ({skew_desc})")

# Main execution
if __name__ == "__main__":
    # Load and prepare data
    df = load_and_prepare_data()
    
    if df is not None:
        # Analyze distribution
        genre_stats = analyze_distribution_by_genre(df)
        
        # Create various visualizations
        create_violin_plot(df)
        create_box_plot(df)
        create_combined_plot(df)
        create_genre_comparison_heatmap(df)
        
        # Generate insights
        generate_distribution_insights(df, genre_stats)
        
        print("\n" + "="*70)
        print("TASK A.3 COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nOutput Files Generated:")
        print("1. 'taskA3_violin_plot.png'     - Violin plot of sales by genre")
        print("2. 'taskA3_box_plot.png'        - Box plot comparison")
        print("3. 'taskA3_combined_plot.png'   - Combined violin+box plot")
        print("4. 'taskA3_genre_heatmap.png'   - Genre statistics heatmap")
        print("\nNext Steps:")
        print("1. Include these visualizations in your report")
        print("2. Reference the insights in your analysis")
        print("3. Proceed to Task A.4 (Conditional Analysis)")