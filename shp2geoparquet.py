import geopandas as gpd
import pyarrow as pa
import pyarrow.parquet as pq

def shapefile_to_geoparquet(input_shapefile, output_geoparquet):
    # Read the shapefile
    gdf = gpd.read_file(input_shapefile)
    
    # Convert to GeoParquet
    table = pa.Table.from_pandas(gdf)
    
    # Write to GeoParquet file
    pq.write_table(table, output_geoparquet, compression='snappy')

    print(f"Conversion complete. GeoParquet file saved as {output_geoparquet}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_shapefile> <output_geoparquet>")
        sys.exit(1)
    
    input_shapefile = sys.argv[1]
    output_geoparquet = sys.argv[2]
    
    shapefile_to_geoparquet(input_shapefile, output_geoparquet)