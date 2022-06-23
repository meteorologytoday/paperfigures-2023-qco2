using Formatting
using NCDatasets
using Statistics


Dataset("data/AMOC/qco2/processed-MOC_am.nc", "r") do ds
    global AMOC_qco2 = ds["AMOC_max"][:]
end

Dataset("data/AMOC/CTL/processed-MOC_am.nc", "r") do ds
    global AMOC_CTL = ds["AMOC_max"][:]
end



println("Loading PyPlot")
using PyPlot
plt = PyPlot
println("Done")

fig, ax = plt.subplots(1, 1, figsize=(6, 4), constrained_layout=true)

ax.plot(collect(1:length(AMOC_CTL)),  AMOC_CTL,  color="blue", label="pi")
ax.plot(collect(1:length(AMOC_qco2)), AMOC_qco2, color="red",  label="4xCO2")

ax.set_title("AMOC in POP2")
ax.set_ylabel("[ Sv ]")
ax.set_xlabel("Time [ yr ]")
ax.grid("on")
ax.legend()

plt.savefig("figures/AMOC_POP2.png", dpi=300)

plt.show()
