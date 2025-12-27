import numpy as np

# -------------------------------
# 1. Dot Product: i,i-> (scalar)
# -------------------------------
# a_i · b_i = ∑_i (a_i * b_i)
a = np.array([1, 2, 3])      # Shape: (i,)
b = np.array([10, 20, 30])   # Shape: (i,)

dot = np.einsum('i,i->', a, b)
print("1. Dot Product (i,i->):", dot)
# 1*10 + 2*20 + 3*30 = 10 + 40 + 90 = 140

# -------------------------------
# 2. Outer Product: i,j->ij
# -------------------------------
# a_i * b_j = 2D matrix of all combinations
a = np.array([1, 2])         # Shape: (i,)
b = np.array([10, 20, 30])   # Shape: (j,)

outer = np.einsum('i,j->ij', a, b)
print("\n2. Outer Product (i,j->ij):\n", outer)
# [[1*10, 1*20, 1*30],
#  [2*10, 2*20, 2*30]] = [[10, 20, 30], [20, 40, 60]]

# -------------------------------
# 3. Sum All Elements: ijk->
# -------------------------------
T = np.arange(2 * 3 * 4).reshape(2, 3, 4)  # Shape: (i, j, k)
total = np.einsum('ijk->', T)
print("\n3. Total Sum (ijk->):", total)
# Sum of numbers from 0 to 23 = (23 * 24) / 2 = 276

# -------------------------------
# 4. Sum Over One Axis: ijk->ik
# -------------------------------
sum_over_j = np.einsum('ijk->ik', T)
print("\n4. Sum over j (ijk->ik):\n", sum_over_j)
# Shape: (2, 4)
# For each i, sum across j (axis 1):
# E.g., T[0,:,0] = [0, 4, 8] → sum = 12

# -------------------------------
# 5. Bilinear Form: i,ij,j-> (scalar)
# -------------------------------
x = np.array([1, 2, 3])       # Shape: (i,)
M = np.array([[1, 0, 0],      # Shape: (i, j)
              [0, 2, 0],
              [0, 0, 3]])
y = np.array([4, 5, 6])       # Shape: (j,)

bilinear = np.einsum('i,ij,j->', x, M, y)
print("\n5. Bilinear Form (i,ij,j->):", bilinear)
# xᵀ M y = 1*1*4 + 2*2*5 + 3*3*6 = 4 + 20 + 54 = 78

# -------------------------------
# 6. Attention Scores: bhqd,bhkd->bhqk
# -------------------------------
Q = np.random.rand(2, 4, 5, 8)   # Shape: (batch=2, heads=4, queries=5, depth=8)
K = np.random.rand(2, 4, 6, 8)   # Shape: (batch=2, heads=4, keys=6, depth=8)

attn_scores = np.einsum('bhqd,bhkd->bhqk', Q, K)
print("\n6. Attention Scores (bhqd,bhkd->bhqk):", attn_scores.shape)
# Output shape: (2, 4, 5, 6)
# For each batch and head: compute dot product of query vs. key (across depth)

# -------------------------------
# 7. Elastic Energy: ij,ij-> (scalar)
# -------------------------------
sigma = np.array([[1, 2],
                  [2, 3]])       # Stress tensor (i, j)
epsilon = np.array([[0.1, 0.2],
                    [0.2, 0.3]]) # Strain tensor (i, j)

energy = np.einsum('ij,ij->', sigma, epsilon)
print("\n7. Elastic Energy (ij,ij->):", energy)
# = 1*0.1 + 2*0.2 + 2*0.2 + 3*0.3 = 0.1 + 0.4 + 0.4 + 0.9 = 1.8

# -------------------------------
# 8. Batched Outer Product: bi,bj->bij
# -------------------------------
A = np.array([[1, 2, 3],
              [4, 5, 6]])     # Shape: (batch=2, i=3)

B = np.array([[10, 20, 30, 40],
              [50, 60, 70, 80]])  # Shape: (batch=2, j=4)

batched_outer = np.einsum('bi,bj->bij', A, B)
print("\n8. Batched Outer Product (bi,bj->bij):", batched_outer.shape)
# Output shape: (2, 3, 4)
# For each batch:
# [1,2,3] ⊗ [10,20,30,40] = 3x4 matrix
# [4,5,6] ⊗ [50,60,70,80] = 3x4 matrix
print(batched_outer[0])  # First batch outer product
print(batched_outer[1])  # Second batch outer product

# -------------------------------
# 9. Tensor Contraction: abcd,bde->ace
# -------------------------------
A = np.random.rand(2, 3, 4, 5)  # Shape: (a=2, b=3, c=4, d=5)
B = np.random.rand(3, 5, 6)     # Shape: (b=3, d=5, e=6)

contracted = np.einsum('abcd,bde->ace', A, B)
print("\n9. Tensor Contraction (abcd,bde->ace):", contracted.shape)
# Output shape: (2, 4, 6)
# Contracting over shared indices: b and d
