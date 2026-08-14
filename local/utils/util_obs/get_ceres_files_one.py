'''
# ------------------
#  get ceres data
# ------------------
wget -r -np -nH --cut-dirs=5 https://asdc.larc.nasa.gov/data/CERES/SYN1deg-Day/Terra-Aqua-MODIS_Edition4A/2003/
'''
import os
import subprocess
import calendar

def download_one(base_url, dest_base, year, month, day, hour):
    end_day = calendar.monthrange(year, int(month))[1]
    # filename = f'CER_SYN1deg-Day_Terra-Aqua-NOAA20_Edition4B_401412.{year}{month}{day}.hdf'

    filename = f'CER_SYN1deg-Day_Terra-Aqua-NOAA20_Edition4B_406412.{year}{month}{day}.hdf'

    url = f"{base_url}/{year}/{month}/{filename}"
    dest = f"{dest_base}/{year}"
    os.makedirs(dest, exist_ok=True)
    out = f'{dest}/{filename}'
    subprocess.run([
        "wget","--continue","--tries=5","--timeout=30","--waitretry=2",
        "--load-cookies", os.path.expanduser("~/.urs_cookies"),
        "--save-cookies", os.path.expanduser("~/.urs_cookies"),
        "--keep-session-cookies","--auth-no-challenge=on",
        "--content-disposition","-O", out, url
    ], check=False)

    nc_out = out.replace(".hdf", ".nc")
    if not os.path.exists(nc_out):
        subprocess.run(["ncks", "-O", out, nc_out], check=False)

    if os.path.exists(nc_out):
        os.remove(out)

def main(base_url, dest_base, year, month, day, hour):
    download_one(base_url, dest_base, year, month, day, hour)

if __name__ == '__main__':
    base_url = 'https://asdc.larc.nasa.gov/data/CERES/SYN1deg-Day/Terra-Aqua-NOAA20_Edition4B/'
    dest_base = "/Volumes/satellite1/work/data/CERES_data"
    year = 2017
    month = '06'
    day = '01'
    hour = '00'
    main(base_url, dest_base, year, month, day, hour)



    # -- key variables --
    # obs_all_toa_net
    # clr_*: clear-sky fluxes.
    # obs_all_toa_sw, obs_all_toa_lw, obs_all_toa_net
    # obs_clr_toa_sw, obs_clr_toa_lw, obs_clr_toa_net


# "/Volumes/satellite1/work/data/CERES_data/2017/CER_SYN1deg-Day_Terra-Aqua-NOAA20_Edition4B_401412.20170101.hdf"
# '/Volumes/satellite1/work/data/CERES_data/2017/CER_SYN1deg-Day_Terra-Aqua-NOAA20_Edition4B_401412.20170101.hdf'









