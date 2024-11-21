import sys

import numpy as np
import spiceypy as spice
from shapely.geometry import Polygon



if False: # deativated until issues are fixed

    from PSOA import *


    def segmentation(optlist, et, target, sc, inst, varargin):
        """
           This function computes the observation windows based on the geometry
            between an observer and the ROIs on a target body

            Programmers:  Paula Betriu (UPC/ESEIAAT)
            Date:         12/2023
            Revision:     1

            Usage:        [tin, nseg, sroi, sst, durst] = segmentation( ...
                              optlist, et)

            Inputs:
              > obsinfo:  struct containing observer and target information,
                          including spacecraft and target SPICE ID names
              > obtlist:  List of structs that contain the information about the
                          observable targets and includes the following fields:
                  # obs:          string SPICE name of the observer body (spacecraft)
                  # inst:         string SPICE name of the instrument
                  # target:       string SPICE name of the body target
                  # campaign:     string that defines the type of campaign:
                      1. 'global': global (large) ROI (future work)
                      2. 'local':  local (small) ROI
                      3. 'single': single point
                  # vertices:    coordinates that bound the observable target.
                                  If it is a single campaign, the latitudinal
                                  coordinates of the observable point are provided.
                                  In the case of both types of ROI, this is a matrix
                                  containing the vertices of the polygon. The vertex
                                  points are expressed in 2D, in latitudinal
                                  coordinates [º]
                  # rgn_name:     string name of the observable target
                  # method:       Future work. string that defines the planetary body
                                  modelization ('DSK' or 'ELLIPSOID')
                  # qkeys:        cell array that contains the dictionary keys of the
                                  queries that apply to the defined observable target.
                                  For instance: qkeys = {'emnang', 'ill', 'dist'};
              > et:       time epoch in TDB seconds past J2000 epoch. It can be
                          either a single point in time or a discretized vector of
                          different time values

            Output:
              > nseg:     number of segments identified where observation conditions
                          are met
              > sroi:     list of strings identifying ROIs corresponding to each
                          segment
              > sst:      array of start times for each segment
              > durst:    array of durations for each segment, in [sec]
        """
        # Pre-allocate variables
        nseg = 0  # number of segments
        sroi = []  # list of intersected ROIs
        sst = []  # initial time where the ground track intersects a region of interest
        durst = []  # duration of the segments
        maxangle = 0  # default to nadir pointing unless specified
        tin = np.zeros_like(et, dtype=bool)  # binary vector that states if each corresponding
        # time step is complying with the orientation constraints

        # Off-nadir pointing
        if len(sys.argv) > 3:  # pointing is restricted to the given maximum off-nadir angle
            # In this scenario, the permissible orientation of the camera is
            # represented by a cone. The axis of this cone aligns with the
            # line-of-sight, which is the vector pointing from the observer to the
            # target. The intersection of this cone with the ground surface
            # delineates the boundary or perimeter of the camera's observation
            # area. This perimeter demarcates the extent within which the camera
            # can observe any point on the surface. If this perimeter overlaps with
            # the region of interest (ROI), it implies that the camera can observe
            # parts of the ROI. Therefore, if there is an intersection between the
            # camera's observation perimeter and the ROI, it indicates that the
            # camera is capable of capturing the ROI within its field of view at
            # that specific point in time. This condition is used to determine if a
            # particular moment falls within the segment of time where the ROI is
            # observable.
            maxangle = float(sys.argv[3])
            # Pre-allocate variables
            method = 'ELLIPSOID'
            dref = inst
            abcorr = 'NONE'
            _, targetframe, _ = spice.cnmfrm(target)  # target frame ID in SPICE
            npoints = 100

            # Parametrize cone perimeter
            R = np.sin(np.radians(maxangle))
            p = lambda rho: np.array([R * np.cos(np.radians(rho)), R * np.sin(np.radians(rho)), 1])


            # Compute segments
        for i in range(len(optlist)):
            # For each observable target on the surface...
            x, y = optlist[i]['vertices'][:, 0], optlist[i]['vertices'][:, 1]

        # Initialize segment tracking
        bstart = False  # boolean that indicates if the segment started
        for tt in range(len(et)):
            # Compute ground track or cone intersection based on
            # established pointing (nadir/off-nadir)
            if maxangle == 0:
                # Evaluate during time step if the spacecraft ground track
                # crosses the ROI
                gtlon, gtlat = groundtrack(sc, et[tt], target)
                bin = any(Point(gtlon, gtlat).within(polygons[0]))  # evaluate if the
                # ground track is inside the ROI polygon
            else:
                for n in range(npoints):
                    dvec = p(rho[n])
                    spoint = spice.sincpt(method, target, et[tt], targetframe, abcorr,
                                           sc, dref, dvec)
                    _, latpoint, _ = spice.reclat(spoint)
                    latpoint *= spice.dpr

                # Intersect polygons
                poly2 = polyshape([latpoint[0], latpoint[1]])
                polyout = polygons[0].intersection(poly2)
                bin = polyout.is_empty  # do polygons intersect?

            if bin and not bstart:
                # Initial time of the segment
                bstart = True
                nseg += 1  # increase by 1 nseg
                sroi.append(str(optlist[i]['rgn_key']))  # save the ROI
                # key where the ground track falls inside
                sst.append(et[tt])
            elif not bin and bstart:
                # Ending time of the segment
                bstart = False
                durst.append(et[tt] - sst[-1])  # duration (in [sec])
                # of the segment

            if bin:
                tin[i] = 1