import copy

import numpy as npy


# This class implements a sample to be used with some of the algorithms, if the unknown is a real vector
# In other cases, it can be used as an example or a base class
class basePMOT:
    lowR=None #range for random individuals
    highR=None
    def __init__(self, init):
        self.info=0 #info deactivated by default
        if isinstance(init, int): # init, if it is an integer, is the dimension
            self.x = npy.zeros([init])
        elif isinstance(init, npy.ndarray): # if a npy array, the data
            self.x = init
            #self.x = (self.x).reshape((init.shape))
        else:
            raise Exception('uhhh can''t start from ', init)
        # set a default range for random individuals
        basePMOT.lowR = -10*npy.ones(self.x.size)
        basePMOT.highR = 10*npy.ones(self.x.size)

    def getRanRange(self):
        if self.info>0: print('basePMOT getRanRange')
        return basePMOT.lowR, basePMOT.highR

    def setRanRange(self,lowR,highR):
        if self.info>0: print('basePMOT setRanRange')
        if isinstance(lowR,float):
            basePMOT.lowR = lowR* npy.ones(len(self.x))
        else:
            basePMOT.lowR=lowR
        if isinstance(highR,float):
            basePMOT.highR = highR* npy.ones(len(self.x))
        else:
            basePMOT.highR=highR

    def ranFun(self, ng=0):
        if self.info>0: print('basePMOT ranFun')
        #self.x = npy.random.normal(size=self.x.size, loc=0, scale=5)
        for i in range(len(self.x)):
            self.x[i]=npy.random.uniform(basePMOT.lowR[i],basePMOT.highR[i])

    def setInfo(self, info_):
        self.info = info_

    def getNdof(self): #number of dof, needed by certain algorithms
        return npy.shape(self.x)[0]

    def addVector(self,v): # add a vector to me
        self.x = self.x + npy.reshape(v,[npy.shape(self.x)[0]] )

    def getVector(self): #return my data as a vector
        return self.x

    def setVector(self,newx):
        self.x= npy.reshape(newx,[npy.shape(self.x)[0]] )

    def distance(self,x): # distance is a user-defined measure
        if self.info>0: print('basePMOT distance')
        return npy.sqrt(npy.sum(npy.square(self.x - x.x)))

    def mutFun(self, fa=0, ng=0): # mutation can be of decreasing amplitude when we are closer to the goal
        if self.info>0: print('basePMOT mutFun')
        self.x = self.x + npy.random.normal(size=self.x.size)

    def repFun(self, b, fa=0, fb=0, ng=0):
        if self.info>0: print('basePMOT repFun')
        if not isinstance(b, basePMOT):
            raise Exception('first argument must be an instance of basePMOT ')
        self.x = (self.x + b.x) / 2


    def replaceWithVector(self,newvector):
        a = (self.getNdof())
        print(a)
        self.V = npy.ravel(npy.reshape(newvector, [1,self.getNdof()]))

    def __repr__(self):
        # return x.__str__() ARNAU DIXIT
        return str(self.x.tolist())

    def __str__(self):
        return str(self.x.tolist())

    def __getitem__(self, indx):
        return self.x[indx]

    def __setitem__(self, indx,val):
        #print('set indx=',indx,'val',val)
        self.x[indx]=val
        #print('after setitem self is',self)

    def fitFun(self):  # this function is here only to implement a base gradient, but has to be defined in the derived class
        raise Exception('fitFun is not implemented in base class')

# numerical gradient - TO BE DELETED, it is implemented as a function
    def grad_XXXX(self, eps=0.001):
        #print('eps=',eps)
        fx0 = self.fitFun() # if it is not available, we evaluate it
        nd = npy.shape(self.x)[0]
        g = npy.zeros([nd]) # to store gradient
        for i in range(nd):
            xe = copy.deepcopy(self)
            #print(xe.x.dtype)
            xe[i] = self.x[i] + eps
            #print('grad xe=',xe)
            #print(xe.x[i])
            g[i] = (xe.fitFun() - fx0) / eps
        return g, fx0 # fx0 is the fitness function value evaluated at the initial point

# one step of a simple descent gradient algorithm, evaluating the fitness function NDOF+1 times
    def stepGradient_XXXX(self,step=0.1,eps=0.001): # deprecated method, will be deleted; now it is a function
        xA=self
        g,fxA=self.grad(eps) # find the gradient
        #print('g=',g)
        g=g/npy.linalg.norm(g)
        xB=self.__class__(xA.x-g*step) # find a parabola in the direction of the gradient
        fxB=xB.fitFun()
        xC=self.__class__((xA.x+xB.x)/2)
        fxC=xC.fitFun()
        #print('xA=',xA,'fxA=',fxA)
        #print('xB=',xB,'fxB=',fxB)
        #print('xC=',xC,'fxC=',fxC)
        d=npy.linalg.norm(xA.x-xB.x)
        #print(d)

        x_values = npy.array([0, d, d/2])
        y_values = npy.array([fxA, fxB, fxC])

        coefficients = npy.polyfit(x_values, y_values, 2)

        a, b, c = coefficients

        pmin= -b/(2*a) #location of the minimum

        #print('pmin=',pmin,'min=',npy.polyval(coefficients, pmin))

        # we don't move beyond step
        if pmin>step:
            pmin=step

        r=self.__class__(xA.x -g*pmin)

        return r,pmin # return new location and step
