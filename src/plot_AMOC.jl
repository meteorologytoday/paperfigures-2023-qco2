using Formatting
using NCDatasets
using Statistics


Dataset("data/AMOC/qco2/processed-MOC_am.nc", "r") do ds
    global AMOC_qco2 = ds["AMOC_max"][:]
end

Dataset("data/AMOC/CTL/processed-MOC_am.nc", "r") do ds
    global AMOC_CTL = ds["AMOC_max"][:]
end

Dataset("data/AMOC/CTL/MOC_am.nc", "r") do ds
    local lat = ds["lat_aux_grid"][:]
    local lat_eq_idx = argmin(abs.(lat.-0.0))
    global ATLOHT_eq_CTL = ds["N_HEAT"][lat_eq_idx, 2, 2, :]
end

Dataset("data/AMOC/qco2/MOC_am.nc", "r") do ds
    local lat = ds["lat_aux_grid"][:]
    local lat_eq_idx = argmin(abs.(lat.-0.0))
    global ATLOHT_eq_qco2 = ds["N_HEAT"][lat_eq_idx, 2, 2, :]
end


println("Loading PyPlot")
using PyPlot
plt = PyPlot
println("Done")

fig, ax = plt.subplots(2, 1, figsize=(6, 4), constrained_layout=true)

ax[1].plot(collect(1:length(AMOC_CTL)),  AMOC_CTL,  color="blue", label="PI")
ax[1].plot(collect(1:length(AMOC_qco2)), AMOC_qco2, color="red",  label="QCO2")

ax[2].plot(collect(1:length(ATLOHT_eq_CTL)), ATLOHT_eq_CTL,   color="blue", label="PI")
ax[2].plot(collect(1:length(ATLOHT_eq_qco2)), ATLOHT_eq_qco2,  color="red", label="QCO2")


ax[1].set_title("(e) AMOC strength")
ax[2].set_title("(f) Cross Equatorial OHT in ATL")

ax[1].set_ylabel("[ Sv ]")
ax[2].set_ylabel("[ PW ]")
    
for _ax in ax

    _ax.set_xlabel("Time [ yr ]")
    _ax.grid("on")
    _ax.legend()

end

plt.savefig("figures/AMOC_POP2.png", dpi=300)

plt.show()
