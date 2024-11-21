import string
import copy
import math

import numpy as np

import spiceypy as spice
import spiceypy.utils.support_types as stypes
import matplotlib.pyplot as plt
import matplotlib.patches as patches


# creates a time window
def newTimeWindow(t0,t1):
    r = stypes.SPICEDOUBLE_CELL(2) # tw to contain the result
    spice.wninsd(t0, t1, r)
    return r

def print_tw(tw, label=None, detailed=False): # detailed option is not implemented yet
    nint = spice.wncard(tw)
    if label:
        print('Time window', label, ' ',end='')
    if nint==0:
        print('empty')
        return
    if nint>1:
        print('number of intervals', nint)
    for i in range(nint):
        intbeg, intend = spice.wnfetd(tw, i)
        if nint>1:
            print(' interval ',i,' ',end='')
        print(' start ', intbeg,'=',spice.et2datetime(intbeg), 'end ', intend,'=',spice.et2datetime(intend), 'length (h)=',
              (intend - intbeg) / 3600.0)

# returns a list of instants in tw, separated step seconds
def getSteps_tw(tw,step):
    lt=[]
    nint = spice.wncard(tw)
    for i in range(nint):
        intbeg, intend = spice.wnfetd(tw, i)
        et=intbeg
        while et<=intend:
            lt.append(et)
            et+=step
        if et!=intend:
            lt.append(intend)
    return lt
def plot_tw(ax,tw,lo,hi,color,timeStart=0.0):
    nint = spice.wncard(tw)
    for i in range(nint):
        intbeg, intend = spice.wnfetd(tw, i)
        intbeg = intbeg-timeStart
        intend = intend-timeStart
        ax.add_patch(patches.Rectangle( (intbeg,lo),width=intend-intbeg, height=hi-lo,lw=1,color=color,fill=True))

# From a vector of et, generates labels fot a plot
# ndates can be:
# A integer, and then it is the number of dates
# A list of strings with the dates to be ploted
# If accurate is True, the whole time string is generated, with seconds

def etToAxisStrings(et, ndates=5, accurate=False):
    # Select vector of et
    if isinstance(ndates, int):  # just the number of marks
        idx = np.round(np.linspace(0, len(et) - 1, ndates)).astype(int)
        etv = [et[i] for i in idx]  # we select a ndates equally spaced values
        convert = True
    else:  # a list, we assume they are strings and generate the et
        convert = False
        etv = [spice.str2et(d) for d in ndates]
        ets = ndates

    # Convert to strings (if needed)
    if convert:
        ets = []
        for x in etv:
            ww = spice.et2utc(x, 'C', 0)
            ww = ww.split(' ')
            if accurate:
                s = ww[0] + ' ' + ww[1] + ' ' + ww[2] + ' '+ww[3]
            else:
                s = ww[0] + ' ' + ww[1] + ' ' + ww[2]
            ets.append(s)

    return etv, ets


# userfun: user defined function, takes one float (et) and returns one float
# cnfine: time window to search OR list with two floats that are the start and end of et for the search
# relate: '<', '>', 'RANGE'
# refval: value searched (eg., < 1e6 ) or range [min,max]
# step: search interval as in SPICE functions (see doc)
# max number of intervals of the tw returned
# returns a time window

# iterates until one of 3 conditions is satisfied: max iterations, x tolerance, y tolerance
def mySolver(userfun,e0,e1,nite,xtolerance,ytolerance): # Auxiliary of myTwFinder (Bolzano slow, by now)
    a=e0
    fa=userfun(e0)
    b=e1
    fb=userfun(e1)
    ite=0
    if fa*fb>0:
        raise Exception('fa*fb>0')

    while True:
        c=(a+b)/2.
        fc=userfun(c)
        if fa*fc>0:
            a=c
        else:
            b=c
        if abs(fc)<ytolerance or b-a < xtolerance or ite>nite:
            return c,fc
        ite=ite+1

