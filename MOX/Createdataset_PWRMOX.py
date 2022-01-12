# -*- coding: utf-8 -*-
"""
Fuel inventory library (UOX)

Script to run computations. It will produce a set of folders and outputfiles
and a csv file storing linking the output file paths to the BU, CT, IE values.

zsolt elter 2019
"""
import numpy as np
import os
import math
#import pandas as pd
#from PDfunctions import *
def fuelinput(wp):
    """
    function to calculate the weight percentage of MOX nuclides
    
    formulae from http://holbert.faculty.asu.edu/eee460/NumberDensity.pdf
    
    Parameters
    ----------
    wp : float
        Plutonium content in percentage
        
    Returns
    -------
    fuelstr : str
        Serpent formatted material composition
        
    Notes
    -----
    1, Right now the temperature is hard coded (ie ZAID ends with '.15c'), this can be modified.
    2, Right now the density of fuel is hard coded, this can be modified
    3, The fuel string includes Cf nuclides with 0.0w%. This is to force Serpent2 to include these
    nuclides. The reason to include them because they might be relevant in subsequent neutron coincidence
    based calculations.
    """
    u=1000*1.660539040e-27  #g
    NA=6.0221409e23   ##/mol
    M={'U235': 235.0439299*u*NA,
       'U234': 234.0409521*u*NA,
       'U238': 238.05078826*u*NA,
       'Pu238': 238.0495599*u*NA,
       'Pu239': 239.0521634*u*NA,
       'Pu240': 240.0538135*u*NA,
       'Pu241': 241.0568515*u*NA,
       'Pu242': 242.0587426*u*NA}
               
    Puvec={'Pu238':2.5/100,'Pu239':54.7/100,'Pu240':26.1/100,'Pu241':9.5/100,'Pu242':7.2/100}
    Uvec={'U234':0.0012/100,'U235':0.25/100,'U238':99.7488/100} #czsolti 0.00119 rounded to get 1
    MO16= 15.99491461956*u*NA
    rhoMOX=10.5     #g/cm3 czsolti this density falls out from the equations
    
    wp=wp/100
    
    MU=1/sum([Uvec[iso]/M[iso] for iso in Uvec])
    MPu=1/sum([Puvec[iso]/M[iso] for iso in Puvec])

    MHM=(1-wp)*MU+wp*MPu
    MMOX=MHM+2*MO16
    
    
    rhoHM=rhoMOX*(MHM/MMOX)
    rhoO=rhoMOX*(MO16/MMOX)
    
    MVOL={}
    for iso in Uvec:
        MVOL[iso] = (1-wp)*Uvec[iso]*rhoHM
    for iso in Puvec:
        MVOL[iso] = wp*Puvec[iso]*rhoHM
        
    M_O16=(rhoO*2)
    M_TOT=sum(MVOL.values())+M_O16

    fuelstr='mat MOX -10.5 burn 1'
    fuelstr=fuelstr+'\n 92234.15c  -%.8f'%(MVOL['U234']/M_TOT)
    fuelstr=fuelstr+'\n 92235.15c  -%.8f'%(MVOL['U235']/M_TOT)
    fuelstr=fuelstr+'\n 92238.15c  -%.8f'%(MVOL['U238']/M_TOT)
    fuelstr=fuelstr+'\n 94238.15c  -%.8f'%(MVOL['Pu238']/M_TOT)
    fuelstr=fuelstr+'\n 94239.15c  -%.8f'%(MVOL['Pu239']/M_TOT)
    fuelstr=fuelstr+'\n 94240.15c  -%.8f'%(MVOL['Pu240']/M_TOT)
    fuelstr=fuelstr+'\n 94241.15c  -%.8f'%(MVOL['Pu241']/M_TOT)
    fuelstr=fuelstr+'\n 94242.15c  -%.8f'%(MVOL['Pu242']/M_TOT)
    fuelstr=fuelstr+'\n 8016.15c   -%.8f'%(M_O16/M_TOT)
    fuelstr=fuelstr+'\n 98249.15c  -0.0'
    fuelstr=fuelstr+'\n 98250.15c  -0.0'
    fuelstr=fuelstr+'\n 98251.15c  -0.0'
    fuelstr=fuelstr+'\n 98252.15c  -0.0'
    fuelstr=fuelstr+'\n 98253.15c  -0.0'
    fuelstr=fuelstr+'\n 98254.15c  -0.0'
    return fuelstr

