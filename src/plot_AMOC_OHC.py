import matplotlib as mplt
from matplotlib import cm

import os

#mplt.use('Agg')

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
from pprint import pprint

def mavg(y, w):

    N = len(y)
    yy = np.zeros((N,))
    if w == 0:
        yy[:] = y

    else: 
    
        window = w * 2 + 1
        for i in range(N):
            if i < w:
                rng = slice(0, i+w+1)
                yy[i] = np.mean(y[rng])

            elif i > (N - w - 1):
                rng = slice(i-w, N)
                yy[i] = np.mean(y[rng])

            else:
                rng = slice(i-w,i+w+1)
                yy[i] = np.mean(y[rng])
        
    return yy


data_infos = {

    "pi" : {
        "scenario" : "CTL",
        "time-rng" : [171, 200],
        "label" : "pi",
        "color" : "black",
    },

    "qco2_201-230" : {
        "scenario" : "qco2",
        "time-rng" : [201, 230],
        "label" : "4xCO2 - 201-230",
        "color" : "violet",
    },


    "qco2_471-500" : {
        "scenario" : "qco2",
        "time-rng" : [471, 500],
        "label" : "4xCO2 - 471-500",
        "color" : "dodgerblue",
    },

    "qco2_571-600" : {
        "scenario" : "qco2",
        "time-rng" : [571, 600],
        "label" : "4xCO2 - 571-600",
        "color" : "orange",
    },

    "qco2_671-700" : {
        "scenario" : "qco2",
        "time-rng" : [671, 700],
        "label" : "4xCO2 - 671-700",
        "color" : "red",
    },

    "pi_all" : {
        "scenario" : "CTL",
        "time-rng" : [1, 200],
        "label" : "pi",
        "color" : "black",
    },

    "qco2_all" : {
        "scenario" : "qco2",
        "time-rng" : [1, 700],
        "label" : "4xCO2 - 671-700",
        "color" : "red",
    },


}

ref_casename = "pi"
MOC_casenames = ["pi", "qco2_671-700", ]
OHC_casenames = ["pi", "qco2_671-700", "qco2_571-600", "qco2_471-500", "qco2_201-230", ]

print("Loading streamfunction...")
# loading streamfunction
moc_lat = None
moc_z   = None
moc_data = {}
for casename in data_infos.keys():

    print("Casename : ", casename)
    
    data_info = data_infos[casename]

    moc_data[casename] = {}

    filename = "data/AMOC/%s/MOC_am.nc" % (data_info["scenario"],)
    
    with Dataset(filename, "r") as f:
        moc_data[casename]["MOC"] = f.variables["MOC"][:, :, 0, :, :]
        moc_data[casename]["N_HEAT"] = f.variables["N_HEAT"][:, :, :, :]

        if moc_lat is None:
            moc_lat = f.variables["lat_aux_grid"][:]
            moc_z   = f.variables["moc_z"][:] / 100
            moc_lat_eq_idx = np.argmin(np.abs(moc_lat - 0.0))
            print("The index of euqtor: ", moc_lat_eq_idx)


    print("Taking averages...")
    time_rng = data_info["time-rng"]
    moc_data[casename]["MOC_avg"]    = np.mean(moc_data[casename]["MOC"][slice(time_rng[0]-1, time_rng[1]-1), :, :, :], axis=0)
    moc_data[casename]["N_HEAT_avg"] = np.mean(moc_data[casename]["N_HEAT"][slice(time_rng[0]-1, time_rng[1]-1), :, :, :], axis=0)
    
    moc_data[casename]["N_HEAT_eq"] = moc_data[casename]["N_HEAT"][:, :, :, moc_lat_eq_idx]

print("Plotting...")

"""
fig, ax = plt.subplots(2, 1, figsize=(8, 4), constrained_layout=True)

cmap_psi = cm.get_cmap("bwr")
clevs_psi = np.linspace(-5, 5, 21)
clevticks_psi = np.linspace(-5, 5, 11)

ax[0].plot([0, 0], [moc_z[0], moc_z[-1]], color="gray", linestyle="-")
#ax[1].plot([0, 0], [moc_z[0], moc_z[-1]], color="gray", linestyle="-")

for i, casename in enumerate(data_infos.keys()):

    data_info = data_infos[casename]
    color = data_info["color"]

    if casename in MOC_casenames:
        
        MOC_ATL = moc_data[casename]["MOC_avg"][1, :, :]
        CS = ax[0].contour(moc_lat, moc_z, MOC_ATL, np.arange(-10,50,5), colors=color, linewidths=1, label=data_info["label"])
        clabels = plt.clabel(CS, CS.levels, inline=True, fmt="%d", inline_spacing=0)
        
        for l in clabels:
            l.set_rotation(0)

    if casename in OHC_casenames:
        OHC_ATL = moc_data[casename]["N_HEAT_avg"][1, 1, :]
        ref_OHC_ATL = moc_data[ref_casename]["N_HEAT_avg"][1, 1, :]
        ax[1].plot(moc_lat, OHC_ATL - ref_OHC_ATL, color=color, label=data_info["label"])


ax[0].set_ylim([0, 4000])
ax[0].set_ylabel("Depth [ m ]")

ax[1].set_ylabel("$\\Delta$OHC [ $ \\times 10^{15} \, \\mathrm{W} $ ]")

for _ax in ax:
    _ax.set_xlim([-30, 60])
    _ax.set_xticks([-30, 0, 30, 60])

#ax.set_xlabel("Latitude")


#ax.grid()
#ax.set_xticklabels(["60S", "30S", "EQ", "30N", "60N"])

ax[0].invert_yaxis()
ax[1].legend()

fig.savefig("figures/AMOC_comparison.png", dpi=600)
"""
print("Plotting timeseries...")

fig, ax = plt.subplots(1, 1, figsize=(6, 4), constrained_layout=True)

for i, casename in enumerate(["pi_all", "qco2_all"]):

    data_info = data_infos[casename]
    color = data_info["color"]

    OHC_eq_data = moc_data[casename]["N_HEAT_eq"][:, 1, 1]
    t = np.arange(OHC_eq_data.shape[0])
    ax.plot(t, OHC_eq_data, color=color)

fig.savefig("figures/AMOC_OHT_timeseries.png", dpi=600)
plt.show()
