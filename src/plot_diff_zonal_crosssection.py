from quick_tools2 import *
import os
import sys, argparse
from netCDF4 import Dataset
import numpy as np
from pprint import pprint


import matplotlib as mplt
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import rc

default_linewidth = 2.0;
default_ticksize = 10.0;

mplt.rcParams['lines.linewidth'] =   default_linewidth;
mplt.rcParams['axes.linewidth'] =    default_linewidth;
mplt.rcParams['xtick.major.size'] =  default_ticksize;
mplt.rcParams['xtick.major.width'] = default_linewidth;
mplt.rcParams['ytick.major.size'] =  default_ticksize;
mplt.rcParams['ytick.major.width'] = default_linewidth;

#rc('font', **{'family':'sans-serif', 'serif': 'Bitstream Vera Serif', 'sans-serif': 'MS Reference Sans Serif', 'size': 20.0});
rc('font', **{'size': 15.0});
rc('axes', **{'labelsize': 15.0});
rc('mathtext', **{'fontset':'stixsans'});
#rc(('xtick.major','ytick.major'), pad=20)

#import matplotlib.font_manager as fm;
#print("%s: %d"%(fm.FontProperties().get_name(),fm.FontProperties().get_weight()));
import argparse, pprint

parser = argparse.ArgumentParser()
#parser.add_argument('--region', type=str, help='PAC, IND or ATL')
parser.add_argument('--thumbnail-skip', type=int, default=0)
parser.add_argument('--left-edge-lon', type=float, default=30.0)
args = parser.parse_args()
pprint.pprint(args)

#region = args.region

domain_file = "CESM_domains/domain.lnd.fv0.9x1.25_gx1v6.090309.nc"
ocn_zdomain_file = "CESM_domains/POP2_zdomain.nc"
atm_zdomain_file = "CESM_domains/cam4_lev.nc"

lon_rng = np.array([0, 360]) + args.left_edge_lon
z_rng   = np.array([200, 0])
Re = 6.371e6





with Dataset(domain_file, "r") as f:
    lat  = f.variables["yc"][:, 0]
    lon  = f.variables["xc"][0, :]

    lon_beg_idx = np.argmin(np.abs(lon - args.left_edge_lon))
    

with Dataset(ocn_zdomain_file, "r") as f:
    z_w = f.variables["z_w"][:] / 100.0
    z_t = f.variables["z_t"][:] / 100.0

with Dataset(atm_zdomain_file, "r") as f:
    lev  = f.variables["lev"][:]


# Get the equator
lat_idx = np.abs(lat - 0) < 5.0

"""
lon_idx = {
    "IND": np.logical_and(lon >  50, lon <  95),
    "PAC": np.logical_and(lon > 150, lon < 270),
    "ATL": np.logical_and(lon > 320, lon < 350),
    "ALL": lon > -1,
}[region]
"""

def rotate(arr, axis):
    return np.roll(arr, - lon_beg_idx, axis=axis)

lon_rotate = rotate(lon, axis=0)
lon_rotate[- lon_beg_idx:] += 360.0


data = {}

plot_cases = ["POP2", "EMOM", "MLM", "SOM"]
plot_cases = ["SOM", "MLM", "EMOM", "POP2"]
sim_casenames = getSimcases(plot_cases)

for scenario in ["CTL", "qco2"]:

    data[scenario] = {}

    for exp_name, caseinfo in sim_casenames.items():
            
        dir_name = caseinfo[scenario]
        data[scenario][exp_name] = {}
        
        print(dir_name, "!!!") 
        atm_filename = "data/tropics/%s/%s/atm.am.nc" % (scenario, dir_name)
        ocn_filename = "data/tropics/%s/%s/ocn_regrid.am.nc" % (scenario, dir_name)

        with Dataset(atm_filename, "r") as f:
            print("Loading %s" % (atm_filename,))
            for varname in ["OMEGA", "DTCOND", "U", "V", "T", "MSE"]:
                data[scenario][exp_name][varname] = f.variables[varname][0, :, lat_idx, :].mean(axis=1)

                
                data[scenario][exp_name][varname] = rotate(data[scenario][exp_name][varname], axis=1)

        with Dataset(ocn_filename, "r") as f:
            print("Loading %s" % (ocn_filename,))
            

            for varname in ["WVEL", "VVEL", "UVEL", "TEMP"]:
                if varname == "VVEL" and caseinfo["model"] != "POP2":
                    data[scenario][exp_name][varname] = f.variables["VVEL_T"][0, :, lat_idx, :].mean(axis=1)
                else:
                    data[scenario][exp_name][varname] = f.variables[varname][0, :, lat_idx, :].mean(axis=1)
                
                if varname == "WVEL" and caseinfo["model"] != "POP2":
                    WVEL = f.variables["WVEL"][0, :, lat_idx, :].mean(axis=1)
                    data[scenario][exp_name]["WVEL"] = (WVEL[1:, :] + WVEL[:-1, :]) / 2

                # cm to meter
                if varname in ["VVEL", "UVEL", "WVEL"] and caseinfo["model"] == "POP2":
                    data[scenario][exp_name][varname] /= 100.0
                
                data[scenario][exp_name][varname] = rotate(data[scenario][exp_name][varname], axis=1)

            # Load HMXL
            if "HMXL" in f.variables:
                if caseinfo["model"] != "POP2":
                    data[scenario][exp_name]["HMXL"] = f.variables["HMXL"][0, 0, lat_idx, :].mean(axis=0)
                else:
                    data[scenario][exp_name]["HMXL"] = f.variables["HMXL"][0, lat_idx, :].mean(axis=0) / 100
                
                data[scenario][exp_name]["HMXL"] = rotate(data[scenario][exp_name]["HMXL"], axis=0)

            else:
                print("File %s does not contain HMXL. Skip it." % (ocn_filename,))
     


