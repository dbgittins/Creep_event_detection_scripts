import cdsapi
import os
import sys
from multiprocessing import Pool, cpu_count
from pathlib import Path

# Region metadata
regions = {
    'Hayward':    {'area': [38.1, -122.4, 37.25, -121.8], 'ST': 1993, 'ET': 2024},
    'Hollister':  {'area': [37, -121.75, 36.5, -121],     'ST': 1980, 'ET': 2024},
    'Parkfield':  {'area': [36.1, -120.75, 35.5, -120.1], 'ST': 1984, 'ET': 2024},
    'SoCal':      {'area': [34, -117.25, 32.4, -115.25],  'ST': 2004, 'ET': 2024},
    'Ridgecrest': {'area': [35.8, -118, 35.2, -117],      'ST': 2019, 'ET': 2024},
    'NAF':        {'area': [29.5, 41.1, 33.1, 40.4],       'ST': 2014, 'ET': 2024},
    'EAF':        {'area': [36, 39, 40.25, 36],            'ST': 2017, 'ET': 2024},
    'UTA':        {'area': [-114.2, 42.2, -108.5, 36.8],   'ST': 2012, 'ET': 2018},
    'Pakistan':   {'area': [61, 38, 78, 23],               'ST': 2019, 'ET': 2021},
    'Israel':     {'area': [34.2, 33.3, 35.9, 29.4],       'ST': 2021, 'ET': 2024}
}

def download_era5_for_region(region_name, save_dir="./era5_data", log_dir="./logs"):
    if region_name not in regions:
        raise ValueError(f"Region '{region_name}' not found in the regions dictionary.")

    region_info = regions[region_name]
    area = region_info['area']
    start_year = region_info['ST']
    end_year = region_info['ET']

    os.makedirs(save_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"{region_name}.log")
    completed_chunks = set()
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            completed_chunks = {line.strip() for line in f.readlines()}

    client = cdsapi.Client()
    results = {}

    for chunk_start in range(start_year, end_year + 1, 4):
        chunk_end = min(chunk_start + 3, end_year)
        chunk_id = f"{chunk_start}-{chunk_end}"
        filename = f"era5_{region_name}_{chunk_start}_{chunk_end}.grib"
        filepath = os.path.join(save_dir, filename)

        if chunk_id in completed_chunks and os.path.exists(filepath):
            print(f"[{region_name}] Skipping {chunk_id} (already downloaded)")
            continue

        print(f"[{region_name}] Requesting ERA5 data for {chunk_id}...")

        try:
            years = [str(y) for y in range(chunk_start, chunk_end + 1)]
            request = {
                "product_type": "reanalysis",
                "variable": ["surface_pressure", "total_precipitation"],
                "year": years,
                "month": ["{:02}".format(m) for m in range(1, 13)],
                "day": ["{:02}".format(d) for d in range(1, 32)],
                "time": ["{:02}:00".format(t) for t in range(24)],
                "area": area,
                "format": "grib"
            }

            client.retrieve("reanalysis-era5-single-levels", request).download(filepath)

            # Write to log file
            with open(log_file, "a") as log:
                log.write(f"{chunk_id}\n")

            results[chunk_id] = filepath
        except Exception as e:
            print(f"[{region_name}] Failed to download {chunk_id}: {e}")
            continue

    return results

# Allow command-line usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_era5.py <RegionName|all> [num_cores]")
        print(f"Available regions: {', '.join(regions.keys())}")
        sys.exit(1)

    target = sys.argv[1]
    num_cores = int(sys.argv[2]) if len(sys.argv) >= 3 else 2

    if target == "all":
        region_list = list(regions.keys())
        print(f"Downloading all regions using {num_cores} cores...")
        with Pool(processes=min(num_cores, cpu_count())) as pool:
            pool.map(download_era5_for_region, region_list)
    else:
        download_era5_for_region(target)
