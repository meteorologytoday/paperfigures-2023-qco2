using DataStructures

archive_root = "/grimsey/tienyiah/simulation_data/qco2/"
output_dir = "output"
domain_files = Dict(
    "ice" => "CESM_domains/domain.ocn.gx1v6.090206.nc",
    "ocn" => "CESM_domains/domain.ocn.gx1v6.090206.nc",
)


cases = OrderedDict(

    "qco2_SOM" => Dict(
        "model" => "SOM",
        "yrng" => [371, 400],
    ),

    "qco2_MLM" => Dict(
        "model" => "MLM",
        "yrng" => [471, 500],
    ),

    "qco2_EMOM" => Dict(
        "model" => "EMOM",
        "yrng" => [471, 500],
    ),

    "qco2_POP2" => Dict(
        "model" => "POP2",
        "yrng" => [671, 700],
    ),
)

casenames = keys(cases)
