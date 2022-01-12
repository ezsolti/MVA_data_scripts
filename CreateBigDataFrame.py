"""
Script to create dataframe from serpent bumat files
including all the nuclides.

Zsolt Elter 2019

"""
import json
import os
with  open ('nuclides.json') as json_file:
    nuclidesDict = json.load(json_file)


#final name of the file
dataFrame='PWR_UOX-MOX_BigDataFrame-SF-GSRC-noReactorType.csv'


def readInventory(filename):
    """Function to read Serpent bumat files
    
    Parameter
    ---------
    filename : str
        path to the bumatfile to be read
    
    Returns
    -------
    inventory : dict
        dictionary to store the inventory. keys are ZAID identifiers (str), values
        are atom densities (str) in b^{-1}cm^{-1}
    """
    
    mat=open(filename)
    matfile=mat.readlines()
    mat.close()
    inventory={}
    for line in matfile[6:]:
        x=line.strip().split()
        inventory[x[0][:-4]]=x[1]
    return inventory


#header of file
dataFrameStr=',BU,CT,IE,fuelType,TOT_SF,TOT_GSRC,TOT_A,TOT_H'
for nuclIDi in nuclidesDict.values():
    dataFrameStr=dataFrameStr+',%s'%nuclIDi  #here we add the nuclide identifier to the header!
dataFrameStr=dataFrameStr+'\n'
#header ends

f = open(dataFrame,'w')
f.write(dataFrameStr)
f.close()

#let's open the file linking to the outputs
csv=open('file_log_PWR_UOX-MOX.csv').readlines()

depfileOld=''
for line in csv[1:]:
    x=line.strip().split(',')
    ####SFRATE AND GSRC
    if x[4]=='UOX':
        deppath='/UOX/serpent_files/' #since originally I have not included a link to the _dep.m file, here I had to fix that 
        depfileNew='%s/IE%d/BU%d/sPWR_IE_%d_BU_%d_dep.m'%(deppath,10*float(x[3]),10*float(x[1]),10*float(x[3]),10*float(x[1])) #and find out from the BIC parameters
    else:                                                                                                                      #the path to the _dep.m file...
        deppath='/MOX/serpent_files/'
        depfileNew='%s/IE%d/BU%d/sPWR_MOX_IE_%d_BU_%d_dep.m'%(deppath,10*float(x[3]),10*float(x[1]),10*float(x[3]),10*float(x[1]))

    

    if depfileNew != depfileOld: #of course there is one _dep.m file for all the CT's for a given BU-IE, so we keep track what to open. And we only do it once
    #things we grep here are lists!
        TOTSFs=os.popen('grep TOT_SF %s -A 2'%depfileNew).readlines()[2].strip().split()  #not the most time efficient greping, but does the job
        TOTGSRCs=os.popen('grep TOT_GSRC %s -A 2'%depfileNew).readlines()[2].strip().split()
        TOTAs=os.popen('grep "TOT_A =" %s -A 2'%depfileNew).readlines()[2].strip().split() #TOT_A in itself matches TOT_ADENS, that is why we need "" around it
        TOTHs=os.popen('grep TOT_H %s -A 2'%depfileNew).readlines()[2].strip().split()
        depfileOld=depfileNew
    else:
        depfileOld=depfileNew
    ####
    inv=readInventory(x[-1])                        #extract inventory from the outputfile
    idx=int(x[-1][x[-1].find('bumat')+5:])          #get an index, since we want to know which value from the list to take
    totsf=TOTSFs[idx]
    totgsrc=TOTGSRCs[idx]
    tota=TOTAs[idx]
    toth=TOTHs[idx]
    #we make a big string for the entry, storing all the columns
    newentry=x[0]+','+x[1]+','+x[2]+','+x[3]+','+x[4]+','+totsf+','+totgsrc+','+tota+','+toth
    for nucli in nuclidesDict.keys():
        newentry=newentry+',%s'%(inv[nucli])
    newentry=newentry+'\n'
    #entry is created, so we append
    f = open(dataFrame,'a')
    f.write(newentry)
    f.close()
    
    #and we print just to see where is the process at.
    if int(x[0])%1000==0:
        print(x[0])
