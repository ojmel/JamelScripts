import pandas as pd
import numpy as np
import sympy as sp


def create_covariance_matrix(matrix: np.array):
    matrix_mean = np.mean(matrix, axis=0)
    centered_matrix = matrix - matrix_mean
    covariance_matrix = np.dot(centered_matrix.T, centered_matrix) / (centered_matrix.shape[1] - 1)
    return covariance_matrix


def solve_eigen(matrix: np.array):
    lamb=sp.symbols('l')
    lamb_iden = lamb * np.identity(matrix.shape[0])
    determinant = lamb_iden - matrix
    top_row_temoved = np.delete(determinant, 0, 0)
    polynomial = []
    for column in range(determinant.shape[0]):
        scalar = determinant[0, column]
        two_by_two = np.delete(top_row_temoved, column, 1)
        component = scalar * (two_by_two[0, 0] * two_by_two[1, 1] - two_by_two[0, 1] * two_by_two[1, 0])
        if column % 2 != 0:
            polynomial.append(-component)
        else:
            polynomial.append(component)
    polynomial=sp.simplify(sum(polynomial))

    print(sp.solve(polynomial,lamb))
    print(np.linalg.eigvals(matrix))


def create_enumerated_matrix(height: int, width: int):
    matrix = np.array([range(y, y + width) for y in range(1, height * width, width)])
    return matrix


def main():
    tcga = pd.read_csv('tcga_hpv_feature_matrix.csv').drop(columns=['patient', 'Unnamed: 0', 'hpv_status'])
    # center points on origin
    # make lines intersecting origin and find largest distance of projections for all points
    # square and sum
    # components of eigenvector for pc1 is loading score
    # average ofsum of squares is eigenvalue or variation
    # pc2 is perpendicular to
    tcga = np.array(tcga)
    covar=create_covariance_matrix(tcga)
    solve_eigen(covar)


if __name__ == '__main__':
    main()
