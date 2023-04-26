import matplotlib as mplt
from matplotlib import cm

import prettyLatLon
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



moc_ctl_t_rng = slice(171-1, 200-1)
moc_exp_t_rng = slice(671-1, 700-1)

moc_ctl_t_rng = slice(1-1, 200-1)
moc_exp_t_rng = slice(601-1, 700-1)



data = {}

scenarios = ["CTL", "qco2"]

print("Loading streamfunction...")
# loading streamfunction
moc_lat = None
moc_z   = None
moc_data = {}
for scenario in scenarios:

    print(scenario)
    moc_data[scenario] = {}

    filename = "data/AMOC/%s/MOC_am.nc" % (scenario,)
    
    with Dataset(filename, "r") as f:
        moc_data[scenario]["MOC"] = f.variables["MOC"][:, :, 0, :, :]

        if moc_lat is None:
            moc_lat = f.variables["lat_aux_grid"][:]
            moc_z   = f.variables["moc_z"][:] / 100


print("Taking averages...")
MOC_CTL = np.mean(moc_data["CTL"]["MOC"][moc_ctl_t_rng, :, :, :], axis=0)
MOC_qco2 = np.mean(moc_data["qco2"]["MOC"][moc_exp_t_rng, :, :, :], axis=0)

# Take Atlantic ocean portion out
MOC_DIFF = MOC_qco2 - MOC_CTL
#MOC_CTL = MOC_CTL[1, :, :] #- MOC_CTL[1, :, :]
#MOC_qco2 = MOC_qco2[1, :, :] #- MOC_qco2[1, :, :]


print("Plotting...")

fig, ax = plt.subplots(1,1, figsize=(6, 4), constrained_layout=True)
    
    
cmap_psi = cm.get_cmap("bwr")
clevs_psi = np.linspace(-5, 5, 21)
clevticks_psi = np.linspace(-5, 5, 11)
mappable = ax.contourf(moc_lat, moc_z, MOC_DIFF[1, :, :], clevs_psi, cmap=cmap_psi, extend="both")
        
cb = fig.colorbar(mappable,  ax=ax, ticks=clevticks_psi, orientation="vertical")
cb.set_label("$ \\Delta \\psi $ [ $\\mathrm{Sv}$ ] ")

ax.plot([0, 0], [moc_z[0], moc_z[-1]], color="gray", linestyle="-")
#CS = ax.contour(moc_lat, moc_z, MOC_DIFF[1, :, :], np.linspace(-8,0,9), colors="k", linewidths=2)

CS = ax.contour(moc_lat, moc_z, MOC_CTL[1, :, :], np.arange(-10,50,5), colors="k", linewidths=1)
clabels = plt.clabel(CS, CS.levels, inline=True, fmt="%d", inline_spacing=0, manual=[(45, 1500), (42, 1930), (42, 2360), (42, 3040), (11, 3200)])

CS = ax.contour(moc_lat, moc_z, MOC_qco2[1, :, :], np.arange(-10,50,5), colors="limegreen", linewidths=1)
clabels = plt.clabel(CS, CS.levels, inline=True, fmt="%d", inline_spacing=0, manual=[(40, 1023), (20, 1220), (20, 1550, ), (20, 1950), (20, 2480)])


for l in clabels:
    l.set_rotation(0)
#[txt.set_bbox(dict(boxstyle='square,pad=0')) for txt in clabels]

ax.set_ylim([0, 4000])
ax.set_xlim([-30, 60])

#ax.set_xlabel("Latitude")
ax.set_ylabel("Depth [ m ]")
ax.set_xticks([-30, 0, 30, 60])
ax.set_xticklabels(prettyLatLon.getPrettyLat(ax.get_xticks()))
#ax.grid()
#ax.set_xticklabels(["60S", "30S", "EQ", "30N", "60N"])

ax.set_title("(g) AMOC streamfunction")
#ax.xaxis.tick_top()
ax.invert_yaxis()
#ax.text(0.1, 0.9, "(a)", va="top", ha="left", transform=ax[0].transAxes)
#ax.text(0.1, 0.9, "(b)", va="top", ha="left", transform=ax[1].transAxes)


fig.savefig("figures/AMOC_psi.png", dpi=600)
plt.show()
