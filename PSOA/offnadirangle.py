import spiceypy as spice
import numpy as np

from PSOA.bodyobsvec import bodyobsvec
from PSOA.trgobsvec import trgobsvec


def offnadirangle(srfpoint, t, target, obs):
    """
    Calculates the off-nadir angle of an observer with respect to a point on the surface of a target body at a given time.
    The off-nadir angle is the angle between the line-of-sight from an observer to a surface point and the nadir vector.

    :param srfpoint: target surface point.
                     It can be input either in latitudinal coordinates (in [deg]) or Cartesian coordinates (in [km])
    :param t: time epoch in TDB seconds past J2000 epoch.
              It can be either a single point in time or a discretized vector of different time values
    :param target: string SPICE name of the target body
    :param obs: string SPICE name of the observer body
    :return: angle: off-nadir angle for each time step, in [deg]
    """

    # Compute observer's position relative to the target body in the body-fixed frame (nadir)
    bodyobspos, _ = bodyobsvec(t, target, obs)

    # Normalize observer's position vector to unit length
    u = -bodyobspos / np.linalg.norm(bodyobspos)
    # Compute observer's position relative to the surface point in the body-fixed frame (off-nadir)
    srfobspos, _ = trgobsvec(srfpoint, t, target, obs)
    
    # Normalize observer's position vector to unit length
    v = -srfobspos / np.linalg.norm(srfobspos)
    # Calculate angle
    if np.size(t) > 1:
        angle = np.zeros(t.shape[0])
        for i in range(t.shape[0]):
            angle[i] = np.degrees(spice.vsep(u[i], v[i]))

    else:
        angle = np.degrees(spice.vsep(u, v))
    return angle
