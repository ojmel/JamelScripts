import pandas as pd
tcga=pd.read_csv('tcga_hpv_feature_matrix.csv')
# center points on origin
# make lines intersecting origin and find largest distance of projections for all points
# square and sum
#components of eigenvector for pc1 is loading score
#average ofsum of squares is eigenvalue or variation
#pc2 is perpendicular to pc1