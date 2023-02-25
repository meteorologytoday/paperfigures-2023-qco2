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
parser.add_argument('--region', type=str, help='PAC, IND or ATL')
parser.add_argument('--thumbnail-skip', type=int, default=0)
args = parser.parse_args()
pprint.pprint(args)

region = args.region

domain_file = "CESM_domains/domain.lnd.fv0.9x1.25_gx1v6.090309.nc"
ocn_zdomain_file = "CESM_domains/POP2_zdomain.nc"
atm_zdomain_file = "CESM_domains/cam4_lev.nc"

lat_rng = np.array([-15, 15])
z_rng   = np.array([200, 0])
Re = 6.371e6

with Dataset(domain_file, "r") as f:
    lat  = f.variables["yc"][:, 0]
    lon  = f.variables["xc"][0, :]

with Dataset(ocn_zdomain_file, "r") as f:
    z_w = f.variables["z_w"][:] / 100.0
    z_t = f.variables["z_t"][:] / 100.0

with Dataset(atm_zdomain_file, "r") as f:
    lev  = f.variables["lev"][:]


lon_idx = {
    "IND": np.logical_and(lon >  50, lon <  95),
    "PAC": np.logical_and(lon > 150, lon < 270),
    "ATL": np.logical_and(lon > 320, lon < 350),
    "ALL": lon > -1,
}[region]

data = {}

plot_cases = ["POP2", "EMOM", "MLM", "SOM"]
#plot_cases = ["POP2", "EMOM",]
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
            for varname in ["OMEGA", "DTCOND", "V", "T"]:
                data[scenario][exp_name][varname] = f.variables[varname][0, :, :, lon_idx].mean(axis=2)

        with Dataset(ocn_filename, "r") as f:
            print("Loading %s" % (ocn_filename,))
            

            for varname in ["WVEL", "VVEL", "TEMP"]:
                if varname == "VVEL" and caseinfo["model"] != "POP2":
                    data[scenario][exp_name][varname] = f.variables["VVEL_T"][0, :, :, lon_idx].mean(axis=2)
                else:
                    data[scenario][exp_name][varname] = f.variables[varname][0, :, :, lon_idx].mean(axis=2)
                
                if varname == "WVEL" and caseinfo["model"] != "POP2":
                    WVEL = f.variables["WVEL"][0, :, :, lon_idx].mean(axis=2)
                    data[scenario][exp_name]["WVEL"] = (WVEL[1:, :] + WVEL[:-1, :]) / 2

                # cm to meter
                if varname in ["VVEL", "UVEL", "WVEL"] and caseinfo["model"] == "POP2":
                    data[scenario][exp_name][varname] /= 100.0

            # Load HMXL
            if "HMXL" in f.variables:
                if caseinfo["model"] != "POP2":
                    data[scenario][exp_name]["HMXL"] = f.variables["HMXL"][0, 0, :, lon_idx].mean(axis=1)
                else:
                    data[scenario][exp_name]["HMXL"] = f.variables["HMXL"][0, :, lon_idx].mean(axis=1) / 100

            else:
                print("File %s does not contain HMXL. Skip it." % (ocn_filename,))
     


factors = {
    "T"     : 1,
    "TEMP"  : 1,
    "OMEGA" : -1e2,
    "WVEL"  : 86400.0 * 365,
    "VVEL"  : 86400.0 * 365,
    "V"     : 1,
    "DTCOND"  : 86400.0,
}

cntr_levs = {
    "OMEGA" : np.linspace(-5,   5, 21),
    "T"     : np.linspace(0, 10, 21),
    "TEMP"  : np.linspace(0, 5, 11),
    "WVEL"  : np.linspace(-100, 100, 21),
    "DTCOND": np.linspace(-1, 1, 21),
} 
 
cb_ticks = {
    "T"     : np.linspace(0, 10, 6),
    "TEMP"  : np.linspace(0, 5, 6),
} 
    
