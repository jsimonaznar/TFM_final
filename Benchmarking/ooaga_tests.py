import copy
import random

import numpy as npy


# aga meaning A Genetic Algorithm
class aga:
    def __init__(self, sample, pop, options=None):
        self.sample = sample
        self.setPopulation(pop)
        self.defaultOptions = {'ne': 1,  # elite, won't change
                               'nm': int(self.np * 0.2),
                               # new individuals obtained by mutation (or mutants after reproduction if biological=True, to be implemented)
                               'nd': int(self.np * 0.7),  # new individuals obtained by reproduction
                               'nCanMutate': npy.max([int(self.np * 0.05),1]),  # number of individuals considered mutants
                               'nCanProcreate': int(self.np * 0.3),  # number of individuals considered parents
                               'degenerateDistance': 1e-4, # individuals at distance <= than this are considered degenerate
                               'repFunction': 'BLX_a', # use the BLX-alpha crossover to reproduce
                               'info': 0}
        self.defaultOptions['nn'] = self.np - self.defaultOptions['ne'] - self.defaultOptions['nm'] - \
                                    self.defaultOptions['nd']  # new individuals that are random
        if options is None:
            self.options = self.defaultOptions.copy()
        else:
            self.options = options


    def getOptions(self):
        return self.options.copy()

    def getOption(self,name):
        return self.options[name]

    def getPopulationSize(self):
        return len(self.pop)

    #set or get just one option
    def setOptions(self, options):
        self.options = options

    def setOption(self, name, value):
        self.options[name] = value

    def printStatus(self):
        print('Population:')
        for i in range(len(self.pop)):
            print('i=', f'{i:3d}', ':', self.pop[i], ' fit= '+f'{self.fit[i]:8.3e}',' type=',self.popType[i],end='')
            if i>0:
                print(' distToPrevious:',self.pop[i].distance(self.pop[i-1]))
            else:
                print()
        print('Sorted=',self.sorted)

    # Starts user defined population and population type
    # popType is a list of short strings that define the origin of each individual
    # N: new
    # M: mutant
    # D: descendant
    # I: initial
    # L: loaded
    # FM: forced mutation
    # ....
    def setPopulation(self, initpop):
        if isinstance(initpop,int): #An integer, it is just the population size
            self.np=initpop
            self.pop=[]
            self.popType=[]
            self.fit=[]
            for i in range(self.np):
                self.pop.append(copy.deepcopy(self.sample))
                self.pop[i].ranFun()
                self.popType.append('N')
                self.fit.append(0)
        elif isinstance(initpop,list): # A list: it is the population
            self.pop = initpop
            self.np = len(self.pop)
            self.popType = ['I']*self.np
            self.fit=[0]*self.np
            if not type(self.pop[0]) is type(self.sample):
                raise Exception('pop should be of a list of objects of the same class as the sample')
        else:
            raise Exception('pop should be an integer(population size) or a list with the population')
        self.sorted = False

    def getPopulation(self):
        return self.pop
    def evalFitnessAndSort(self):
        self.fit = [0] * self.np
        for i in range(self.np):
            self.fit[i] = self.pop[i].fitFun()
        sorted_indices = sorted(range(len(self.fit)), key=lambda k: self.fit[k])
        self.pop = [self.pop[i] for i in sorted_indices]
        self.fit = [self.fit[i] for i in sorted_indices]
        self.popType = [self.popType[i] for i in sorted_indices]
        self.sorted=True

# assuming that the population is sorted, forces a mutation if two consecutive individuals are equal
    # or very close (distance<degenerateDistance); fitness of mutants is reevaluated and population is sorted again
    def mutateDegenerates(self,gen):
        if not self.sorted:
            raise Exception('sort to detect degenerates')
        forcedMutants=[]
        for i in range(1,len(self.pop)): # distance between consecutive individuals
            dist=self.pop[i].distance(self.pop[i-1])
            if dist<= self.options['degenerateDistance']: # if too close, force to mutate
                if self.options['info']>1: print('Distance = ',dist,'Individual ',i,'=',self.pop[i],' forced to mutate and reevaluated')
                forcedMutants.append(i)

        if self.options['info']>1:
            print('forced mutants:',forcedMutants)

        for i in forcedMutants:
                q= copy.deepcopy(self.pop[i])
                q.mutFun(self.fit[i],gen)
                self.pop[i]=q
                self.fit[i]=q.fitFun()
                self.popType[i]='FM' # forced mutation
        self.sort()
