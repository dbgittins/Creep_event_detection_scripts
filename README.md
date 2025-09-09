# Creep_event_detection_scripts


**Tags**:  `aseismic slip` · `shallow slip bursts` · `geophysics` · `time series analysis`

This repository standardises creepmeter data and facilitates the maual identificaiton of shallow slip bursts. 

## Features

- Converts CSV to HDF5 files
- Manual identification of shallow asiesmic slip
- Includes plotting utilities for visualising model fits and confidence intervals

## Input Data

- **Raw creepmeter data in various formats (e.g., .csv, .txt)**: Creepmeter data with sime slip and temperature

## Usage

This project is primarily designed for use in **Jupyter notebooks**. The typical workflow is:

1. Load in creepmeter data 
2. Convert to HDF5
3. Manually identify aseismic slip burts
4. Quality check
5. Visualise fits and statistical summaries