fig, ax = plt.subplots(2 * len(plot_cases)//2, 2, sharey=False, sharex=False, figsize=(6 * 2, 3 * (2*len(plot_cases) / 2)), constrained_layout=True, squeeze=False)

thumbnail = "abcdefghijklmn"

def getDIFF(exp_name, varname):
    return data["qco2"][exp_name][varname] - data["CTL"][exp_name][varname]

ax_idx = 0  
ax_flat = ax.transpose().flatten()
print("Region: ", region)

for exp_name, caseinfo in sim_casenames.items():

    print("Doing: ", exp_name)

    ax_atm = ax[2 * (ax_idx//2)    , ax_idx%2]
    ax_ocn = ax[2 * (ax_idx//2) + 1, ax_idx%2]
    
    label = "%s" % exp_name

    d = {}
    for varname in ["WVEL", "TEMP", "OMEGA", "V", "T", "DTCOND", "VVEL"]:
        d[varname] = getDIFF(exp_name, varname) * factors[varname]
   

    #mappable_diff_atm = ax_atm.contourf(lat, lev, d["T"], cntr_levs["T"], cmap="rainbow", extend="both")
    #mappable_diff_atm = ax_atm.contourf(lat, lev, d["OMEGA"], cntr_levs["OMEGA"], cmap="bwr", extend="both")
    #mappable_diff_atm = ax_atm.contourf(lat, lev, d["DTCOND"], cntr_levs["DTCOND"], cmap="hot_r", extend="both")
    CS = ax_atm.contour(lat, lev, d["OMEGA"], cntr_levs["OMEGA"], colors="k", linewidths=1)
    #CS = ax_atm.contour(lat, lev, d["T"], cntr_levs["T"], colors="k", linewidths=1)
    clabels = plt.clabel(CS, CS.levels, inline=True, fmt="%.1f", inline_spacing=0)

    ax_atm.set_title("(%s) %s-%s" % ("abcdefghijklmn"[ax_idx+args.thumbnail_skip], args.region, label))

    ocn_z_t = z_t[0:d["TEMP"].shape[0]]
    #print(d["TEMP"].shape)
    #print(ocn_z_t.shape)
    mappable_diff_ocn = ax_ocn.contourf(lat, ocn_z_t, d["TEMP"], cntr_levs["TEMP"], cmap="OrRd", extend="both")
    CS = ax_ocn.contour(lat, ocn_z_t, d["WVEL"], cntr_levs["WVEL"], colors="k", linewidths=1)
    #mappable_diff_ocn = ax_ocn.contourf(lat, ocn_z_t, d["WVEL"], cntr_levs["WVEL"], cmap="bwr", extend="both")
    #CS = ax_ocn.contour(lat, ocn_z_t, d["TEMP"], cntr_levs["TEMP"], colors="k", linewidths=1)
    #clabels = plt.clabel(CS, CS.levels, inline=True, fmt="%.1f", inline_spacing=0)
    
    
    HMXL = data["qco2"][exp_name]["HMXL"]
    ax_ocn.plot(lat, HMXL, color="white", linewidth=2)


    quiver_ratio = np.abs(z_rng[1] - z_rng[0]) / (np.abs(lat_rng[1] - lat_rng[0]) * (2*np.pi*Re/360.0) )
    #ax_ocn.quiver(lat, ocn_z_t, d["VVEL"], d["WVEL"] / quiver_ratio, scale=0.5e7)
    #ax_ocn.streamplot(lat, ocn_z_t, d["VVEL"], d["WVEL"] / quiver_ratio)


    if caseinfo["model"] == "POP2":
        HMXL_before = data["qco2"]["EMOM"]["HMXL"]
        ax_ocn.plot(lat, HMXL_before, color="white", ls="dashed", linewidth=1)

    ax_atm.set_ylim([1000, 100])

    ax_ocn.set_ylim(z_rng)

  
    ax_ocn.set_xticks([-10, 0, 10])
    ax_ocn.set_xticklabels(["10S", "EQ", "10N",])

    ax_atm.set_ylabel("Pressure [hPa]")
    ax_ocn.set_ylabel("Depth [m]")

    for _ax in [ax_atm, ax_ocn]:
        _ax.grid(True)
        _ax.set_xlim(lat_rng)
 
    plt.colorbar(mappable_diff_ocn, ax=ax_ocn, orientation="vertical", label="Ocean Temp [K]", ticks=cb_ticks["TEMP"])


    ax_idx += 1


fig.savefig("figures/diff_zmean_vertical_%s.png" % (region,), dpi=200)

plt.show()
plt.close(fig)

