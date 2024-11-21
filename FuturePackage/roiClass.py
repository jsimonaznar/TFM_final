import math
import numpy as np


import PSOA as psoa
import spiceypy as spice
from pySPICElib.roiDatabase import roi



class oPlanRoi(roi):
    def __init__(self, body, name, vertices):
        super().__init__(body, name, vertices)
        self.ROI_TW = None
        self.ROI_ObsET = None
        self.ROI_ObsLen = None
        self.ROI_ObsImg = None
        self.ROI_ObsRes = None
        self.ROI_ObsCov = None

    def initializeObservationDataBase(self, roitw, instrument=None, observer= None, timeData = None, nImg = None, res = None):
        self.ROI_TW = roitw  # Compliant TW for a ROI within the mission TW, given certain constraints
        self.ROI_ObsET = self.computeObservationET()
        if timeData is None and nImg is None and res is None:
            timeData, nImg, res = self.computeObservationData(instrument, observer)
        self.ROI_ObsLen = timeData
        self.ROI_ObsImg = nImg
        self.ROI_ObsRes = res

    def initializeScanDataBase(self, roitw, instrument=None, observer= None, timeData = None, cov = None, targetRadii = 2634): # Ganymede's radius [km] by default
        self.ROI_TW = roitw  # Compliant TW for a ROI within the mission TW, given certain constraints
        self.ROI_ObsET = self.computeObservationET()
        #print(self.ROI_ObsET)
        if timeData is None and cov is None:
            timeData, cov = self.computeScanData(observer = observer, targetRadii = targetRadii)
        self.ROI_ObsLen = timeData
        self.ROI_ObsCov = cov

    def computeObservationET(self):
        et_list = []
        compliantIntervals = spice.wncard(self.ROI_TW)
        for i in range(compliantIntervals):
            twBegin, twEnd = spice.wnfetd(self.ROI_TW, i)
            t = np.linspace(twBegin, twEnd, num=1000, endpoint=True)
            et_list.append(t)
        #print(len(et_list))
        return et_list

    def computeObservationData(self, instrument, observer):
        #print('Entra en compute')
        tw_ObsLengths = []
        tw_NImgs = []
        tw_res = []
        for compliantInterval in self.ROI_ObsET:
            nimg = []
            time = []
            res = []
            for i, et in enumerate(compliantInterval):
                r = psoa.pointres(instrument.ifov, self.centroid, et, self.body, observer)  # km/pix
                if np.isnan(r):
                    return np.nan, np.nan
                areaCov = (r * instrument.npix) ** 2
                nimg.append(math.ceil((self.area / areaCov) * (1 + instrument.safetyFactor / 100)))
                #print(nimg[i])
                time.append(nimg[i] * instrument.imageRate)
                res.append(r)
            tw_ObsLengths.append(np.array(time))
            tw_NImgs.append(np.array(nimg))
            tw_res.append(np.array(res))

        return tw_ObsLengths, tw_NImgs, tw_res
    
    def computeScanData(self, observer, targetRadii = 2634):
        tw_ObsLengths = []
        tw_cov = []
        for compliantInterval in self.ROI_ObsET:
            cov = []
            # Calculate the duration of the interval
            start = compliantInterval[0]  # First ET in the interval
            end = compliantInterval[-1]   # Last ET in the interval
            time = end - start  # Duration of the interval

            for i, et in enumerate(compliantInterval):
                #print(len(compliantInterval))
                c = psoa.radarcover(targetRadii, psoa.groundtrack(observer, et, self.body), et, self.body, observer) 
                if np.isnan(c):
                    cov.append(np.nan)
                else:
                    cov.append(c)
            tw_ObsLengths.append(np.array(time))
            tw_cov.append(np.array(cov))

        return tw_ObsLengths, tw_cov

    def interpolateObservationData(self, t, interval = None):
        #print(self.name)
        if interval is None:
            for int in range(len(self.ROI_ObsET)):
                start = self.ROI_ObsET[int][0]
                end = self.ROI_ObsET[int][-1]
                if start <= t <= end:
                    break
                else:
                    continue
            nimages = math.ceil(np.interp(t, self.ROI_ObsET[int], self.ROI_ObsImg[int]))
            timeobs = np.interp(t, self.ROI_ObsET[int], self.ROI_ObsLen[int])
            # print('t = ', t, '\n obsET = ', self.ROI_ObsET[interval][-1])
            res = np.interp(t, self.ROI_ObsET[int], self.ROI_ObsRes[int])
            return nimages, timeobs, res
        else:
            nimages = math.ceil(np.interp(t, self.ROI_ObsET[interval], self.ROI_ObsImg[interval]))
            timeobs = np.interp(t, self.ROI_ObsET[interval], self.ROI_ObsLen[interval])
            #print(f'images observation: {nimages}')
            #print(f'length observation: {self.ROI_ObsLen[interval]}')
            #print(f'time observation: {self.ROI_ObsET[interval]}')
            #print(f'time et: {t}')
            # print('t = ', t, '\n obsET = ', self.ROI_ObsET[interval][-1])
            res = np.interp(t, self.ROI_ObsET[interval], self.ROI_ObsRes[interval])
            return nimages, timeobs, res

