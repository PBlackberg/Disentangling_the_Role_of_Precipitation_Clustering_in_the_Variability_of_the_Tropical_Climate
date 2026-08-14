import os, subprocess
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://asdc.larc.nasa.gov/data/CERES/SYN1deg-Day/Terra-Aqua-NOAA20_Edition4B"
DEST_BASE = "/Volumes/satellite1/work/data/CERES_data"
WORKERS = 4             # 4–8 is sane
MIN_BYTES = 2_000_000   # ~1 MB sanity

def days(start=date(2001,1,1), end=date(2023,12,31)):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)

def relogin():
    subprocess.run([
        "wget","-qO-",
        "--save-cookies", os.path.expanduser("~/.urs_cookies"),
        "--keep-session-cookies","--auth-no-challenge=on",
        "https://asdc.larc.nasa.gov/data/CERES/SYN1deg-Day/"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def fetch_one(d):
    year, month, day = f"{d:%Y}", f"{d:%m}", f"{d:%d}"

    # == find the id code ==
    ID_code = '401412'                                                      # CER_SYN1deg-Day_Terra-Aqua-NOAA20_Edition4B_401412.20150601.hdf
    if (int(year) == 2015 and int(month) >= 7) or (int(year) > 2015):       # CER_SYN1deg-Day_Terra-Aqua-NOAA20_Edition4B_405412.20150701.hdf
        ID_code = '405412'                  

    if (int(year) == 2016 and int(month) >= 3) or (int(year) > 2016):
        ID_code = '406412'
    
    if (int(year) == 2018 and int(month) >= 2) or (int(year) > 2018):
        ID_code = '407412'
    
    if (int(year) == 2020 and int(month) >= 6) or (int(year) > 2020):
        ID_code = '408412'
    
    if (int(year) == 2021 and int(month) >= 9) or (int(year) > 2021):
        ID_code = '409412'

    fname_hdf = f"CER_SYN1deg-Day_Terra-Aqua-NOAA20_Edition4B_{ID_code}.{year}{month}{day}.hdf"
    url = f"{BASE_URL}/{year}/{month}/{fname_hdf}"
    dest_dir = f"{DEST_BASE}/{year}"; os.makedirs(dest_dir, exist_ok=True)
    out_hdf = f"{dest_dir}/{fname_hdf}"
    out_nc  = out_hdf.replace(".hdf", ".nc")
    if os.path.exists(out_nc): return 0

    for attempt in range(3):
        rc = subprocess.run([
            "wget","--continue","--tries=5","--timeout=60","--waitretry=3",
            "--load-cookies", os.path.expanduser("~/.urs_cookies"),
            "--save-cookies", os.path.expanduser("~/.urs_cookies"),
            "--keep-session-cookies","--auth-no-challenge=on",
            "--content-disposition","-O", out_hdf, url
        ]).returncode
        ok = (rc == 0 and os.path.exists(out_hdf) and os.path.getsize(out_hdf) >= MIN_BYTES)
        if ok: 
            break
        try: 
            os.remove(out_hdf)
        except FileNotFoundError: 
            pass
        # relogin()

    if not ok: 
        return 1

    rc = subprocess.run(["ncks","-O", out_hdf, out_nc]).returncode
    if rc == 0 and os.path.exists(out_nc):
        try: os.remove(out_hdf)
        except OSError: pass

    return rc


if __name__ == "__main__":
    # relogin()  
    todo = [d for d in days(start=date(2004,1,1), end=date(2004,12,31))]
    # fetch_one(todo[0])
    # exit()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        fut = {ex.submit(fetch_one, d): d for d in todo}
        for f in as_completed(fut):
            if f.result() != 0:
                print("Failed:", fut[f])
