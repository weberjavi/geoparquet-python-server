import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import geopandas as gpd
import pyarrow as pa
import pyarrow.parquet as pq
from shapely.geometry import box
import io
import math

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Directory containing GeoParquet files
GEOPARQUET_DIR = "path/to/your/geoparquet/files"

def load_geoparquet(file_path):
    return gpd.read_parquet(file_path)

def tile_to_bbox(x, y, z):
    n = 2.0 ** z
    lon_deg = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return (lon_deg, lat_deg, lon_deg + 360 / n, lat_deg + (lat_deg - math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y+1) / n))))))

@app.get("/tile/{z}/{x}/{y}")
async def get_tile(z: int, x: int, y: int):
    west, south, east, north = tile_to_bbox(x, y, z)
    bbox = box(west, south, east, north)

    # List all GeoParquet files in the directory
    geoparquet_files = [f for f in os.listdir(GEOPARQUET_DIR) if f.endswith('.parquet')]

    combined_gdf = gpd.GeoDataFrame()

    for file in geoparquet_files:
        file_path = os.path.join(GEOPARQUET_DIR, file)
        gdf = load_geoparquet(file_path)
        
        # Filter geometries within the bounding box
        filtered_gdf = gdf[gdf.intersects(bbox)]
        
        if not filtered_gdf.empty:
            combined_gdf = combined_gdf.append(filtered_gdf)

    if combined_gdf.empty:
        raise HTTPException(status_code=204, detail="No content")

    # Convert the GeoDataFrame to a PyArrow Table
    table = pa.Table.from_pandas(combined_gdf)

    # Write the PyArrow Table to a bytes buffer in Parquet format
    buf = io.BytesIO()
    pq.write_table(table, buf)

    # Get the bytes from the buffer
    parquet_bytes = buf.getvalue()

    return Response(content=parquet_bytes, media_type="application/octet-stream", 
                    headers={"Content-Disposition": f"attachment; filename=tile_{z}_{x}_{y}.parquet"})

@app.get("/")
async def root():
    return {"message": "GeoParquet Tile Server"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