# replaces one invidual with a specified new individual; by default, it replaces the last
    def replaceIndividual(self,newIndividual, newFitness, newType,i=-1):
        if not self.sorted:
            raise Exception('sort to replaceIndividual')
        self.pop[i]=newIndividual
        self.fit[i]=newFitness
        self.popType[i]=newType
        self.sort()

    def sort(self): # sorts, assuming fitness is already updated
        sorted_indices = sorted(range(len(self.fit)), key=lambda k: self.fit[k])
        self.pop = [self.pop[i] for i in sorted_indices]
        self.fit = [self.fit[i] for i in sorted_indices]
        self.popType = [self.popType[i] for i in sorted_indices]
        self.sorted=True

    def printOptions(self):
        print('aga run options: ne=', self.options['ne'],
              'nm=', self.options['nm'],
              'nd=', self.options['nd'],
              'nn=', self.options['nn'],
              'nCanMutate=', self.options['nCanMutate'],
              'nCanProcreate=', self.options['nCanProcreate'])

    def getBest(self):
        if self.sorted:
            return self.pop[0],self.fit[0], self.popType[0]
        else:
            raise Exception('call evalFitnessAndSort before getBest')
    def getFitBest(self):
        return self.fit[0]

    def getPopSize(self):
        return len(self.pop)
    def repopulate(self,gen): # Manel style # Tiene fallo
        if not self.sorted:
            raise Exception('call evalFitnessAndSort before repopulate')

        ne = self.options['ne']
        nm = self.options['nm']
        nd = self.options['nd']
        nn = self.options['nn']
        nCanMutate = self.options['nCanMutate']
        nCanProcreate = self.options['nCanProcreate']

        pop2 = self.pop  # will be overwritten
        popType2= self.popType
        if hasattr(self, 'crowd'):
            sorted_population = sorted([(self.pop[i], self.front[i], self.crowd[i]) for i in range(len(self.pop))],
        key=lambda x: (x[1], -x[2]))
        else:
            sorted_population = sorted([(self.pop[i], self.front[i]) for i in range(len(self.pop))],
        key=lambda x: (x[1]))
        for i in range(len(self.pop)):
            if i < ne:  # unchanged elite
                #print('Elite info original',self.pop[i].info)
                pop2[i] = copy.deepcopy(sorted_population[i][0])
                #print('Elite info copy',pop2[i].info)
                popType2[i] = self.popType[i] #same type
                if (self.options['info'] >= 2): print('--pop2', i, 'is a copy of ', i, 'type:',popType2[i],':',end=''), print(pop2[i])
                popType2[i] = 'E'
                # print(i,'elite')
            elif i < ne + nm:  # mutants
                origin = random.randint(0, nCanMutate - 1)
                #print('origin = ',origin)
                a=sorted_population[origin][0]
                #print(type(a))
                #print('original info ',a.info)
                b= copy.deepcopy(a)
                #print('copy info ',b.info)
                pop2[i] = b
                pop2[i].mutFun(self.fit[i], ng = gen)
                self.fit[i, :] = pop2[i].fitFun()
                popType2[i] = 'M'
                if (self.options['info'] >= 2): print('--pop2', i, 'is a mutant of', origin,'type:',popType2[i],':',end=''), print(pop2[i])
                # print(i,'mutant of 0')
            elif i < ne + nd + nm:  # desdendants
                parent1 = random.randint(0, nCanProcreate - 1)
                parent2 = random.randint(0, nCanProcreate - 1)
                while parent1 == parent2: parent2 = random.randint(0, nCanProcreate - 1)
                if self.options['repFunction'] == 'BLX_a':                
                    pop2[i].repFunBLX_a(sorted_population[parent1][0], sorted_population[parent2][0]) #TO BE DONE: CALL WITH FITNESS & GENERATION !!!
                else:
                    pop2[i].repFunSBX(sorted_population[parent1][0], sorted_population[parent2][0])
                self.fit[i, :] = pop2[i].fitFun()
                popType2[i] = 'D'
                if (self.options['info'] >= 2): print('--pop2', i, 'is a descendant of', parent1, 'and', parent2,'type:',popType2[i],':',end=''), print(pop2[i])
            else:  # newcommers
                pop2[i] = copy.deepcopy(self.sample)
                pop2[i].ranFun()
                self.fit[i, :] = pop2[i].fitFun()
                popType2[i] = 'N'
                if (self.options['info'] >= 2): print('--pop2', i, 'is a newcommer',end=''), print(pop2[i])
        self.pop = pop2
        self.popType = popType2
        self.sorted=False

        if (self.options['info'] >= 3):print('status inside base class after repopulate'); self.printStatus()


# Pablo:
#    if maxFitEval is not None:
#        if sample.nfit>maxFitEval:
#            break
# idem en SA
    def run(self, ng=10,goal=-1e7,maxFitEval=None):
        if (self.options['info'] ): print('AGA vanilla run')
        reeval=True
        if self.options['info'] >= 1:
            self.printOptions()
        for g in range(0, ng):  # 1 generation is defined as: fitness evaluation + reproduction
            self.evalFitnessAndSort()
            self.mutateDegenerates(g) # forces mutation of degenerates and reevaluates their fitness
            if (self.options['info'] >= 1):
                print('**** AGA run best', g, ' best fitness is ', self.fit[0])
            if self.getFitBest()<=goal:
                if (self.options['info'] ): print('**** AGA goal reached')
                reeval=False # don't need to reevaluate
                break
            if maxFitEval is not None:
                if self.sample.nfit >= maxFitEval:
                    reeval = False
                    break
            self.repopulate(g)
        if reeval: # we need to reevaluate if iterations are ended after repopulation
            self.evalFitnessAndSort()
            if self.options['info']>0: print('**** AGA run best END', ' best fitness is ', self.fit[0])

        return self.pop[0],self.fit[0],self.popType[0],g