#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 <input_directory> <output_directory>"
    exit 1
}

# Check if correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    usage
fi

input_directory=$1
output_directory=$2

# Create output directory if it doesn't exist
mkdir -p "$output_directory"

# Function to get the geometry type
get_geom_type() {
    ogrinfo -so -q "$1" | grep 'Geometry:' | awk '{print $2}'
}

# Process each shapefile in the input directory
for shp_file in "$input_directory"/*.shp; do
    # Check if the file exists (in case no .shp files were found)
    [ -e "$shp_file" ] || continue

    # Get the base name of the shapefile (without extension)
    base_name=$(basename "$shp_file" .shp)

    # Check if all required files exist
    for ext in .shp .shx .dbf .prj; do
        if [ ! -f "${input_directory}/${base_name}${ext}" ]; then
            echo "Skipping $base_name: Missing ${ext} file"
            continue 2
        fi
    done

    # Get the geometry type of the input shapefile
    geom_type=$(get_geom_type "$shp_file")

    # Define the corresponding OGR geometry type
    case $geom_type in
        Point)              ogr_type="POINT" ;;
        Line|LineString)    ogr_type="LINESTRING" ;;
        Polygon)            ogr_type="POLYGON" ;;
        Multi*)             ogr_type="${geom_type^^}" ;;
        *)                  ogr_type="GEOMETRY" ;;  # Default to generic geometry
    esac

    echo "Processing $base_name (Geometry type: $geom_type, OGR type: $ogr_type)"

    # Convert shapefile to GeoPackage (intermediate step)
    ogr2ogr -f "GPKG" -nlt $ogr_type "${output_directory}/${base_name}_temp.gpkg" "$shp_file"

    # Convert GeoPackage to GeoParquet
    ogr2ogr -f "Parquet" "${output_directory}/${base_name}.parquet" "${output_directory}/${base_name}_temp.gpkg"

    # Clean up temporary file
    rm "${output_directory}/${base_name}_temp.gpkg"

    echo "Conversion complete. GeoParquet file saved as ${output_directory}/${base_name}.parquet"
done

echo "All shapefiles processed."