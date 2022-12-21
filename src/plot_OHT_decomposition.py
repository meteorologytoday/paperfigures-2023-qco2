import cartopy.crs as ccrs
import matplotlib as mplt
from matplotlib import cm
#from quick_tools import *
from quick_tools2 import *

import os

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

import matplotlib.pyplot as plt

import sys, argparse
from netCDF4 import Dataset
import numpy as np

import argparse, pprint

parser = argparse.ArgumentParser()
parser.add_argument('--region', type=str, help='an integer for the accumulator', required=True)
parser.add_argument('--thumbnail-skip', type=int, default=0)
args = parser.parse_args()
pprint.pprint(args)

region = args.region

def area_mean(data, area):
    data.mask = False
    idx = np.isfinite(data)
    aa = area[idx]
    return sum(data[idx] * aa) / sum(aa)
 
domain_file = "CESM_domains/domain.lnd.fv0.9x1.25_gx1v6.090309.nc"
zdomain_file = "CESM_domains/POP2_zdomain.nc"

sim_casenames = getSimcases(["EMOM", "POP2"])

with Dataset(domain_file, "r") as f:
    lat  = f.variables["yc"][:, 0]
    lon  = f.variables["xc"][0, :]
    
    dlat = lat[1:] - lat[:-1]
    lat_mid = (lat[1:] + lat[:-1] ) / 2

with Dataset(zdomain_file, "r") as f:
    z_w  = f.variables["z_w"][:]

R_e = 6.371e6
dlon = lon[1] - lon[0]
cp = 3996.0
Omega = 7.292e-5
epsilon = 1.41e-5
f_co = 2 * Omega * np.sin(lat * np.pi / 180)
cos_lat = np.cos(lat * np.pi / 180)
dz  = z_w[1:] - z_w[:-1]
z_t = (z_w[1:] + z_w[:-1]) / 2

z_idx_EK = np.arange(0, 5)
z_idx_RF = np.arange(5,33)


lon_idx = {
    "IND": np.logical_and(lon >  50, lon <  95),
    "PAC": np.logical_and(lon > 150, lon < 270),
    "ATL": np.logical_and(lon > 320, lon < 350),
    "ALL": lon > -1,
}[region]

region_name = {
    "IND": "Indian Ocean",
    "PAC": "Pacific Ocean",
    "ATL": "Atlantic Ocean",
    "ALL": "Global",
}[region]

thumbnails = {
    "PAC": ["a", "b"],
    "ATL": ["c", "d"],
    "IND": ["e", "f"],
}[region]


data = {}

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
            for varname in ["TAUX", "TAUY"]:
                # Remember TAU needs a negative sign
                data[scenario][exp_name][varname] = - f.variables[varname][0, :, lon_idx].mean(axis=1)

        with Dataset(ocn_filename, "r") as f:
            print("Loading %s" % (ocn_filename,))
            
            for varname in ["TEMP"]:
                data[scenario][exp_name][varname] = f.variables[varname][0, :, :, lon_idx].mean(axis=2)
            

        data[scenario][exp_name]["TEMP_EK"] = np.average(data[scenario][exp_name]["TEMP"][z_idx_EK, :], weights=dz[z_idx_EK], axis=0)
        data[scenario][exp_name]["TEMP_RF"] = np.average(data[scenario][exp_name]["TEMP"][z_idx_RF, :], weights=dz[z_idx_RF], axis=0)
        data[scenario][exp_name]["STRT_TEMP"] = data[scenario][exp_name]["TEMP_EK"] - data[scenario][exp_name]["TEMP_RF"] 


################################

print("Ready to plot...")
 
