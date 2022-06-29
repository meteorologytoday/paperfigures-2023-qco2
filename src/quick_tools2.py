def getSimcases(casenames):

    
    all_simcases = {

        "SOM" : {
            "model" : "SOM",
            "CTL"  : "paper2021_SOM_CTL_coupled/0171-0200",
            "qco2" : "qco2_SOM/0371-0400",
        },

        "MLM" : {
            "model" : "MLM",
            "CTL"  : "paper2021_MLM_CTL_coupled/0171-0200",
            "qco2" : "qco2_MLM/0471-0500",
        },

        "EMOM" : {
            "model" : "EMOM",
            "CTL"  : "paper2021_EMOM_CTL_coupled/0171-0200",
            "qco2" : "qco2_EMOM/0471-0500",
        },

        "POP2" : {
            "model" : "POP2",
            "CTL"  : "paper2021_CTL_POP2/0171-0200",
            "qco2" : "qco2_POP2/0671-0700",
        },

    }

    r = {}
    for casename in casenames:
        r[casename] = all_simcases[casename]


    return r