factors = {
    "T"     : 1,
    "TEMP"  : 1,
    "OMEGA" : -1e2,
    "WVEL"  : 86400.0 * 365,
    "VVEL"  : 86400.0 * 365,
    "UVEL"  : 86400.0 * 365,
    "V"     : 1,
    "U"     : 1,
    "DTCOND"  : 86400.0,
    "MSE" : 1e-3,
}

cntr_levs = {
    "OMEGA" : np.linspace(-5,   5, 11),
    "T"     : np.linspace(0, 10, 21),
    "TEMP"  : np.linspace(2, 4, 21),
    "WVEL"  : np.linspace(-100, 100, 11),
    "DTCOND": np.linspace(-1, 1, 21),
    "MSE"   : np.linspace(8, 18, 21),
} 
 
cb_ticks = {
    "T"     : np.linspace(0, 10, 6),
    "TEMP"  : np.linspace(2, 4, 3),
    "MSE"  : np.linspace(8, 18, 6),
} 
    
fig, ax = plt.subplots(
    2 * len(plot_cases) // 1,
    1,
    sharey=False,
    sharex=False,
    figsize=(10, 3 * (2*len(plot_cases) / 1)),
    constrained_layout=True,
    squeeze=False,
)

thumbnail = "abcdefghijklmn"

def getDIFF(exp_name, varname):
    return data["qco2"][exp_name][varname] - data["CTL"][exp_name][varname]

ax_idx = 0  
ax_flat = ax.transpose().flatten()
#print("Region: ", region)

for exp_name, caseinfo in sim_casenames.items():

    print("Doing: ", exp_name)

    #ax_atm = ax[2 * (ax_idx//2)    , ax_idx%2]
    #ax_ocn = ax[2 * (ax_idx//2) + 1, ax_idx%2]
 
    ax_atm = ax[2 * (ax_idx//1)    , 0]
    ax_ocn = ax[2 * (ax_idx//1) + 1, 0]

    label = "%s" % exp_name

    d = {}
    for varname in ["WVEL", "TEMP", "OMEGA", "U", "V", "T", "DTCOND", "VVEL", "MSE", "UVEL"]:
        d[varname] = getDIFF(exp_name, varname) * factors[varname]
   

    mappable_diff_atm = ax_atm.contourf(lon_rotate, lev, d["MSE"], cntr_levs["MSE"], cmap="afmhot_r", extend="both")
    CS = ax_atm.contour(lon_rotate, lev, d["OMEGA"], cntr_levs["OMEGA"], colors="k", linewidths=1)
    clabels = plt.clabel(CS, CS.levels, inline=True, fmt="%.1f", inline_spacing=0)

    # Vectors
    lon_skips = 10
    quiver_ratio = 1#np.abs(1000 - 100) / ( np.abs(lon_rng[1] - lon_rng[0]) * ( np.pi/180.0 * Re))
    ax_atm.quiver(lon_rotate[::lon_skips], lev, d["U"][:, ::lon_skips] * (180 / np.pi / Re) / 50, d["OMEGA"][:, ::lon_skips] / .5e7  , scale=1/86400.0)

    ax_atm.set_title("(%s) %s" % ("abcdefghijklmn"[ax_idx+args.thumbnail_skip], label))

    ocn_z_t = z_t[0:d["TEMP"].shape[0]]
    mappable_diff_ocn = ax_ocn.contourf(lon_rotate, ocn_z_t, d["TEMP"], cntr_levs["TEMP"], cmap="OrRd", extend="both")

    CS = ax_ocn.contour(lon_rotate, ocn_z_t, d["WVEL"], cntr_levs["WVEL"], colors="k", linewidths=1)
    
    
    HMXL = data["qco2"][exp_name]["HMXL"]
    ax_ocn.plot(lon_rotate, HMXL, color="white", linewidth=2)


    quiver_ratio = np.abs(z_rng[1] - z_rng[0]) / (np.abs(lon_rng[1] - lon_rng[0]) * (2*np.pi*Re/360.0) )

    if caseinfo["model"] == "POP2":
        HMXL_before = data["qco2"]["EMOM"]["HMXL"]
        ax_ocn.plot(lon_rotate, HMXL_before, color="white", ls="dashed", linewidth=1)
   
    lon_skips = 10 
    ax_ocn.quiver(lon_rotate[::lon_skips], ocn_z_t, d["UVEL"][:, ::lon_skips] * (180 / np.pi / Re) / 200, d["WVEL"][:, ::lon_skips] / 1e2 , scale=10)

    ax_atm.set_ylim([1000, 100])

    ax_ocn.set_ylim(z_rng)

  
    ax_ocn.set_xticks(np.linspace(0, 360, 7) + args.left_edge_lon)
    #ax_ocn.set_xticklabels(["10S", "EQ", "10N",])

    ax_atm.set_ylabel("Pressure [hPa]")
    ax_ocn.set_ylabel("Depth [m]")

    for _ax in [ax_atm, ax_ocn]:
        _ax.grid(True)
        _ax.set_xlim(lon_rng)
 
    plt.colorbar(mappable_diff_atm, ax=ax_atm, orientation="vertical", label="MSE [kJ]", ticks=cb_ticks["MSE"])
    plt.colorbar(mappable_diff_ocn, ax=ax_ocn, orientation="vertical", label="Ocean Temp [K]", ticks=cb_ticks["TEMP"])


    ax_idx += 1


fig.savefig("figures/diff_zonal_crosssection.png", dpi=100)

plt.show()
plt.close(fig)

