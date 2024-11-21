import spiceypy as spice
import numpy as np

from PSOA.trgobsvec import trgobsvec


def radarcover(radii, srfpoint, t, target, obs):
    """
    Calculates the coverage of a sub-surface radar from a specific surface point (nadir, this surface point must be computed as groundtrack) on a target body as observed from the
        instrument at a given time.

    :param srfpoint: target surface point.
                     It can be input either in latitudinal coordinates (in [deg]) or Cartesian coordinates (in [km])
    :param t: time epoch in TDB seconds past J2000 epoch.
              It can be either a single point in time or a discretized vector of different time values
    :param target: string SPICE name of the target body
    :param obs: string SPICE name of the observer body
    :return: area of the surface covered
    """

    # Convert latitudinal coordinates to rectangular if needed
    if len(srfpoint) == 2:
        srfpoint = np.radians(srfpoint)  # [deg] to [rad]
        srfpoint = spice.srfrec(spice.bodn2c(target), srfpoint[0], srfpoint[1])

    # Compute distance between surface point and the observer
    obsvec, dist = trgobsvec(srfpoint, t, target, obs)

    altrack = 0.8 * dist

    theta = np.arcsin(radii / (radii + dist))
    actrack = radii * (np.pi - 2 * theta)

    return(altrack * actrack)