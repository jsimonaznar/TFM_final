import spiceypy as spice
import numpy as np


def groundtrack(obs, t, target):
    """
    This function returns the spacecraft ground track across the target surface, at time t

    :param obs: string SPICE name of the observer body
    :param t: time epoch in TDB seconds past J2000 epoch. It can be either a single
              point in time or a discretized vector of different time values
    :param target: string SPICE name of the target body
    :return: gtlon: longitude coordinate of the observer ground track, in [deg]
             gtlat: latitude coordinate of the observer ground track, in [deg]
    """

    method = 'INTERCEPT/ELLIPSOID'  # Target modeling
    abcorr = 'NONE'  # Aberration correction
    tframe = spice.cnmfrm(target)[1]  # Body-fixed frame

    # Get ground track
    if np.size(t) >1:
        sctrack = np.zeros((t.shape[0],3))
        gtlon = np.zeros(t.shape[0])
        gtlat = np.zeros(t.shape[0])
        for i in range(len(t)):
            sctrack[i] = spice.subpnt(method, target, t[i], tframe, abcorr, obs)[0]  # Sub-spacecraft point
            _, gtlon[i], gtlat[i] = spice.reclat(sctrack[i])  # Convert to latitudinal coordinates
    else:
        sctrack = spice.subpnt(method, target, t, tframe, abcorr, obs)[0]
        _, gtlon, gtlat = spice.reclat(sctrack)
    #sctrack = spice.subpnt(method, target, t, tframe, abcorr, obs)[0]  # Sub-spacecraft point
    #_, gtlon, gtlat = spice.reclat(sctrack)  # Convert to latitudinal coordinates
    
    gtlon = spice.dpr() * gtlon  # Convert from radians to degrees
    gtlat = spice.dpr() * gtlat  # Convert from radians to degrees

    return [gtlon, gtlat]
