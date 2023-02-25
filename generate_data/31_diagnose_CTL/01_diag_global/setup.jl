using DataStructures

archive_root = "/seley/tienyiah/paper2021_simulation"
output_dir = "output"
domain_files = Dict(
    "ice" => "CESM_domains/domain.ocn.gx1v6.090206.nc",
    "ocn" => "CESM_domains/domain.ocn.gx1v6.090206.nc",
)


cases = OrderedDict(

    "paper2021_SOM_CTL_coupled" => Dict(
        "model" => "SOM",
        "yrng" => [1, 200],
    ),

    "paper2021_MLM_CTL_coupled" => Dict(
        "model" => "MLM",
        "yrng" => [1, 200],
    ),

    "paper2021_EMOM_CTL_coupled" => Dict(
        "model" => "EMOM",
        "yrng" => [1, 200],
    ),

    "paper2021_CTL_POP2" => Dict(
        "model" => "POP2",
        "yrng" => [1, 200],
    ),
)

casenames = keys(cases)
