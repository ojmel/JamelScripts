import numpy as np
import turtle

Alpha_Num=np.zeros(16, dtype=object)
i=0

for i in range(9):
  Alpha_Num[i+1]+=i+1
import string
i=0
for i in range(6):
  Alpha_Num[i+10]=string.ascii_lowercase[i]
  i+=1
i=0

rng=np.random.default_rng()
Hexcode=rng.choice(Alpha_Num,size=6,shuffle=False)
screen=turtle.getscreen()
pen=turtle.Turtle()
Numberofcircles=30
FinalHexcode=np.empty((Numberofcircles), dtype=object)
j=-1
i=0
for i in range(Numberofcircles):
    FinalHexcode[i]='#'
i=0
for i in range(Numberofcircles):
    Hexcode = rng.choice(Alpha_Num, size=6, shuffle=False)
    j+=1
    print(Hexcode)
    for i in range(6):

        FinalHexcode[j]+=str(Hexcode[i])
        i+=1
j=0
for i in range(Numberofcircles):
    pen.color(str(FinalHexcode[i]))
    pen.pensize(2)
    pen.circle(20+j)
    j+=5