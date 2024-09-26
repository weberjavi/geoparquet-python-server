import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import io
import math
from functools import lru_cache

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEOPARQUET_DIR = "./parquet"

@lru_cache(maxsize=1)
def load_all_geoparquet():
    geoparquet_files = [f for f in os.listdir(GEOPARQUET_DIR) if f.endswith('.parquet')]
    gdfs = []
    for file in geoparquet_files:
        file_path = os.path.join(GEOPARQUET_DIR, file)
        gdf = gpd.read_parquet(file_path)
        gdfs.append(gdf)
    combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    print(f"Loaded {len(combined_gdf)} total features")
    print(f"CRS of the data: {combined_gdf.crs}")
    print(f"Bounds of the data: {combined_gdf.total_bounds}")
    return combined_gdf

def tile_to_bbox(x, y, z):
    if z == 0:
        return (-180, -90, 180, 90)
    
    n = 2.0 ** z
    lon_deg_west = x / n * 360.0 - 180.0
    lon_deg_east = (x + 1) / n * 360.0 - 180.0
    
    lat_rad_north = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_rad_south = math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n)))
    
    lat_deg_north = math.degrees(lat_rad_north)
    lat_deg_south = math.degrees(lat_rad_south)
    
    return (lon_deg_west, lat_deg_south, lon_deg_east, lat_deg_north)

def gdf_to_geoparquet(gdf):
    buf = io.BytesIO()
    gdf.to_parquet(buf, index=False)
    buf.seek(0)
    return buf.getvalue()

@lru_cache(maxsize=1000)
def get_filtered_data(z: int, x: int, y: int):
    west, south, east, north = tile_to_bbox(x, y, z)
    bbox = box(west, south, east, north)
    
    all_data = load_all_geoparquet()
    
    # Ensure the CRS is set to EPSG:4326 (WGS84)
    if all_data.crs is None or all_data.crs != "EPSG:4326":
        print(f"Converting CRS from {all_data.crs} to EPSG:4326")
        all_data = all_data.to_crs("EPSG:4326")
    
    # Use 'intersects' for filtering, but add a small buffer to the bbox to catch edge cases
    buffered_bbox = bbox.buffer(0.000001)
    filtered_gdf = all_data[all_data.intersects(buffered_bbox)]
    
    print(f"Tile {z}/{x}/{y} - Bbox: {bbox.bounds}")
    print(f"All data: {len(all_data)} features")
    print(f"Filtered data: {len(filtered_gdf)} features")
    
    if filtered_gdf.empty:
        return None
    
    return gdf_to_geoparquet(filtered_gdf)

@app.get("/tile/{z}/{x}/{y}")
async def get_tile(z: int, x: int, y: int):
    geoparquet_bytes = get_filtered_data(z, x, y)
    
    if geoparquet_bytes is None:
        raise HTTPException(status_code=204, detail="No content")
    
    return Response(content=geoparquet_bytes, media_type="application/octet-stream", 
                    headers={"Content-Disposition": f"attachment; filename=tile_{z}_{x}_{y}.parquet"})

@app.get("/")
async def root():
    return {"message": "GeoParquet Tile Server with Caching"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)