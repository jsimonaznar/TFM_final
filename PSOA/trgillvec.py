from PSOA.trgobsvec import trgobsvec


def trgillvec(srfpoint, t, target, frame=None):
    """
    Distance vector between the target surface point P and the illumination source (the Sun), at time t

    :param srfpoint: target surface point. It can be input either in latitudinal coordinates (in [deg])
                     or Cartesian coordinates (in [km]) with respect to the body-fixed reference frame
    :param t: time epoch in TDB seconds past J2000 epoch. It can be either a single point in time or
              a discretized vector of different time values
    :param target: string SPICE name of the target body
    :param frame: string SPICE name of the reference frame with respect to which the vector is going to be
                  expressed. If this variable is not input, the body-fixed reference frame is used by default
    :return: illvec: illumination source position vector as seen from the target surface point in the target
                     body-fixed reference frame, in [km]
             dist: distance between the illumination source and the surface point
    """

    # Call trgobsvec function with 'SUN' as the observer
    illvec, dist = trgobsvec(srfpoint, t, target, 'SUN', frame)

    return illvec, dist
