#!/bin/bash
#PBS -P if69
#PBS -q normalbw
#PBS -l walltime=23:59:00
#PBS -l ncpus=2
#PBS -l mem=9GB
#PBS -l jobfs=20GB
#PBS -l storage=gdata/hh5+gdata/k10+gdata/rt52+scratch/k10

module load cdo/2.0.5

# change this to the ERA5 variable you want to use
VAR=slhf

FILES=/g/data/rt52/era5/single-levels/reanalysis/$VAR/
MIDDIR=/scratch/k10/cb4968/$VAR/
OUTDIR=/g/data/k10/cb4968/era5_daily_means/$VAR/

mkdir -p $MIDDIR
mkdir -p $OUTDIR

for year in {2008..2021}; #1979
do 
    for month in {01,02,03,04,05,06,07,08,09,10,11,12}; 
    do
        cdo -L -daymean -remapcon,r360x180 $FILES/$year/${VAR}_era5_oper_sfc_$year$month\01*.nc /scratch/k10/cb4968/$VAR/$year$month.nc
    done
    # concat months into years #  -setctomiss,-inf
    cdo -b f32 mergetime /scratch/k10/cb4968/${VAR}/$year*.nc $OUTDIR/era5_${VAR}_daily_mean_$year.nc
done

