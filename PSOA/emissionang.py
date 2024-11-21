import spiceypy as spice
import numpy as np

from PSOA.trgobsvec import trgobsvec


def emissionang(srfpoint, t, target, obs):
    """
    This function returns the phase angle between the target normal to surface and the distance vector to the observer,
    from the target surface point srfpoint, at time t

    :param srfpoint: target surface point.
                     It can be input either in latitudinal coordinates (in [deg]) or Cartesian coordinates (in [km])
    :param t: time epoch in TDB seconds past J2000 epoch.
              It can be either a single point in time or a discretized vector of different time values
    :param target: string SPICE name of the target body
    :param obs: string SPICE name of the observer body
    :return: angle: angle between the normal surface and the distance vector to the observer, in [deg]
    """

    method = 'ELLIPSOID'  # Assumption: tri-axial ellipsoid modeling of the target body
    targetframe = spice.cnmfrm(target)[1]  # Target frame ID in SPICE

    # Compute the observer position vector as seen from the srfpoint
    obsvec, _ = trgobsvec(srfpoint, t, target, obs)
    # Convert latitudinal coordinates to rectangular if needed
    if len(srfpoint) == 2:
        srfpoint = np.radians(srfpoint)  # [deg] to [rad]
        srfpoint = spice.srfrec(spice.bodn2c(target), srfpoint[0], srfpoint[1])
    else:
        srfpoint = np.array(srfpoint).reshape(-1, 1)

    srfpoint = [srfpoint.reshape([3])]
    
    

    # Obtain the outwards surface normal vector
    if np.size(t) > 1:
        nrmvec = np.zeros((len(t), 3))

        for i in range(len(t)):
            nrmvec[i] = spice.srfnrm(method, target, t[i], targetframe, srfpoint) # https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/srfnrm_c.html
        
        # Angle between the two vectors
        angle = np.zeros(len(t))
        for i in range(len(angle)):
            angle[i] = spice.vsep(obsvec[i], nrmvec[i])
        angle = np.degrees(angle)  # Convert from radians to degrees
    else:
        nrmvec = spice.srfnrm(method, target, t, targetframe, srfpoint)
        #print(obsvec)
        
        nrmvec = np.concatenate(nrmvec, axis=0)
        #print(nrmvec)
        angle = spice.vsep(obsvec, nrmvec)
        angle = np.degrees(angle)  # Convert from radians to degrees
   
    

    return angle
