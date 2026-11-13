import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def main():
    # Read and process the CSV file
    df = pd.read_csv('ICT505 A3.csv', header=None)
    
    # Extract the first column which contains all the data as a single string
    combined_data = df.iloc[:, 0]
    
    # Split the combined string into separate columns
    split_data = combined_data.str.split(',', expand=True)
    
    # Set the column names from the first row
    columns = split_data.iloc[0].str.replace('"', '')  # Remove quotes from column names
    split_data.columns = columns
    
    # Remove the first row (header) and reset index
    processed_df = split_data.iloc[1:].reset_index(drop=True)
    
    # Convert closing prices to numeric values
    processed_df['Close'] = pd.to_numeric(processed_df['Close'])
    
    # Create a category based on price ranges for visualization
    # We'll create price range categories
    price_bins = [0, 55, 60, 65, 70, 75, 80]
    price_labels = ['Under 55', '55-60', '60-65', '65-70', '70-75', '75+']
    processed_df['Price_Category'] = pd.cut(processed_df['Close'], bins=price_bins, labels=price_labels)
    
    # Set Seaborn style for professional appearance
    sns.set_style("whitegrid")
    sns.set_palette("husl")
    
    # Create the box plot
    plt.figure(figsize=(10, 6))
    box_plot = sns.boxplot(x='Price_Category', y='Close', data=processed_df)
    
    # Customize the plot
    plt.xlabel('Price Categories')
    plt.ylabel('Closing Price')
    plt.title('Distribution of Stock Closing Prices by Category')
    
    # Improve professional appearance
    plt.tight_layout()
    
    # Display the plot
    plt.show()

if __name__ == "__main__":
    main()