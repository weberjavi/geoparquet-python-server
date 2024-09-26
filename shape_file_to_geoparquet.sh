#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 <input_shapefile> <output_geoparquet>"
    exit 1
}

# Check if correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    usage
fi

input_shapefile=$1
output_geoparquet=$2

# Function to get the geometry type
get_geom_type() {
    ogrinfo -so -q "$1" | grep 'Geometry:' | awk '{print $2}'
}

# Get the geometry type of the input shapefile
geom_type=$(get_geom_type "$input_shapefile")

# Define the corresponding OGR geometry type
case $geom_type in
    Point)              ogr_type="POINT" ;;
    Line|LineString)    ogr_type="LINESTRING" ;;
    Polygon)            ogr_type="POLYGON" ;;
    Multi*)             ogr_type="${geom_type^^}" ;;
    *)                  ogr_type="GEOMETRY" ;;  # Default to generic geometry
esac

echo "Detected geometry type: $geom_type"
echo "Using OGR type: $ogr_type"

# Convert shapefile to GeoPackage (intermediate step)
ogr2ogr -f "GPKG" -nlt $ogr_type temp.gpkg "$input_shapefile"

# Convert GeoPackage to GeoParquet
ogr2ogr -f "Parquet" "$output_geoparquet" temp.gpkg

# Clean up temporary file
rm temp.gpkg

echo "Conversion complete. GeoParquet file saved as $output_geoparquet"