import spiceypy as spice
import numpy as np

from PSOA.emissionang import emissionang
from PSOA.trgobsvec import trgobsvec


def pointres(ifov, srfpoint, t, target, obs):
    """
    Calculates the resolution of an instrument at a specific surface point on a target body as observed from an
        instrument at a given time.
    Note: It does not take into account visibility

    :param ifov: angular resolution of the instrument [rad/px]
    :param srfpoint: target surface point.
                     It can be input either in latitudinal coordinates (in [deg]) or Cartesian coordinates (in [km])
    :param t: time epoch in TDB seconds past J2000 epoch.
              It can be either a single point in time or a discretized vector of different time values
    :param target: string SPICE name of the target body
    :param obs: string SPICE name of the observer body
    :return: meanres: mean resolution at the specified surface point, in [km/px]
    """

    # Convert latitudinal coordinates to rectangular if needed
    if len(srfpoint) == 2:
        srfpoint = np.radians(srfpoint)  # [deg] to [rad]
        srfpoint = spice.srfrec(spice.bodn2c(target), srfpoint[0], srfpoint[1])

    # Compute distance between surface point and the observer
    obsvec, dist = trgobsvec(srfpoint, t, target, obs)

    # Compute emission angle between the surface point and the observer
    emnang = emissionang(srfpoint, t, target, obs)
    if np.size(t) >1:
        emnang[emnang >= 90] = np.nan
    else:
        if emnang >= 90:
            emnang = np.nan

    # Mean (boresight) resolution in [km/px]
    meanres = ifov * dist / np.sqrt(np.sin(np.radians(90 - emnang)))

    # Maximum resolution limit to avoid singularities
    maxres = ifov * np.max(dist) / np.sqrt(np.sin(np.radians(2)))
    if np.size(t) >1:
        meanres[meanres > maxres] = maxres  # Limit mean resolution to maxres
    else:
        if meanres > maxres:
            meanres = maxres

    return meanres
