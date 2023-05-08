# Description

This is the code to reproduce figures of the paper "The Effect of Air-sea Coupling over the Tropical Pacific on the Response in Rainfall to Abrupt Greenhouse Gas Forcing" submitted to Geophysical Research Letter.

# Prerequisite

1. Python >= 3.7
    - Matplotlib
    - Cartopy
    - Numpy
    - Scipy
    - netCDF4
2. Julia >= 1.8
    - Fomatting
    - NCDatasets
    - Statistics
3. ImageMagick >= 6.9.10


# Reproducing Figures

1. Clone this project.
2. Download the file `data.zip` from [https://doi.org/10.5281/zenodo.7677817](https://doi.org/10.5281/zenodo.7677817)
3. Unzip the folder `data` from `data.zip` into this git project root folder (i.e., the same folder containing this `README.md` file).
4. Run `00_runall.sh`.
5. The figures are generated in the folder `final_figures`.
