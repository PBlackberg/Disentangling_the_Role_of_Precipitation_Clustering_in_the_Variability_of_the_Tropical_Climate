# Disentangling the Role of Precipitation Clustering in the Variability of the Tropical Climate
<br>
<img src='logo.png' align="right" height="139" />
This Github repository includes scripts that show how metrics were generated for the paper: <br>
"Disentangling the Role of Precipitation Clustering in the Variability of the Tropical Climate" <br>

<br>

**Authors** [name, affiliation, email, github username]  
[Philip Blackberg,      Monash University,              philip.blackberg@monash.edu,    [PBlackberg](https://github.com/PBlackberg?tab=repositories)] (corresponding) <br>
[Martin Singh,          Monash University,              martin.singh@monash.edu,        [mssingh](https://github.com/mssingh?tab=repositories)]

**Abstract** <br>
The spatial organisation of deep convection is known to play an important role in modulating the tropical radiation budget, 
through its connection to clear-sky and cloud-radiative feedbacks. 
In this study, we examine the relationships between different aspects of convective organisation 
and the cloud and humidity distribution of the deep tropics 
in observed variability of the climate system.
By decomposing the commonly 1-dimensional description of organisation into one measure of the number of convective elements (coverage) 
and another measure of how close together convective elements are (coalescence). 
we show that these two components of convective clustering connect to the tropical environment in different ways. 
In particular, we find that high coverage is associated with a moister atmosphere and more extensive high cloudiness, 
while high coalescence is associated with a warmer and drier free troposphere. 
Further, we show that coverage and coalescence tend to oscillate from one to the other on intraseasonal timescales.
The temporal evolution of clustering and the tropical convective environment suggests that coverage and coalescence 
help to maintain a recently-identified tropics-wide intraseasonal oscillation (TWISO). 
These findings highlight the importance of considering both coverage and coalescence aspects of convective clustering, 
when assessing the degree to which convection is in a more organised state, 
and help elucidate processes contributing to variations in convective organisation in the deep tropics. 

### Repository structure
```bash
Disentangling_the_Role_of_Precipitation_Clustering_in_the_Variability_of_the_Tropical_Climate/
├── LICENCE
├── README.md
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
Scripts to generate metrics from IMERG rainfall data and ERA5 re-analysis data are found in the "gadi" folder. <br>
Scripts to generate metrics from GRIDSAT-B1 brightness temperature data and CERES syn1deg data are found in the "local" folder. <br>
These metrics can also be found on Zenodo, DOI: 10.5281/zenodo.21974459 <br>
Note: This repository only includes examples of how the key metrics were generated. A more complete repository is available upon request.

