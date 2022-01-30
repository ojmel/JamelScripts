import numpy as np
import math
def RPKM(a,b):
    file1 = open(a, "r")
    f=file1.readlines()
    file2 = open(b, "r")
    g = file2.readlines()
    linenumber=0
    for line in f:
        linenumber+=1

    pca=np.empty((linenumber,4), dtype=object)
    i=0
    for line in f:
        x=line.split()
        pca[i,0]=x[0]

        if float(x[3])<=.05 and float(x[1])<0:
            pca[i,1]="down"
        elif float(x[3]) <= .05 and float(x[1]) > 0:
            pca[i, 1] = "up"
        i+=1
    i=0
    for line in g:
        y=line.split()
        i=0
        for line in f:
            if y[-1]==pca[i,0]:
                pca[i,2] = y[0]
                pca[i,3]=y[-2]
                break
            else:
                i+=1

    print(pca)
    np.savetxt("profile.csv", pca,delimiter="      ",fmt="%s,%s,%s,%s")
RPKM("etreads - etreads.tsv","peakannodht1 - peakannodht1 (1).tsv")