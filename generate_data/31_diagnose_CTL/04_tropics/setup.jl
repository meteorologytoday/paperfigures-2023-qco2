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
        "yrng" => [171, 200],
    ),

    "paper2021_MLM_CTL_coupled" => Dict(
        "model" => "MLM",
        "yrng" => [171, 200],
    ),

    "paper2021_EMOM_CTL_coupled" => Dict(
        "model" => "EMOM",
        "yrng" => [171, 200],
    ),

    "paper2021_POP2_CTL" => Dict(
        "model" => "POP2",
        "yrng" => [171, 200],
    ),
)

casenames = keys(cases)