def loadData(exp_name):

    loaded_data = {
        "CTL" : {},
        "qco2": {},
    }

    for scenario in loaded_data.keys():
        for varname in ["TAUX", "TAUY", "STRT_TEMP"]:
            loaded_data[scenario][varname] = data[scenario][exp_name][varname]


        dT = loaded_data[scenario]["STRT_TEMP"]
        TAUX = loaded_data[scenario]["TAUX"]
        TAUY = loaded_data[scenario]["TAUY"]

        loaded_data[scenario]["OHT_rot"] = - cp * dT * f_co    * TAUX / (epsilon**2.0 + f_co**2.0) * R_e * cos_lat * np.pi / 180
        loaded_data[scenario]["OHT_fct"] =   cp * dT * epsilon * TAUY / (epsilon**2.0 + f_co**2.0) * R_e * cos_lat * np.pi / 180

        loaded_data[scenario]["OHTCVG_rot"] = - (loaded_data[scenario]["OHT_rot"][1:] - loaded_data[scenario]["OHT_rot"][:-1]) / dlat
        loaded_data[scenario]["OHTCVG_fct"] = - (loaded_data[scenario]["OHT_fct"][1:] - loaded_data[scenario]["OHT_fct"][:-1]) / dlat
    return loaded_data

         
fig, ax = plt.subplots(2, 1, sharex=True, figsize=(6, 9), constrained_layout=True, squeeze=False)

ax = ax.flatten()

#fig.subplots_adjust(wspace=0.3)


    
for exp_name, caseinfo in sim_casenames.items():

    label = "%s" % caseinfo["model"]
    lc = caseinfo["lc"]

    
    d = loadData(exp_name)
    d_dif = {}
    
    for varname in ["TAUX", "TAUY", "STRT_TEMP", "OHT_rot", "OHT_fct", "OHTCVG_rot", "OHTCVG_fct"]:
        d_dif[varname] = d["qco2"][varname] - d["CTL"][varname]

    #ax[0].plot(lat, d_dif["TAUX"], color=lc, label=label)
    #ax[1].plot(lat, d_dif["TAUY"], color=lc, label=label)
    ax[0].plot(lat, d_dif["OHT_rot"] / 1e12, color=lc, label="%s (Ekman)" % label, ls="solid")
    ax[0].plot(lat, d_dif["OHT_fct"] / 1e12, color=lc, label="%s (friction)" % label, ls="dashed")
 
    ax[1].plot(lat_mid, d_dif["OHTCVG_rot"] / 1e12, color=lc, label="%s (Ekman)" % label, ls="solid")
    ax[1].plot(lat_mid, d_dif["OHTCVG_fct"] / 1e12, color=lc, label="%s (friction)" % label, ls="dashed")


for _ax in ax:

    _ax.legend(ncol=2, loc='upper center', framealpha=1, fontsize=10, columnspacing=1, handletextpad=0.3, handlelength=2)
    _ax.grid(True)
    _ax.plot([-90, 90], [0, 0], linestyle="dashed", color="black", linewidth=1)
    _ax.set_xticks([-10, 0, 10])
 
ax[-1].set_xticklabels(["10S", "EQ", "10N"])
ax[-1].set_xlim([-15, 15])

ax[0].set_ylim([-4.0, 5.0])
ax[1].set_ylim([-1.2, 2.5])

ax[0].set_ylabel("Density of OHT\n[$ \\times 10^{12} \\mathrm{W} \\, / \\, \\mathrm{deg} $]")
ax[1].set_ylabel("Density of OHTC\n[$ \\times 10^{12} \\mathrm{W} \\, / \\, \\mathrm{deg}^2 $]")

ax[0].set_title("(%s) %s-OHT" % ("abcdefghijklmn"[args.thumbnail_skip], args.region))
ax[1].set_title("(%s) %s-OHTC" % ("abcdefghijklmn"[args.thumbnail_skip+1], args.region))

#ax[0].legend(loc='auto', framealpha=1, fontsize=10, columnspacing=1.0, handletextpad=0.3, handlelength=1)
#ax[0].legend()

#fig.suptitle(region)

fig.savefig("figures/OHT_decomp_%s.png" % (region,), dpi=600)
plt.show()
#plt.close(fig)

