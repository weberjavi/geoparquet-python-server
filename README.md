# GeoParquet Tile Server

This project implements a tile server that serves GeoParquet data based on tile coordinates (z, x, y). It's designed to efficiently handle large geospatial datasets stored in GeoParquet format and serve subsets of this data for specific geographic areas.

## Features

- Serves GeoParquet data for requested tiles
- Supports caching for improved performance
- Filters data based on tile boundaries
- Preserves original geometry information
- Built with FastAPI for high performance

## Requirements

- Python 3.7+
- FastAPI
- GeoPandas
- PyArrow
- Shapely

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/geoparquet-tile-server.git
   cd geoparquet-tile-server
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv geostuff
   source geostuff/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install fastapi uvicorn geopandas pyarrow shapely
   ```

## Configuration

1. Open the `tile-based-geoparquet-server.py` file.
2. Locate the `GEOPARQUET_DIR` variable and set it to the path of your directory containing GeoParquet files:
   ```python
   GEOPARQUET_DIR = "/path/to/your/geoparquet/files"
   ```

## Usage

1. Start the server:
   ```
   python tile-based-geoparquet-server.py
   ```

2. The server will start running on `http://localhost:8000`.

3. To request a tile, use the following URL format:
   ```
   http://localhost:8000/tile/{z}/{x}/{y}
   ```
   Where `{z}` is the zoom level, and `{x}` and `{y}` are the tile coordinates.

4. The server will respond with a GeoParquet file containing the data for the requested tile.

## API Endpoints

- `GET /tile/{z}/{x}/{y}`: Retrieve GeoParquet data for a specific tile.
- `GET /`: A simple health check endpoint that returns a message indicating the server is running.

## Performance Considerations

- The server uses caching to improve performance for repeated requests.
- For large datasets, consider implementing additional optimizations such as pre-filtering or creating spatial indexes.



---

Remember to star this repository if you find it useful!
