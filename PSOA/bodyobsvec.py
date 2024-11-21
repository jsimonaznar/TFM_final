import spiceypy as spice
import numpy as np


def bodyobsvec(t, target, obs, frame=None):
    """
    Distance vector between the target and the observer at time t

    :param t: time epoch in TDB seconds past J2000 epoch.
              It can be either a single point in time or a discretized vector of different time values
    :param target: string SPICE name of the target body
    :param obs: string SPICE name of the observer body
    :param frame: string SPICE name of the reference frame with respect to which the vector is going to be expressed.
                  If this variable is not input, the body-fixed reference frame is used by default
    :return: obsvec: observer position vector as seen from the target center, in [km]
             dist: distance between the observer and the target
    """

    # Target frame
    frame_info = spice.cnmfrm(target)
    target_frame = frame_info[1]
    abcorr = 'NONE'  # Assumption: geometric positions, no light aberrations

    # Compute the observer position as seen from the target in the specified frame
    obsvec, _ = spice.spkpos(obs, t, target_frame, abcorr, target)

    if frame is not None:
        fframe = target_frame
        tframe = frame
        # Process each time point if t is an array of times
        if np.size(t) > 1:
            # Initialize a rotation matrix list
            rotmat_list = [spice.pxform(fframe, tframe, time_point) for time_point in t] # rotation matrix from body-fixed reference frame to the requested one
            # Apply rotation for each time point
            for i, rotmat in enumerate(rotmat_list):
                # Ensure obsvec[:, i] is a 3D vector
                obsvec[i] = np.dot(rotmat, obsvec[i])
                # Compute distance
                dist = np.zeros(obsvec.shape[0])
                for i in range(obsvec.shape[0]):
                    dist[i] = np.linalg.norm(obsvec[i])
        else:
            # Process a single time point
            rotmat = spice.pxform(target_frame, frame, t)
            obsvec = np.dot(rotmat, obsvec)
            dist = np.linalg.norm(obsvec)
    else:
            dist = np.linalg.norm(obsvec)
       
        
        

    

    return obsvec, dist
