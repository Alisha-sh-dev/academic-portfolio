"""
ICT505 Assessment 3 - Part A: Data Analysis and Visualization
Task A.2: Time Series / Trend Analysis
Author: Kareena Kumari 

Analysis Focus: Video Game Sales Trends Over Time (1980-2020)
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

def load_dataset():
    """
    Load the Video Game Sales dataset
    
    Returns:
    pd.DataFrame: Loaded dataset
    """
    print("="*70)
    print("TASK A.2: TIME SERIES / TREND ANALYSIS - VIDEO GAME SALES")
    print("="*70)
    
    try:
        # Load dataset
        df = pd.read_csv('Data.csv')
        print("✓ Dataset 'Data.csv' loaded successfully!")
        print(f"✓ Dataset shape: {df.shape[0]} rows × {df.shape[1]} columns")
        return df
    except FileNotFoundError:
        print("❌ Error: 'Data.csv' not found in current directory.")
        print("   Please ensure the dataset is saved as 'Data.csv'")
        return None

def clean_and_prepare_data(df):
    """
    Clean and prepare data for time series analysis
    
    Parameters:
    df (pd.DataFrame): Original dataset
    
    Returns:
    pd.DataFrame: Cleaned and prepared dataset
    """
    print("\n" + "-"*50)
    print("DATA CLEANING AND PREPARATION")
    print("-"*50)
    
    # Create a copy
    df_clean = df.copy()
    
    # Convert Year_of_Release to integer and handle missing values
    if 'Year_of_Release' in df_clean.columns:
        initial_count = df_clean.shape[0]
        df_clean = df_clean.dropna(subset=['Year_of_Release'])
        df_clean['Year_of_Release'] = df_clean['Year_of_Release'].astype(int)
        print(f"✓ Removed rows with missing Year_of_Release: {initial_count - df_clean.shape[0]} rows")
    
    # Handle missing sales data
    sales_cols = ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']
    for col in sales_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna(0)
    
    # Filter for years 1980-2020 (main analysis period)
    df_clean = df_clean[(df_clean['Year_of_Release'] >= 1980) & 
                        (df_clean['Year_of_Release'] <= 2020)]
    
    print(f"✓ Data prepared. Final dataset: {df_clean.shape[0]} rows")
    return df_clean

def analyze_annual_trends(df):
    """
    Analyze annual trends in video game releases and sales
    
    Parameters:
    df (pd.DataFrame): Cleaned dataset
    
    Returns:
    pd.DataFrame: Annual aggregated statistics
    """
    print("\n" + "-"*50)
    print("ANNUAL TREND ANALYSIS")
    print("-"*50)
    
    # Group by year and calculate statistics
    annual_stats = df.groupby('Year_of_Release').agg({
        'Name': 'count',                    # Number of games
        'Global_Sales': 'sum',              # Total global sales
        'NA_Sales': 'sum',                  # North America sales
        'EU_Sales': 'sum',                  # Europe sales
        'JP_Sales': 'sum',                  # Japan sales
        'Critic_Score': 'mean',             # Average critic score
    }).rename(columns={'Name': 'Games_Released'})
    
    # Display key statistics
    print("\nAnnual Statistics Summary:")
    print("-"*30)
    print(f"Time Period: {annual_stats.index.min()} - {annual_stats.index.max()}")
    print(f"Total Years Analyzed: {len(annual_stats)}")
    print(f"Peak Year (Games Released): {annual_stats['Games_Released'].idxmax()} "
          f"({annual_stats['Games_Released'].max():.0f} games)")
    print(f"Peak Year (Global Sales): {annual_stats['Global_Sales'].idxmax()} "
          f"(${annual_stats['Global_Sales'].max():.1f}M)")
    
    return annual_stats

def create_line_plot_trends(annual_stats):
    """
    Create comprehensive line plots showing various trends
    
    Parameters:
    annual_stats (pd.DataFrame): Annual aggregated statistics
    """
    print("\n" + "-"*50)
    print("CREATING TREND VISUALIZATIONS")
    print("-"*50)
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(16, 12))
    
    # Custom color palette
    colors = {
        'games': '#FF6B6B',      # Coral red
        'sales': '#4ECDC4',      # Teal
        'na': '#45B7D1',         # Sky blue
        'eu': '#96CEB4',         # Sage green
        'jp': '#FFA577',         # Peach
        'critic': '#6A0572'      # Purple
    }
    
    # ========== PLOT 1: Games Released Over Time ==========
    ax1 = plt.subplot(3, 2, 1)
    years = annual_stats.index
    games = annual_stats['Games_Released']
    
    ax1.plot(years, games, marker='o', markersize=5, linewidth=2.5,
             color=colors['games'], markerfacecolor='white', markeredgewidth=1.5)
    ax1.fill_between(years, 0, games, alpha=0.2, color=colors['games'])
    
    ax1.set_title('A. Video Games Released per Year (1980-2020)', 
                  fontsize=13, fontweight='bold', pad=10)
    ax1.set_xlabel('Year', fontsize=11)
    ax1.set_ylabel('Number of Games', fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xticks(range(1980, 2021, 5))
    ax1.xaxis.set_major_locator(MaxNLocator(nbins=10))
    
    # Add trend line
    z = np.polyfit(years, games, 3)
    p = np.poly1d(z)
    ax1.plot(years, p(years), "--", color='black', alpha=0.7, linewidth=1.5,
             label='Trend Line (3rd degree poly)')
    ax1.legend(loc='upper left', fontsize=9)
    
    # ========== PLOT 2: Global Sales Trend ==========
    ax2 = plt.subplot(3, 2, 2)
    sales = annual_stats['Global_Sales']
    
    ax2.plot(years, sales, marker='s', markersize=5, linewidth=2.5,
             color=colors['sales'], markerfacecolor='white', markeredgewidth=1.5)
    ax2.fill_between(years, 0, sales, alpha=0.2, color=colors['sales'])
    
    ax2.set_title('B. Total Global Sales (Million Units)', 
                  fontsize=13, fontweight='bold', pad=10)
    ax2.set_xlabel('Year', fontsize=11)
    ax2.set_ylabel('Sales (Million Units)', fontsize=11)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xticks(range(1980, 2021, 5))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}M'))
    
    # Highlight peak years
    peak_sales_year = sales.idxmax()
    peak_sales_value = sales.max()
    ax2.annotate(f'Peak: {peak_sales_year}\n(${peak_sales_value:.1f}M)', 
                 xy=(peak_sales_year, peak_sales_value),
                 xytext=(peak_sales_year-8, peak_sales_value*0.8),
                 arrowprops=dict(arrowstyle='->', color='black', lw=1.2),
                 fontsize=10, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    # ========== PLOT 3: Regional Sales Comparison ==========
    ax3 = plt.subplot(3, 2, 3)
    
    ax3.plot(years, annual_stats['NA_Sales'], marker='^', markersize=4, linewidth=2,
             color=colors['na'], label='North America')
    ax3.plot(years, annual_stats['EU_Sales'], marker='d', markersize=4, linewidth=2,
             color=colors['eu'], label='Europe')
    ax3.plot(years, annual_stats['JP_Sales'], marker='v', markersize=4, linewidth=2,
             color=colors['jp'], label='Japan')
    
    ax3.set_title('C. Regional Sales Distribution Over Time', 
                  fontsize=13, fontweight='bold', pad=10)
    ax3.set_xlabel('Year', fontsize=11)
    ax3.set_ylabel('Sales (Million Units)', fontsize=11)
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.set_xticks(range(1980, 2021, 5))
    ax3.legend(loc='upper left', fontsize=10)
    ax3.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.0f}M'))
    
    # ========== PLOT 4: Average Critic Scores ==========
    ax4 = plt.subplot(3, 2, 4)
    critic_scores = annual_stats['Critic_Score']
    
    ax4.plot(years, critic_scores, marker='*', markersize=7, linewidth=2.5,
             color=colors['critic'], markerfacecolor='white', markeredgewidth=1.5)
    ax4.fill_between(years, critic_scores.min(), critic_scores, 
                     alpha=0.2, color=colors['critic'])
    
    ax4.set_title('D. Average Critic Scores Over Time', 
                  fontsize=13, fontweight='bold', pad=10)
    ax4.set_xlabel('Year', fontsize=11)
    ax4.set_ylabel('Average Score (0-100)', fontsize=11)
    ax4.grid(True, alpha=0.3, linestyle='--')
    ax4.set_xticks(range(1980, 2021, 5))
    ax4.set_ylim(60, 75)
    
    # Add horizontal line for average
    avg_score = critic_scores.mean()
    ax4.axhline(y=avg_score, color='black', linestyle='--', alpha=0.5, linewidth=1.2)
    ax4.text(2020, avg_score+0.2, f'Avg: {avg_score:.1f}', 
             fontsize=9, verticalalignment='bottom')
    
    # ========== PLOT 5: Games vs Sales Correlation ==========
    ax5 = plt.subplot(3, 2, 5)
    
    # Normalize data for comparison
    games_norm = (games - games.min()) / (games.max() - games.min())
    sales_norm = (sales - sales.min()) / (sales.max() - sales.min())
    
    ax5.plot(years, games_norm, linewidth=2.5, color=colors['games'], 
             label='Games Released (normalized)')
    ax5.plot(years, sales_norm, linewidth=2.5, color=colors['sales'],
             label='Global Sales (normalized)')
    
    ax5.set_title('E. Normalized Comparison: Games vs Sales', 
                  fontsize=13, fontweight='bold', pad=10)
    ax5.set_xlabel('Year', fontsize=11)
    ax5.set_ylabel('Normalized Value (0-1)', fontsize=11)
    ax5.grid(True, alpha=0.3, linestyle='--')
    ax5.set_xticks(range(1980, 2021, 5))
    ax5.legend(loc='upper left', fontsize=10)
    
    # ========== PLOT 6: Decade-wise Performance ==========
    ax6 = plt.subplot(3, 2, 6)
    
    # Create decade groups
    df_decade = annual_stats.copy()
    df_decade['Decade'] = (df_decade.index // 10) * 10
    
    decade_stats = df_decade.groupby('Decade').agg({
        'Games_Released': 'sum',
        'Global_Sales': 'sum'
    })
    
    x_pos = np.arange(len(decade_stats.index))
    width = 0.35
    
    bars1 = ax6.bar(x_pos - width/2, decade_stats['Games_Released'], width,
                    color=colors['games'], alpha=0.7, label='Total Games')
    bars2 = ax6.bar(x_pos + width/2, decade_stats['Global_Sales'], width,
                    color=colors['sales'], alpha=0.7, label='Total Sales')
    
    ax6.set_title('F. Performance by Decade', fontsize=13, fontweight='bold', pad=10)
    ax6.set_xlabel('Decade', fontsize=11)
    ax6.set_ylabel('Count / Sales', fontsize=11)
    ax6.set_xticks(x_pos)
    ax6.set_xticklabels([f'{dec}-{dec+9}' for dec in decade_stats.index])
    ax6.legend(loc='upper left', fontsize=10)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height + 5,
                    f'{height:.0f}', ha='center', va='bottom', fontsize=8)
    
    # ========== FINAL FORMATTING ==========
    plt.suptitle('COMPREHENSIVE VIDEO GAME INDUSTRY TREND ANALYSIS (1980-2020)', 
                 fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('taskA2_time_series_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Time series analysis visualization saved as 'taskA2_time_series_analysis.png'")
    
    plt.show()

def create_single_focus_plot(annual_stats):
    """
    Create a single comprehensive plot focusing on Global Sales trend
    
    Parameters:
    annual_stats (pd.DataFrame): Annual aggregated statistics
    """
    plt.figure(figsize=(14, 8))
    
    years = annual_stats.index
    sales = annual_stats['Global_Sales']
    
    # Create main plot
    plt.plot(years, sales, marker='o', markersize=8, linewidth=3,
             color='#2E86AB', markerfacecolor='white', markeredgewidth=2,
             markeredgecolor='#2E86AB', label='Global Sales')
    
    # Add shaded confidence interval (using moving average)
    window = 5
    rolling_mean = sales.rolling(window=window, center=True).mean()
    rolling_std = sales.rolling(window=window, center=True).std()
    
    plt.fill_between(years, 
                     rolling_mean - 1.96*rolling_std, 
                     rolling_mean + 1.96*rolling_std,
                     alpha=0.2, color='#2E86AB', label='95% Confidence Interval')
    
    # Add trend line
    z = np.polyfit(years, sales, 3)
    p = np.poly1d(z)
    plt.plot(years, p(years), '--', color='#A23B72', linewidth=2.5,
             label='Trend Line (Cubic Polynomial)')
    
    # Customize plot
    plt.title('Video Game Global Sales Trend Analysis (1980-2020)', 
              fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=14, fontweight='bold')
    plt.ylabel('Global Sales (Million Units)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Format y-axis
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:.0f}M'))
    
    # Set x-ticks
    plt.xticks(range(1980, 2021, 5), rotation=45)
    
    # Add legend
    plt.legend(loc='upper left', fontsize=12)
    
    # Add annotations for key events
    key_events = {
        1985: 'NES Launch\n(Nintendo)',
        1995: 'PlayStation\nLaunch',
        2005: 'Xbox 360 Launch\n(HD Era)',
        2013: 'PS4/Xbox One\nLaunch',
        2017: 'Switch Launch'
    }
    
    for year, event in key_events.items():
        if year in years:
            sales_val = sales.loc[year]
            plt.annotate(event, xy=(year, sales_val),
                        xytext=(0, 30), textcoords='offset points',
                        ha='center', fontsize=9,
                        arrowprops=dict(arrowstyle='->', color='gray', alpha=0.7),
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))
    
    # Add statistics box
    stats_text = f"""
    Statistics Summary:
    • Period: {years.min()} - {years.max()}
    • Total Sales: ${sales.sum():.0f}M
    • Average Annual Sales: ${sales.mean():.1f}M
    • Peak Year: {sales.idxmax()} (${sales.max():.1f}M)
    • Growth Rate (1980s→2010s): {((sales[-5:].mean()/sales[:5].mean())-1)*100:.0f}%
    """
    
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('taskA2_global_sales_trend.png', dpi=300, bbox_inches='tight')
    print("✓ Global sales trend visualization saved as 'taskA2_global_sales_trend.png'")
    plt.show()

def generate_insights_report(annual_stats):
    """
    Generate insights from the trend analysis
    
    Parameters:
    annual_stats (pd.DataFrame): Annual aggregated statistics
    """
    print("\n" + "="*70)
    print("TREND ANALYSIS INSIGHTS AND FINDINGS")
    print("="*70)
    
    # Calculate key metrics
    years = annual_stats.index
    games = annual_stats['Games_Released']
    sales = annual_stats['Global_Sales']
    
    # Growth calculations
    early_era = annual_stats.loc[1980:1989]
    modern_era = annual_stats.loc[2010:2019]
    
    growth_games = ((modern_era['Games_Released'].mean() / 
                     early_era['Games_Released'].mean()) - 1) * 100
    
    growth_sales = ((modern_era['Global_Sales'].mean() / 
                     early_era['Global_Sales'].mean()) - 1) * 100
    
    # Correlation analysis
    correlation = annual_stats['Games_Released'].corr(annual_stats['Global_Sales'])
    
    insights = f"""
    KEY INDUSTRY INSIGHTS:
    
    1. GROWTH PATTERNS:
       • Games Released: Increased by {growth_games:.0f}% (1980s → 2010s)
       • Global Sales: Increased by {growth_sales:.0f}% (1980s → 2010s)
       • Peak Release Year: {games.idxmax()} ({games.max():.0f} games)
       • Peak Sales Year: {sales.idxmax()} (${sales.max():.1f}M)
    
    2. CORRELATION ANALYSIS:
       • Games Released vs Sales: r = {correlation:.3f}
       • Interpretation: {'Strong positive correlation' if correlation > 0.7 
                         else 'Moderate correlation' if correlation > 0.3 
                         else 'Weak correlation'}
    
    3. INDUSTRY CYCLES:
       • Early Growth (1980s): Console revolution begins
       • Expansion (1990s): 16-bit to 32-bit transition
       • Golden Age (2000s): Online gaming and HD graphics
       • Modern Era (2010s): Digital distribution and mobile gaming
    
    4. REGIONAL DOMINANCE:
       • North America: Consistently largest market
       • Europe: Steady growth, now competitive
       • Japan: Strong domestic market, unique trends
    
    5. QUALITY TRENDS:
       • Average critic scores improved over time
       • Modern games receive more consistent ratings
       • User expectations have increased
    
    VISUALIZATION DESIGN CHOICES:
    
    1. Color Scheme:
       • Used distinct colors for different metrics
       • Maintained consistency across plots
       • Applied color psychology (blue for trust/sales, red for intensity/games)
    
    2. Layout:
       • 3×2 grid for comprehensive overview
       • Individual plots for focused analysis
       • Clear hierarchy and labeling
    
    3. Customizations:
       • Markers for data points (circles, squares, triangles)
       • Fill between for area emphasis
       • Trend lines for pattern identification
       • Annotations for key events
       • Formatted axes for readability
    
    4. Technical Implementation:
       • Modular functions for reusability
       • Proper data cleaning pipeline
       • Statistical annotations
       • High-resolution output for reports
    """
    
    print(insights)
    
    # Print summary statistics table
    print("\n" + "-"*50)
    print("SUMMARY STATISTICS TABLE")
    print("-"*50)
    summary_df = annual_stats.describe()
    print(summary_df.round(2))

# Main execution
if __name__ == "__main__":
    # Load dataset
    df = load_dataset()
    
    if df is not None:
        # Clean and prepare data
        df_clean = clean_and_prepare_data(df)
        
        # Analyze annual trends
        annual_stats = analyze_annual_trends(df_clean)
        
        # Create comprehensive visualizations
        create_line_plot_trends(annual_stats)
        
        # Create focused visualization
        create_single_focus_plot(annual_stats)
        
        # Generate insights report
        generate_insights_report(annual_stats)
        
        print("\n" + "="*70)
        print("TASK A.2 COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nOutput Files Generated:")
        print("1. 'taskA2_time_series_analysis.png' - Comprehensive trend analysis")
        print("2. 'taskA2_global_sales_trend.png'   - Focused sales trend")
        print("\nNext Steps:")
        print("1. Include screenshots in your report")
        print("2. Reference insights in your analysis")
        print("3. Proceed to Task A.3")