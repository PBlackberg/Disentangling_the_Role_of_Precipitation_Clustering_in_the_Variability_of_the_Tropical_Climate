# gadi
<br>
<img src='logo.png' align="right" height="139" />
This repository includes example scripts to fetch and pre-process data and generate metrics from observations and Global Climate Models (GCMs) participating the in Coupled Model Inter-comparison project phase 6 (CMIP6).

### Repository structure
```bash
├── gadi/
│   ├── get_metrics/
│   │   └── observations/
│   │       ├── ERA5/...
│   │       │   └── satfrac_timeseries/
│   │       │       ├── calc_metric.py
│   │       │       ├── main_func.py
│   │       │       └── submit_as_job.py
│   │       └── IMERG/...
│   │           ├── mean_area/
│   │           │   ├── plot_func/
│   │           │   │   └── map_subplot.py
│   │           │   ├── plots/...
│   │           │   │   └── snapshot_0.png
│   │           │   ├── calc_metric.py
│   │           │   ├── main_func.py
│   │           │   └── submit_as_job.py
│   │           └── pr_percentiles/
│   │               ├── calc_metric.py
│   │               ├── main_func.py
│   │               └── submit_as_job.py
│   ├── utils/...
│   │    ├── util_calc/...
│   │    │   └── doc_metrics/...
│   │    │       └── mean_area/
│   │    │           └── mean_area.py
│   │    ├── util_obs/...
│   │    │   ├── get_era5_data.py
│   │    │   └── get_imerg_data.py
│   │    ├── util_qsub/
│   │    │   ├── interactive_script.py
│   │    │   └── submission_funcs.py
│   │    └── user_specs.py
│   └── environment.yml
```

### How to use repository
First, change the paths in utils/user_specs.py such that the scripts know from where to save/load data and metrics. <br>
Next, change the working directory to where the "gadi" folder is. This is necessary as all scripts import the "utils" folder from the current working directory. <br>
To submit a metric calculation as a HPC job, run "submit_as_job.py". This script includes customizable settings for the calculation such as domain area, resolution, etc. <br>
To run metric calculation interactively, run main_func.py. This script still use the settings specified in "submit_as_job.py". <br>
If timestep data is saved, "calc_metric.py" can isolate the targeted calculation for quick plotting / printing. <br>

