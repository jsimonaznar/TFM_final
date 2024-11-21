import spiceypy as spice
import numpy as np


def altitude(obs, target, t):
    """
    This function returns the observer altitude over the target body surface, at time(s) t

    :param obs: string SPICE name of the observer body
    :param target: string SPICE name of the target body
    :param t: time epoch in TDB seconds past J2000 epoch.
              It can be either a single point in time or a discretized vector of different time values
    :return: alt: observer altitude over the body surface at each time step, in [km]
    """

    method = 'INTERCEPT/ELLIPSOID'  # Target modeling
    abcorr = 'NONE'  # Aberration correction
    tframe = spice.cnmfrm(target)[1]  # Target frame ID in SPICE

    # Initialize altitude array
    t = np.atleast_1d(t)  # Ensure t is an array for iteration
    alt = np.zeros(t.shape)

    # Iterate over each time to calculate altitude
    for i, ti in enumerate(t):
        # Get sub-observer point
        subpnt = spice.subpnt(method, target, ti, tframe, abcorr, obs)[0]

        # Compute the observer position vector as seen from the sub-observer point
        obsvec, _ = spice.spkpos(obs, ti, tframe, abcorr, target)

        # Compute altitude: distance between observer and sub-observer point
        alt[i] = spice.vnorm(obsvec - subpnt)

    # If input t was a scalar, return a scalar altitude
    if np.isscalar(t) or len(t) == 1:
        return alt[0]
    return alt
