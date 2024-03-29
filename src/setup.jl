using DataStructures

archive_root = "/glade/scratch/tienyiao/archive"
output_dir = "output"
domain_files = Dict(
    "ice" => "CESM_domains/domain.ocn.gx1v6.090206.nc",
    "ocn" => "CESM_domains/domain.ocn.gx1v6.090206.nc",
)


cases = OrderedDict(

    "qco2_SOM" => Dict(
        "model" => "SOM",
        "yrng" => [201, 400],
        "label" => "4xCO2_SOM",
    ),

    "qco2_MLM" => Dict(
        "model" => "MLM",
        "yrng" => [201, 500],
        "label" => "4xCO2_MLM",
    ),

    "qco2_EMOM" => Dict(
        "model" => "EMOM",
        "yrng" => [201, 500],
        "label" => "4xCO2_EMOM",
    ),

    "qco2_POP2" => Dict(
        "model" => "POP2",
        "yrng" => [  1, 700],
        "label" => "4xCO2_POP2",
    ),
)
casenames = keys(cases)
