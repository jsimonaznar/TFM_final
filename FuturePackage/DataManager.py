import copy
from sys import getsizeof
import tracemalloc


# PONER COMENTARIOS
class DataManager:
    __instance = None
    __lock = False

    @staticmethod
    def getInstance():
        if DataManager.__instance is None:
            DataManager()
        return DataManager.__instance

    def __init__(self, roiL1, roiL2, instrumentData, observer):
        if roiL1 is not None and instrumentData is not None and observer is not None and roiL2 is not None:
            if DataManager.__lock:
                raise Exception("Already initialized")
            self.roiList1 = roiL1
            self.roiList2 = roiL2
            self.instrument = instrumentData
            self.observer = observer
            DataManager.__lock = True
        DataManager.__instance = self

    def getROIList(self,s = None, e = None):
        if s is None:
            return self.roiList1, self.roiList2
        else:
            return self.roiList1[s:e+1], self.roiList2[s:e+1]

    def getSingleROI(self, i):
        return self.roiList1[i], self.roiList2[i]

    def getInstrumentData(self):
        return self.instrument

    def getObserver(self):
        return self.observer

    def initObservationDataBase(self, twL, i = None):
        if i is None: #i is the roi number, if None it is assumed that a sorted list containing the constrained TW for each roi is being passed. It must have the same order as the roiList
            for i, tw in enumerate(twL):
                self.roiList1[i].initializeObservationDataBase(tw, self.instrument, self.observer)
        else:
            self.roiList1[i].initializeObservationDataBase(twL, self.instrument, self.observer)