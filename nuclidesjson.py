#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get nuclide IDs for all Jeff 3.1

Zsolt Elter 2019
"""

import json

jeff=open('jeff31.xsdata').readlines()

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

tracked=list(readInventory('sample.bumat').keys())

nuclides={}

for i,line in enumerate(jeff):
    if i%2==1:
        x=line.strip().split()
        isoname=x[0][:-4].replace('-','')
        isozaid=x[1][:-4]
        if isozaid not in  nuclides and isozaid in tracked:
            nuclides[isozaid]=isoname

with  open ('nuclides.json','w') as outfile:
    json.dump(nuclides, outfile, indent =4)

