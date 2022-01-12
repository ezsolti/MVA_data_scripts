"""
Script to merge csv files

Zsolt Elter 2019
"""


import os
dataFrame='file_log_PWR_UOX-MOX.csv'
os.system('cp UOX/fuellog_strategicPWR_UOX.csv %s'%dataFrame)




csv=open('MOX/fuellog_strategicPWR_MOX.csv').readlines()
idnum=789406 #number to be changed if BIC range changes
             #or use a less lazy and more intelligent way to handle this:)

for line in csv[1:]:
    x=line.strip().split(',')
    
    newentry=str(idnum)+','+x[1]+','+x[2]+','+x[3]+','+x[4]+','+x[5]+','+x[6]+'\n'
    
    f = open(dataFrame,'a')
    f.write(newentry)
    f.close()
    idnum=idnum+1
    if int(idnum)%1000==0:
        print(x[0]) #printing just to see progress

        


