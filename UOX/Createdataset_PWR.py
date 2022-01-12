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

def fuelinput(wp):
    """
    function to calculate the weight percentage of U235 and U238 based on initial enrichment
    
    formulae from http://holbert.faculty.asu.edu/eee460/NumberDensity.pdf
    
    Parameters
    ----------
    wp : float
        Initial enrichment in percentage
        
    Returns
    -------
    fuelstr : str
        Serpent formatted material composition
        
    Notes
    -----
    1, Right now the temperature is hard coded (ie ZAID ends with '.15c'), this can be modified.
    2, Right now the density of fuel is hard coded, this can be modified.
    """
    
    u=1000*1.660539040e-27  #g
    NA=6.0221409e23   ##/mol
    MU235=235.0439299*u*NA    #g/mol
    MU238=238.05078826*u*NA   #g/mol
    MO16= 15.99491461956*u*NA
    rhoUO2=10.5     #g/cm3
    wp=wp/100
    MU=1/(wp/MU235 + (1-wp)/MU238)
    MUO2=MU+2*MO16
    
    rhoU=rhoUO2*(MU/MUO2)
    rhoO=rhoUO2*(MO16/MUO2)
    
    NU235=(wp*rhoU*NA)/MU235
    NU238=((1-wp)*rhoU*NA)/MU238
    NO16=(rhoO*2*NA)/MO16
    NTOT=NU235+NU238+NO16

    M_U235=(wp*rhoU)
    M_U238=((1-wp)*rhoU)
    M_O16=(rhoO*2)
    M_TOT=M_U235+M_U238+M_O16
    fuelstr='mat UOX -10.5 burn 1'
    fuelstr=fuelstr+'\n 92235.15c  -%.8f'%(M_U235/M_TOT)
    fuelstr=fuelstr+'\n 92238.15c  -%.8f'%(M_U238/M_TOT)
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
dataFrame='fuellog_strategicPWR_UOX.csv'
inputFileBU = open('UOX_manyBU')
inputFileBURefStr = inputFileBU.read()
inputFileBU.close()

inputFileCT = open('UOX_manyCT')
inputFileCTRefStr = inputFileCT.read()
inputFileCT.close()

IE=np.linspace(1.5,6.0,46)  #IE range can be modified here
idfuel=0
for ie in IE:
    fstr=fuelinput(ie)
    inputFileBUStr = inputFileBURefStr
    inputFileBUStr = inputFileBUStr.replace('fuelstr', fstr)
    
    sfile='sPWR_IE_%d'%(ie*10)
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
            spentmat=spentmat.replace('UOXp1r1','UOX')
            spentmat=spentmat.replace('\n            1001.15c',' burn 1\n            1001.15c')
            
            inputFileCTStr = inputFileCTRefStr
            inputFileCTStr = inputFileCTStr.replace('matstr', spentmat)
            
            sfilect='sPWR_IE_%d_BU_%d'%(ie*10,bu*10)
            
            os.system('mkdir BU%d'%(bu*10))
            os.chdir(path+'serpent_files/IE%d/BU%d/'%(ie*10,bu*10))
            inputFileRun = open(sfilect,'w')
            inputFileRun.write(inputFileCTStr)
            inputFileRun.close()
            os.system('nohup sss2 '+sfilect+' -omp 64')
            for cti in range(131):
                filepath=path+'serpent_files/IE%d/BU%d/'%(ie*10,bu*10)+sfilect+'.bumat'+str(cti)    
                
                csvstr='%d,%.2f,%.2f,%.2f,UO2,PWR,%s\n'%(idfuel,bu,CTs[cti],ie,filepath)
                idfuel=idfuel+1
                os.chdir(path)
                inputFileRun = open(dataFrame,'a')
                inputFileRun.write(csvstr)
                inputFileRun.close()
            bu=bu+0.5

