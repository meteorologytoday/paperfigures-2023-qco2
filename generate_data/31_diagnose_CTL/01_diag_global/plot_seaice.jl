using Formatting
using NCDatasets
using Statistics
include(joinpath("..", "CESM-diagnostic", "src", "diagnose_scripts_julia", "lib", "CESMReader.jl"))

using .CESMReader

function m2a(ts)
    return mean(reshape(ts, 12, :), dims=(1,))[1, :]
end

include("setup.jl")

data_dir = "output"

data = Dict()
models = ["SOM", "MLM", "EMOM", "POP2"]
#models = ["SOM", ]
year_skip = 10
R = 6.371e6

Dataset(domain_files["ice"], "r") do ds

    global area = ds["area"][:]
    global mask = ds["mask"][:]
    global lat  = ds["yc"][:]

    area .*= 4π * (R^2) / sum(area)

    global _area = reshape(area, size(area)... , 1)
    global mask_NH_idx = (mask .== 1) .& (lat .>= 0)
    global mask_SH_idx = (mask .== 1) .& (lat .<  0)

end


for (casename, caseinfo) in cases
    

    d = Dict()

    fh = FileHandler(filename_format="$data_dir/$casename/ice/$casename.cice.{:04d}.nc", form=:YEAR_MONTH)

    yrng = caseinfo["yrng"]
    time_vec = [(y, 1) for y = yrng[1]:year_skip:yrng[2]]

    ICEVOL  = CESMReader._getData(fh, "hi", time_vec, (:, :) ) 
    
    ICEVOL = _area .* ICEVOL 
    ICEVOL[isnan.(ICEVOL)] .= 0

    ICEVOL_NH = zeros(Float64, size(ICEVOL, 3))
    ICEVOL_SH = zeros(Float64, size(ICEVOL, 3))
    
    for t=1:length(ICEVOL_NH)
        ICEVOL_NH[t] = sum(view(ICEVOL, :, :, t)[mask_NH_idx])
        ICEVOL_SH[t] = sum(view(ICEVOL, :, :, t)[mask_SH_idx])
    end

    ICEAREA = CESMReader._getData(fh, "aice", time_vec, (:, :) )
    ICEAREA = _area .* ICEAREA
    ICEAREA[isnan.(ICEAREA)] .= 0

    ICEAREA_NH = zeros(Float64, size(ICEAREA, 3))
    ICEAREA_SH = zeros(Float64, size(ICEAREA, 3))
    
    for t=1:length(ICEAREA_NH)
        ICEAREA_NH[t] = sum(view(ICEAREA, :, :, t)[mask_NH_idx])
        ICEAREA_SH[t] = sum(view(ICEAREA, :, :, t)[mask_SH_idx])
    end


    data[casename] = Dict(
        "ICEVOL"    => ICEVOL_NH + ICEVOL_SH,
        "ICEVOL_NH" => ICEVOL_NH,
        "ICEVOL_SH" => ICEVOL_SH,

        "ICEAREA"    => ICEAREA_NH + ICEAREA_SH,
        "ICEAREA_NH" => ICEAREA_NH,
        "ICEAREA_SH" => ICEAREA_SH,

    )

end


println("Loading PyPlot")
using PyPlot
plt = PyPlot
println("Done")

fig, ax = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=true)

for (casename, caseinfo) in cases
    
    d = data[casename]
    t = collect(1:length(d["ICEVOL_SH"])) * year_skip

    ax[1, 1].plot(t, d["ICEVOL_NH"] / 1e12, label=casename)
    ax[2, 1].plot(t, d["ICEVOL_SH"] / 1e12, label=casename)
 
    ax[1, 2].plot(t, d["ICEAREA_NH"] / 1e15, label=casename)
    ax[2, 2].plot(t, d["ICEAREA_SH"] / 1e15, label=casename)
    
end

ax[1, 1].legend()
ax[1, 1].set_title("NH sea ice volume")
ax[2, 1].set_title("SH sea ice volume")

ax[1, 2].set_title("NH sea ice area")
ax[2, 2].set_title("SH sea ice area")
    
ax[1, 1].set_ylabel("[\$ \\times 10^{12} \\mathrm{m}^3 \$]")
ax[2, 1].set_ylabel("[\$ \\times 10^{12} \\mathrm{m}^3 \$]")

ax[1, 2].set_ylabel("[\$ \\times 10^{15} \\mathrm{m}^2 \$]")
ax[2, 2].set_ylabel("[\$ \\times 10^{15} \\mathrm{m}^2 \$]")


for _ax in ax[:]
    _ax.set_xlabel("Time [ yr ]")
end



mkpath("figures")

plt.savefig("figures/seaice_vol_area.png", dpi=300)

plt.show()