def myTwFinder(userfun, cnfine, relate, refval, step, maxntw=200,nite=20,xtolerance=1.0,ytolerance=1.0):
    info=0
    def val(x): # val<0: false; >0: true
        q = userfun(x) - refval
        if relate=='<': q = -q
        return q

    if relate.upper() != 'RANGE' and relate != '<' and relate != '>':
        raise Exception('unknown relate type ',relate)

    if relate.upper()=='RANGE':
        ftw = myTwFinder(userfun, cnfine,'>',refval[0],step,maxntw)
        r   = myTwFinder(userfun, ftw   ,'<',refval[1],step,maxntw)
        return r

    r = stypes.SPICEDOUBLE_CELL(maxntw) # tw to contain the result

    if isinstance(cnfine,spice.utils.support_types.SpiceCell):
        pass
    else:
        t0=cnfine[0]
        t1=cnfine[1]
        cnfine = stypes.SPICEDOUBLE_CELL(2)
        spice.wninsd(t0, t1, cnfine)
    nint = spice.wncard(cnfine)
    if info: print('number of intervals in search time window', nint)
    for i in range(nint): # for each interval in the search time window
        et0, et1 = spice.wnfetd(cnfine, i) # get start & end
        rr=np.arange(et0+step,et1+step,step)

        if val(et0)>0:
            if info: print('>> START1: ',et0, val(et0),spice.et2datetime(et1))
            tstart=et0
            state=True
        else:
            state=False
        for t in rr:
            v=val(t)
            if v>0: # is true
                if state==False: #and was false
                    zt, _ = mySolver(val, t - step, t, nite=nite, xtolerance=xtolerance,ytolerance=ytolerance)
                    if info: print('>> START2: ', zt,val(zt),spice.et2datetime(zt))
                    tstart = zt
                state = True
            else: # is false
                if state==True: # and was true
                    zt,_ = mySolver(val, t - step, t, nite=nite, xtolerance=xtolerance,ytolerance=ytolerance)
                    if info: print('>> END1: ',t,val(t),spice.et2datetime(zt))
                    tend = zt
                    spice.wninsd(tstart, tend, r)  # add an interval
                state = False
        if state==True:
            if info: print('>> END2: ', et1, val(et1),spice.et2datetime(et1))
            tend = et1
            spice.wninsd(tstart, tend, r)

    return r



# searches for the time window when all the conditions defined by qlist are satisfied (AND)
# each list entry is another list with: [function, operator, value/range ]
def myTwFinderList(qlist, cnfine, step, maxntw=200, nite=20, xtolerance=0.1, ytolerance=0.1):
    searchw = cnfine
    for i in range(len(qlist)):
        q = qlist[i]
        uf = q[0]
        relate = q[1]
        refval = q[2]
        retw = myTwFinder(uf, searchw, relate, refval, step, nite=nite, xtolerance=xtolerance, ytolerance=ytolerance)
        searchw = retw
    return retw


# plots each function of the qlist in a separated figure (intended to visualize the results of the previous function)
def myTwPlotter(qlist, cnfine, step = 100, final_tw=None, plotSearchTw=False, ylabels=None):
    tv = getSteps_tw(cnfine,step)
    for f,_ in enumerate(qlist):
        print('f = ....',f,'len=',len(qlist))
        val = [0]*len(tv)
        for i, et in enumerate(tv):
            fun = qlist[f][0]
            val[i] = fun(et)
        lo = min(val)
        hi = max(val)
        etv, ets = etToAxisStrings(tv, 5, accurate=True)
        fig,ax = plt.subplots()
        plt.plot(tv,val)
        plt.xticks(etv, ets)
        if ylabels is None:
            plt.ylabel('function '+str(f))
        else:
            plt.ylabel(ylabels[f])
        plt.xticks(rotation=15)
        if plotSearchTw:
            plot_tw(ax,cnfine,lo,hi,'b')
        qvals=qlist[f][2]
        if isinstance(qvals,list):
            for qval in qvals:
                plt.plot([min(tv),max(tv)],[qval,qval],'k')
        else:
            plt.plot([min(tv), max(tv)], [qvals, qvals], 'k')
        if final_tw is not None:
            plot_tw(ax,final_tw,min(val),max(val),'r')

        plt.show()

# Plot ground track
def plotGtrack(ax,lon,lat,label='',color='r',lw=1,markerStart=None):
    d = [math.fabs(lon[i+1]-lon[i]) for i in range(len(lon)-1)]
    brk = [i for i in range(len(d)) if d[i] > 180.]
    if len(brk)==0:
        ax.plot(lon,lat,label=label,color=color,lw=lw)
    else:
        ax.plot(lon[:brk[0]], lat[:brk[0]], label=label,color=color, lw=lw)
        for i in range(len(brk)-1):
            ax.plot(lon[brk[i]+1:brk[i+1]],lat[brk[i]+1:brk[i+1]], color=color,lw=lw)
        ax.plot(lon[brk[-1]+1:], lat[brk[-1]+1:], color=color, lw=lw)
    if markerStart is not None:
        ax.plot(lon[0],lat[0],marker=markerStart, color=color, lw=lw)


