from PSOA.emissionang import emissionang


def illzenithang(srfpoint, t, target):
    """
    Returns the phase angle between the distance vector to the illumination source (the Sun) and the surface normal,
    from the target surface point srfpoint, at time t.

    :param srfpoint: target surface point. It can be input either in latitudinal coordinates (in [deg])
                     or Cartesian coordinates (in [km])
    :param t: time epoch in TDB seconds past J2000 epoch. It can be either a single point in time or
              a discretized vector of different time values
    :param target: string SPICE name of the target body
    :return: angle: angle between the normal surface and the distance vector to the illumination source, in [deg]
    """

    # The illumination source zenith angle is the same as the emission angle
    # but in this case the 'observer' is the illumination source
    angle = emissionang(srfpoint, t, target, 'SUN')

    return angle
