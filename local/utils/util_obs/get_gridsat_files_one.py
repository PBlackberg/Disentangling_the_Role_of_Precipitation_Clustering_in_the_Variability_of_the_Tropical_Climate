'''
# ------------------
#  get gridsat data
# ------------------
'https://www.ncei.noaa.gov/data/geostationary-ir-channel-brightness-temperature-gridsat-b1/access/2001/'
'''
import os
import subprocess

def download_one(base_url, dest_base, year, month, day, hour):
    filename = f'GRIDSAT-B1.{year}.{month}.{day}.{hour}.v02r01.nc'
    # print(filename)
    # exit()
    url = f"{base_url}/{year}/{filename}"

    dest = f"{dest_base}/{year}"
    os.makedirs(dest, exist_ok=True)
    out = f'{dest}/{filename}'
    subprocess.run([
        "wget", "--continue", "--tries=5", "--timeout=30", "--waitretry=2",
        "-O", str(out), url
    ], check=False)

def main(base_url, dest_base, year, month, day, hour):
    download_one(base_url, dest_base, year, month, day, hour)

if __name__ == '__main__':
    base_url = "https://www.ncei.noaa.gov/data/geostationary-ir-channel-brightness-temperature-gridsat-b1/access"
    dest_base = "/Volumes/Elements_pb/work/data/GRIDSAT_data"
    year = 2003
    month = '01'
    day = '01'
    hour = '00'
    main(base_url, dest_base, year, month, day, hour)



