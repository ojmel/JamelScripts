import math

import numpy as np
file=open('pangplddt.txt',"r")
file2=open('rbdpermuteplddt.txt',"r")
Score1=file.readlines()
Score2=file2.readlines()
PercentError=np.zeros((len(Score1),2))

print(Score1[1])
Lengthofover10=0
for i in range(len(Score1)):
    PercentError[i,0]=((math.fabs(float(Score1[i])-float(Score2[i])))/float(Score1[i]))*100
    PercentError[i,1]=int(i+1)
    if PercentError[i,0]>10:
        Lengthofover10+=1
print(Lengthofover10)
PercentErrorover10=np.zeros((Lengthofover10,2))
i=0
j=0
for j in range(len(Score1)):
    if PercentError[j,0]>10:
        PercentErrorover10[i,0]=PercentError[j,0]
        PercentErrorover10[i, 1] = PercentError[j, 1]
        i+=1
#print(PercentError)
print(PercentErrorover10)
