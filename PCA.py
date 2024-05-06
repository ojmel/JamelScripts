import pandas as pd
import numpy as np
tcga=pd.read_csv('tcga_hpv_feature_matrix.csv')
# center points on origin
# make lines intersecting origin and find largest distance of projections for all points
# square and sum
#components of eigenvector for pc1 is loading score
#average ofsum of squares is eigenvalue or variation
#pc2 is perpendicular to
tcga=tcga.drop(columns=['patient','Unnamed: 0','hpv_status'])
tcga=np.array(tcga)
def covariance_matrix(matrix):
    matrix_mean=np.mean(matrix,axis=0)
    centered_matrix=matrix-matrix_mean
    squared_matrix=centered_matrix * centered_matrix
    variance_vector=np.sum(squared_matrix,axis=0)/centered_matrix.shape[0]
covariance_matrix(tcga)
