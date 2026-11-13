# Import necessary libraries
import geopandas as gpd
import matplotlib.pyplot as plt
import os

def main():
    # 1. Load a shapefile containing country/region boundaries
    # We'll use a different approach to get world map data
    try:
        # Try to use the built-in world dataset from GeoPandas
        # This might work in some installations
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        gdf = world
        print("Loaded built-in world dataset.")
    except:
        try:
            # Alternative approach: use a simple world map from a different source
            # Download a simple world boundaries GeoJSON file from GitHub
            import requests
            import json
            
            print("Downloading world boundaries data...")
            url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
            response = requests.get(url)
            
            if response.status_code == 200:
                # Save the GeoJSON data to a temporary file
                with open('countries.geojson', 'w') as f:
                    f.write(response.text)
                
                # Load the GeoJSON file with GeoPandas
                gdf = gpd.read_file('countries.geojson')
                print("Downloaded and loaded world boundaries data.")
            else:
                print("Failed to download world data.")
                return
        except Exception as e:
            print(f"Error loading world data: {e}")
            print("Please ensure you have an internet connection.")
            return
    
    # 2. Create a choropleth map with a numeric attribute
    # Since we're using simplified boundary data, we'll create a sample population density attribute
    # In a real scenario, you would join this with actual population data
    
    # Add a dummy population density attribute for visualization
    # This is just for demonstration purposes
    import numpy as np
    np.random.seed(42)  # For reproducible random values
    gdf['pop_density'] = np.random.randint(10, 1000, len(gdf))
    
    # Set up the plot
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Create the choropleth map
    gdf.plot(column='pop_density', 
             ax=ax, 
             legend=True, 
             cmap='OrRd',  # Color scheme
             edgecolor='black', 
             linewidth=0.5)
    
    # 3. Customize the map
    ax.set_title('Population Density by Region', fontsize=16, fontweight='bold')
    ax.set_axis_off()  # Remove axes
    
    # Add a legend title
    legend = ax.get_legend()
    if legend:
        legend.set_title('Population Density\n(people/km²)')
        # Adjust legend position if needed
        legend.set_bbox_to_anchor((1.05, 1))
    
    # Save the plot
    plt.savefig('choropleth_map.png', dpi=300, bbox_inches='tight')
    
    # Show the plot
    plt.show()
    
    print("Choropleth map created and saved as 'choropleth_map.png'")
    
    # Clean up temporary files
    if os.path.exists('countries.geojson'):
        os.remove('countries.geojson')

if __name__ == "__main__":
    main()