import pandas as pd
import matplotlib.pyplot as plt

def main():
    # Read the CSV file with proper handling of the structure
    df = pd.read_csv('ICT505 A3.csv', header=None)
    
    # The data is all in the first column, so we need to split it
    # Extract the first column which contains all the data as a single string
    combined_data = df.iloc[:, 0]
    
    # Split the combined string into separate columns
    split_data = combined_data.str.split(',', expand=True)
    
    # Set the column names from the first row
    columns = split_data.iloc[0].str.replace('"', '')  # Remove quotes from column names
    split_data.columns = columns
    
    # Remove the first row (header) and reset index
    processed_df = split_data.iloc[1:].reset_index(drop=True)
    
    # Convert date strings to datetime objects
    processed_df['Date'] = pd.to_datetime(processed_df['Date'])
    
    # Convert closing prices to numeric values
    processed_df['Close'] = pd.to_numeric(processed_df['Close'])
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(processed_df['Date'], processed_df['Close'], 
             marker='o', linestyle='-', linewidth=1, markersize=3)
    
    # Enhance the plot with labels and title
    plt.xlabel('Date')
    plt.ylabel('Closing Price')
    plt.title('Stock Closing Prices Over Time')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Rotate date labels for better readability
    plt.xticks(rotation=45)
    
    # Adjust layout to prevent cutting off labels
    plt.tight_layout()
    
    # Display the plot
    plt.show()

if __name__ == "__main__":
    main()