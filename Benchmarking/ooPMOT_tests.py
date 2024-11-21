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
            self.x[i]=npy.random.uniform(basePMOT.lowR,basePMOT.highR)
        #self.x = npy.random.rand(5)

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
    
    #def mutFun(self, fa=0, ng=0): # mutation can be of decreasing amplitude when we are closer to the goal
    #    if self.info>0: print('basePMOT mutFun')
    #    #while True:
    #    self.x = self.x + npy.random.normal(loc=0.0, scale=0.1, size=self.x.size)
    #    if not npy.all((self.x >= 0) & (self.x <= 1)):
    #        #break
    #        self.x = npy.clip(self.x, 0.0, 1.0)

    def mutFun(self, fa=0, ng=0, scale_0=0.2):
        if self.info > 0: print('basePMOT mutFun')

        # Adaptive mutation: Scale decreases as generations progress
        scale = scale_0 * (1 - ng / 50)  # Start with scale=0.2, reduce over generations

        mutation = npy.random.normal(loc=0.0, scale=scale, size=self.x.size)
        self.x = self.x + mutation

        # Apply reflective boundary conditions
        if not npy.all((self.x >= -15) & (self.x <= 30)):
            self.x = npy.where(self.x < -15, -self.x, self.x)  # Reflect values < 0 back into the range
            self.x = npy.where(self.x > 30, 2 - self.x, self.x)  # Reflect values > 1 back into the range

    def repFun(self, b, fa=0, fb=0, ng=0):
        if self.info>0: print('basePMOT repFun')
        if not isinstance(b, basePMOT):
            raise Exception('first argument must be an instance of basePMOT ')
        self.x = (self.x + b.x) / 2

    def repFunSBX(self, a, b, eta=1):
        #while True:
        u = npy.random.rand()
        v = npy.random.rand()
        if u <= 0.5:
            beta = (2 * u) ** (1 / (eta + 1))
        else:
            beta = (1 / (2 * (1 - u))) ** (1 / (eta + 1))
        if v <= 0.5:
            self.x = 0.5 * ((1 + beta) * a.x + (1 - beta) * b.x)
                
        else:
            self.x = 0.5 * ((1 - beta) * a.x + (1 + beta) * b.x)

        if not npy.all((self.x >= -15) & (self.x <= 30)):
            self.x = npy.where(self.x < -15, -self.x, self.x)  # Reflect values < 0 back into the range
            self.x = npy.where(self.x > 30, 2 - self.x, self.x)  # Reflect values > 1 back into the range
    
    def repFunBLX_a(self, a, b, alpha=0.0):
        #while True:
            beta = npy.random.uniform(0, 1 + alpha) #(alpha, 1 + alpha)
            self.x = a.x + beta * (b.x - a.x)
            if not npy.all((self.x >= -15) & (self.x <= 30)):
                self.x = npy.where(self.x < -15, -self.x, self.x)  # Reflect values < 0 back into the range
                self.x = npy.where(self.x > 30, 2 - self.x, self.x)  # Reflect values > 1 back into the range


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
