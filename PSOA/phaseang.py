import spiceypy as spice
import numpy as np

from PSOA.trgillvec import trgillvec
from PSOA.trgobsvec import trgobsvec


def phaseang(srfpoint, t, target, obs):
    """
    This function returns the phase angle between the distance vector to the
    illumination source (the Sun) and the distance vector to the observer,
    from the target surface point P, at time ts

    :param srfpoint: target surface point. It can be input either in latitudinal
                     coordinates (in [deg]) or Cartesian coordinates (in [km])
    :param t: time epoch in TDB seconds past J2000 epoch. It can be either a single
              point in time or a discretized vector of different time values
    :param target: string SPICE name of the target body
    :param obs: string SPICE name of the observer body
    :return: angle: angle between the distance vector to the illumination source and the
                     distance vector to the observer, in [deg]
    """

    # Convert latitudinal coordinates to rectangular if needed
    if len(srfpoint) == 2:
        srfpoint = np.radians(srfpoint)  # [deg] to [rad]
        srfpoint = spice.srfrec(spice.bodn2c(target), srfpoint[0], srfpoint[1])
    else:
        srfpoint = np.array(srfpoint).reshape(-1, 1)

    # Compute the observer position vector as seen from the srfpoint
    obsvec, _ = trgobsvec(srfpoint, t, target, obs)

    # Compute the illumination source position vector as seen from the srfpoint
    illvec, _ = trgillvec(srfpoint, t, target)

    # Calculate the angle between the two vectors
    if np.size(t) > 1:
        angle = np.zeros(t.shape[0])
        for i in range(t.shape[0]):
            angle[i] = np.degrees(spice.vsep(obsvec[i], illvec[i]))
    else:
        angle = np.degrees(spice.vsep(obsvec, illvec))
    return angle