### SCRIPT to run

###Init array for CTs-> can be modified if other CT values are preferred.
CT=0
CTs=[0]
decstep=[]
while CT<70*365:
    if CT<10*365:
        decstep.append(91.25)
        CT=CT+91.25
        CTs.append(CT)
    elif CT<40*365:
        decstep.append(2*91.25)
        CT=CT+2*91.25
        CTs.append(CT)
    else:
        decstep.append(4*91.25)
        CT=CT+4*91.25
        CTs.append(CT)

#csv header
csvstr=',BU,CT,IE,fuelType,reactorType,serpent\n'

#path to be updated
path=os.getcwd()+'/'
dataFrame='fuellog_strategicPWR_MOX.csv'
inputFileRun = open(dataFrame,'a')
inputFileRun.write(csvstr)
inputFileRun.close()

inputFileBU = open('MOX_manyBU')
inputFileBURefStr = inputFileBU.read()
inputFileBU.close()

inputFileCT = open('MOX_manyCT')
inputFileCTRefStr = inputFileCT.read()
inputFileCT.close()

IE=np.linspace(4,10,31)
idfuel=0
for ie in IE:
    fstr=fuelinput(ie)
    inputFileBUStr = inputFileBURefStr
    inputFileBUStr = inputFileBUStr.replace('fuelstr', fstr)
    
    sfile='sPWR_MOX_IE_%d'%(ie*10)
    os.chdir(path+'serpent_files/')
    os.system('mkdir IE%d'%(ie*10))
    os.chdir(path+'serpent_files/IE%d/'%(ie*10))
    inputFileRun = open(sfile,'w')
    inputFileRun.write(inputFileBUStr)
    inputFileRun.close()
   
    #pathV=path+'serpent_filesPWR_BIC/'
    #os.system('ssh '+node+' "nice sss2 '+pathV+sfile+' -omp 64"')
    os.system('nice sss2 '+sfile+' -omp 64')
    
    bu=5.0
    for bui in range(10,147):  #5-70 MWd/kgU
        if bui not in [0,21,42,63,84,105,126]:#downtime
            os.chdir(path+'serpent_files/IE%d/'%(ie*10))
            spentmat = open(sfile+'.bumat'+str(bui)).read()
            spentmat=spentmat.replace('MOXp1r1','MOX')
            spentmat=spentmat.replace('\n            1001.15c',' burn 1\n            1001.15c')
            
            inputFileCTStr = inputFileCTRefStr
            inputFileCTStr = inputFileCTStr.replace('matstr', spentmat)
            
            sfilect='sPWR_MOX_IE_%d_BU_%d'%(ie*10,bu*10)
            
            os.system('mkdir BU%d'%(bu*10))
            os.chdir(path+'serpent_files/IE%d/BU%d/'%(ie*10,bu*10))
            inputFileRun = open(sfilect,'w')
            inputFileRun.write(inputFileCTStr)
            inputFileRun.close()
            os.system('nice sss2 '+sfilect+' -omp 64')
            for cti in range(131):
                filepath=path+'serpent_files/IE%d/BU%d/'%(ie*10,bu*10)+sfilect+'.bumat'+str(cti)    
                
                csvstr='%d,%.2f,%.2f,%.2f,MOX,PWR,%s\n'%(idfuel,bu,CTs[cti],ie,filepath)
                idfuel=idfuel+1
                os.chdir(path)
                inputFileRun = open(dataFrame,'a')
                inputFileRun.write(csvstr)
                inputFileRun.close()
            bu=bu+0.5
