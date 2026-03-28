import geopandas as gpd

# baca shapefile
gdf = gpd.read_file("map_gedung.shp")

# simpan jadi geojson
gdf.to_file("map_gedung.geojson", driver="GeoJSON")