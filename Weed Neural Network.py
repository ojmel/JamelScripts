
import numpy as np
from scipy.special import expit
import random

VotingData = np.genfromtxt("Trump Weed - Sheet1.csv", delimiter=",")

i=0
TrainingSize=20
hiddenlayernodes=4
input=VotingData[0:TrainingSize,(1,2,3)]
weights1= np.random.rand(input.shape[1],hiddenlayernodes)
weights2   = np.random.rand(hiddenlayernodes,1)
Answers=VotingData[0:TrainingSize,-1]
output= np.zeros((VotingData.shape))
layer1 = expit(np.dot(input, weights1))
output = expit(np.dot(layer1, weights2))
d_weights2 = np.dot((2*(Answers - output.T) * (output.T*(1-output.T))), layer1)
dC_da=np.dot(weights2, 2*(Answers - output.T) * ((output.T*(1-output.T))) )* (layer1.T*(1-layer1.T))
d_weights1 = np.dot(input.T, dC_da.T)

weights1 += d_weights1

weights2 += d_weights2.T
input=VotingData[0:,(1,2,3)]
y=VotingData[0:,-1]
output= np.zeros((1,51))
layer1 = expit(np.dot(input, weights1))
output = expit(np.dot(layer1, weights2))
print(y-output.T)
print(output)
