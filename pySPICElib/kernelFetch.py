import os
import sys

import spiceypy as spice


class kernelFetch:
    def __init__(self, kernelPath_=None, addToKernelPath='', textFilesPath_='./'):
        if kernelPath_:  # Use a specific kernel path and override everything else
            self.kernelPath = os.path.join(kernelPath_, addToKernelPath)
        else:  # Use the path specified with the configuration file or the default
            self.kernelPath = os.path.join(self.getDefaultKernelPath(), addToKernelPath)

        self.textFilesPath = textFilesPath_

        print('kernelFetch: Using ', self.kernelPath, ' for kernels and ', self.textFilesPath, ' for kernel lists ')
        if not os.path.isdir(self.kernelPath):
            print('Creating folder', self.kernelPath)
            os.mkdir(self.kernelPath)
        self.urlList = []  # list of url kernels downloaded
        self.fullPathList = []  # list of local kernel files with full names

    # returns default kernel path,  from user/.pySPICElib.cfg if available or user/kernels otherwise
    @staticmethod
    def getDefaultKernelPath():
        homeFolder = os.path.expanduser('~')  # It should work for both Unix and Windows environments
        configFile = os.path.join(homeFolder, '.pySPICElib.cfg')
        if os.path.exists(configFile):
            f = open(configFile, 'r')
            kernelFolder = f.readline().strip()
            f.close()
        else:
            kernelFolder = os.path.join(homeFolder, 'kernels')
        return kernelFolder

    def getKernelPath(self):
        return self.kernelPath

    @staticmethod
    def findKernelType(urlKernel):
        candidates = ['spk', 'ck', 'ik', 'pck', 'fk', 'lsk', 'sclk', 'ek']
        sp = urlKernel.split('/')  # split url
        kt = 'others'
        for s in sp:
            for c in candidates:
                if s == c:
                    kt = s
                    break
            if kt != 'others':
                break
        return kt

    def url2kernelFileName(self, urlKernel):
        sp = urlKernel.split('/')
        file = sp[len(sp) - 1]
        kt = self.findKernelType(urlKernel)
        path = os.path.join(self.kernelPath, kt)
        fullName = os.path.join(self.kernelPath, kt, file)
        return fullName, path, file

    # download kernel if not locally available or forced to do so
    def fetchKernel(self, urlKernel, forceDownload=False):
        fullFileName, path, file = self.url2kernelFileName(urlKernel)

        if not os.path.exists(path):
            print('Creating folder', path)
            os.mkdir(path)
        if forceDownload:
            print('Forced download ...', end='')
        if forceDownload or (not os.path.isfile(fullFileName)):
            print('Downloading ' + urlKernel + ' as', fullFileName, '....  ', end='')
            if sys.version_info < (3, 9):
                # This block is for Python 3.8 and below
                import urllib.request
                urllib.request.urlretrieve(urlKernel, fullFileName)
                # Alternative method for Python 3.8:
                # with urllib.request.urlopen(urlKernel) as response:
                #     with open(fullFileName, "wb") as outputFile:
                #         outputFile.write(response.read())
                print(' done!')
            else:
                # This block is for Python 3.9 and above
                import requests
                response = requests.get(urlKernel)
                if response.status_code == 200:
                    with open(fullFileName, "wb") as output_file:
                        output_file.write(response.content)
                    print(' done!')
                else:
                    print(f"Failed to download file. Status code: {response.status_code}")
        else:
            print('URL ', urlKernel, ': already have ', fullFileName)

        self.urlList.append(urlKernel)
        self.fullPathList.append(fullFileName)

        return fullFileName

    def getKernelList(self):
        return self.urlList, self.fullPathList

    # download and furnish one kernel
    def ffOne(self, urlKernel, forceDownload=False):
        pk = self.fetchKernel(urlKernel, forceDownload)
        spice.furnsh(pk)

    # download and furnish a kernel list
    def ffList(self, urlKernelL, forceDownload=False):
        for k in urlKernelL:
            self.ffOne(k, forceDownload)

    # processes files to obtain the necessary info and delete comments
    @staticmethod
    def parseShortFile(file):
        f = open(file, 'r')
        lls = f.readlines()
        llp = []
        for ll in lls:
            ll = ll.strip()
            p = ll.find('#')
            if p != -1:
                if p > 0:
                    lo = ll[0:p - 1]
                else:
                    continue
            else:
                lo = ll
            if len(lo) == 0:
                continue
            llp.append(lo)
        f.close()
        return llp

    # download or load kernels from a file
    def ffFile(self, metaK, forceDownload=False):
        lks = self.parseShortFile(self.textFilesPath + metaK)
        for lk in lks:
            self.ffOne(lk, forceDownload)
