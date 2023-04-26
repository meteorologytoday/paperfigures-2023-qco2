import numpy as np

def getPrettyLat(lat, fmt="%d"):

    if lat == 0:

        return "EQ"

    else:

        if lat < 0:
            NS_str = "S"
            lat = - lat

        elif lat > 0:
            NS_str = "N"

        return "$ %s^\\circ\\mathrm{%s} $ " % (
            fmt % (lat,),
            NS_str
        )





def getPrettyLon(lon, fmt="%d"):

    lon = lon % 360

    if lon < 180:
        EW_str = "E"

    else:
        EW_str = "W"
        lon = 360 - lon


    return "$ %s^\\circ\\mathrm{%s} $ " % (
        fmt % (lon,),
        EW_str
    )


getPrettyLat = np.vectorize(getPrettyLat)
getPrettyLon = np.vectorize(getPrettyLon)


