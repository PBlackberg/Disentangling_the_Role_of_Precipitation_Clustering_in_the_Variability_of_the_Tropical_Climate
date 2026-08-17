# local
<br>
<img src='logo.png' align="right" height="139" />
This repository includes scripts to generate all figures for the paper: "Large-Scale Clustering of Tropical Precipitation and its Implications for the Radiation Budget across Timescales" (excluding figures from the supporting information). <br>

### Repository structure
```bash
└── local/
    ├── get_metrics/
    │   └── observations/
    │       ├── CERES/...
    │       │    └── rad_timeseries_clouds/
    │       │        ├── calc_metric.py
    │       │        ├── main_func.py
    │       │        └── submit_as_job.py
    │       └── GRIDSAT/...
    │            └── i_org/
    │                ├── calc_metric.py
    │                ├── main_func.py
    │                └── submit_as_job.py
    ├── utils/
    │    ├── util_calc/...
    │    │   └── doc_metrics/...
    │    │       └── I_org/
    │    │           └── I_org_calc.py
    │    ├── util_obs/...
    │    │   ├── get_ceres_data.py
    │    │   ├── get_ceres_files.py
    │    │   ├── get_gridsat_data.py
    │    │   └── get_gridsat_files_one.py 
    │    └── user_specs.py
    └── environment.yml
```

### How to use repository
First, change the paths in utils/user_specs.py such that the scripts know from where to save/load data and metrics. <br>
Next, change the working directory to where the "local" folder is. This is necessary as all scripts import the "utils" folder from the current working directory. <br>
Finally, run any script with the desired metrics. <br>