# plot region of interest
def plotRoi(ax,roi,color='r',lw=1): #TO DO: solve the issue of regions between 180 and -180
    v=roi['vertices']
    nr, nc = v.shape
    for i in range(nr):
        j = i + 1
        if i == nr - 1:
            j = 0
        delta = math.fabs(v[i,0]-v[j,0])
        plt.plot([v[i,0], v[j,0]], [v[i,1], v[j,1]], color=color, linewidth=lw)
    plt.text(v[0, 0], v[0, 1], roi['rgn_name'], color=color)




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
            rotmat_list = [spice.pxform(fframe, tframe, time_point) for time_point in
                           t]  # rotation matrix from body-fixed reference frame to the requested one
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
            nrmvec[i] = spice.srfnrm(method, target, t[i], targetframe,
                                     srfpoint)  # https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/srfnrm_c.html

        # Angle between the two vectors
        angle = np.zeros(len(t))
        for i in range(len(angle)):
            angle[i] = spice.vsep(obsvec[i], nrmvec[i])
        angle = np.degrees(angle)  # Convert from radians to degrees
    else:
        nrmvec = spice.srfnrm(method, target, t, targetframe, srfpoint)
        # print(obsvec)

        nrmvec = np.concatenate(nrmvec, axis=0)
        # print(nrmvec)
        angle = spice.vsep(obsvec, nrmvec)
        angle = np.degrees(angle)  # Convert from radians to degrees
    return angle


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
    if np.size(t) > 1:
        sctrack = np.zeros((t.shape[0], 3))
        gtlon = np.zeros(t.shape[0])
        gtlat = np.zeros(t.shape[0])
        for i in range(len(t)):
            sctrack[i] = spice.subpnt(method, target, t[i], tframe, abcorr, obs)[0]  # Sub-spacecraft point
            _, gtlon[i], gtlat[i] = spice.reclat(sctrack[i])  # Convert to latitudinal coordinates
    else:
        sctrack = spice.subpnt(method, target, t, tframe, abcorr, obs)[0]
        _, gtlon, gtlat = spice.reclat(sctrack)
    # sctrack = spice.subpnt(method, target, t, tframe, abcorr, obs)[0]  # Sub-spacecraft point
    # _, gtlon, gtlat = spice.reclat(sctrack)  # Convert to latitudinal coordinates

    gtlon = spice.dpr() * gtlon  # Convert from radians to degrees
    gtlat = spice.dpr() * gtlat  # Convert from radians to degrees

    return gtlon, gtlat


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

def trgobsvec(srfpoint, t, target, obs, frame=None):
    """
    Distance vector between the target point P and the observer at time t

    :param srfpoint: target surface point. It can be input either in latitudinal coordinates (in [deg])
                     or Cartesian coordinates (in [km]) with respect to the body-fixed reference frame
    :param t: time epoch in TDB seconds past J2000 epoch. It can be either a single point in time or
              a discretized vector of different time values
    :param target: string SPICE name of the target body
    :param obs: string SPICE name of the observer body
    :param frame: string SPICE name of the reference frame with respect to which the vector is going to be
                  expressed. If this variable is not input, the body-fixed reference frame is used by default
    :return: obsvec: observer position vector as seen from the target surface point in the target body-fixed
                     reference frame, in [km]
             dist: distance between the observer and the surface point
    """

    # Target frame
    frame_info = spice.cnmfrm(target)
    target_frame = frame_info[1]
    if frame is None:
        frame = target_frame

    abcorr = 'NONE'  # Assumption: geometric positions, no light aberrations

    # Convert latitudinal coordinates to rectangular if needed
    if len(srfpoint) == 2:
        srfpoint = np.radians(srfpoint)  # [deg] to [rad]
        srfpoint = spice.srfrec(spice.bodn2c(target), srfpoint[0], srfpoint[1])

    # Compute the observer position as seen from the srfpoint
    obspos, _ = spice.spkpos(obs, t, frame, abcorr, target)
    obsvec = obspos - srfpoint.T  # srfpoint-observer distance vector

    # If a different reference frame is requested
    if frame:
        # Process each time point if t is an array of times
        if np.size(t) > 1:
            # Initialize a rotation matrix list
            rotmat_list = [spice.pxform(target_frame, frame, time_point) for time_point in t] # rotation matrix from body-fixed reference frame to the requested one
            # Apply rotation for each time point
            for i, rotmat in enumerate(rotmat_list):
                # Ensure obsvec[:, i] is a 3D vector
                obsvec[i] = np.dot(rotmat, obsvec[i])

            # Compute distance
            dist = np.zeros(obsvec.shape[0])
            for i in range(obsvec.shape[0]):
                dist[i] = np.linalg.norm(obsvec[i], axis=0)
        else:
            # Process a single time point
            rotmat = spice.pxform(target_frame, frame, t)
            obsvec = np.dot(rotmat, obsvec)
            # Compute distance
            dist = np.linalg.norm(obsvec)

    return obsvec, dist

def trgobsdist(srfpoint, t, target, obs, frame=None):
    obsvec, dist = trgobsvec(srfpoint, t, target, obs, frame=None)
    return dist