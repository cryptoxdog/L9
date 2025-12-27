import numpy as np

# ========== 2D ==========
# A: (2, 3), B: (3, 2)
# Indices:
#   i = row of A
#   k = column of A = row of B (contracted)
#   j = column of B
A2 = np.array([
    [1, 2, 3],
    [4, 5, 6]
])  # Shape (i=2, k=3)

B2 = np.array([
    [10, 11],
    [20, 21],
    [30, 31]
])  # Shape (k=3, j=2)

C2 = np.einsum('ik,kj->ij', A2, B2)
print("2D Result (i,k x k,j → i,j):\n", C2)

# ========== 3D ==========
# A: (2, 2, 3), B: (2, 3, 2)
# Indices:
#   b = batch
#   i = row of A
#   k = shared dim (contracted)
#   j = column of B
A3 = np.array([
    [[1, 2, 3],
     [4, 5, 6]],

    [[7, 8, 9],
     [10, 11, 12]]
])  # Shape (b=2, i=2, k=3)

B3 = np.array([
    [[10, 11],
     [12, 13],
     [14, 15]],

    [[16, 17],
     [18, 19],
     [20, 21]]
])  # Shape (b=2, k=3, j=2)

C3 = np.einsum('bik,bkj->bij', A3, B3)
print("\n3D Result (b,i,k x b,k,j → b,i,j):\n", C3)

# ========== 4D ==========
# A: (2, 1, 2, 3), B: (2, 1, 3, 2)
# Indices:
#   b = batch
#   a = extra batch dim (e.g., group)
#   i, j = row/col as before
#   k = contraction axis
A4 = A3.reshape(2, 1, 2, 3)  # (b=2, a=1, i=2, k=3)
B4 = B3.reshape(2, 1, 3, 2)  # (b=2, a=1, k=3, j=2)

C4 = np.einsum('baik,bakj->baij', A4, B4)
print("\n4D Result (b,a,i,k x b,a,k,j → b,a,i,j):\n", C4)

# ========== 5D ==========
# A: (2, 1, 1, 2, 3), B: (2, 1, 1, 3, 2)
# Indices:
#   b = batch
#   a, c = extra grouping dims
#   i = row
#   j = col
#   k = contraction
A5 = A3.reshape(2, 1, 1, 2, 3)  # (b=2, a=1, c=1, i=2, k=3)
B5 = B3.reshape(2, 1, 1, 3, 2)  # (b=2, a=1, c=1, k=3, j=2)

C5 = np.einsum('bacik,backj->bacij', A5, B5)
print("\n5D Result (b,a,c,i,k x b,a,c,k,j → b,a,c,i,j):\n", C5)

# ========== 6D ==========
# A: (2, 1, 1, 1, 2, 3), B: (2, 1, 1, 1, 3, 2)
# Indices:
#   b = batch
#   a, c, d = extra group dimensions
#   i = row, j = col
#   k = contraction axis
A6 = A3.reshape(2, 1, 1, 1, 2, 3)  # (b=2, a=1, c=1, d=1, i=2, k=3)
B6 = B3.reshape(2, 1, 1, 1, 3, 2)  # (b=2, a=1, c=1, d=1, k=3, j=2)

C6 = np.einsum('bacdik,bacdkj->bacdij', A6, B6)
print("\n6D Result (b,a,c,d,i,k x b,a,c,d,k,j → b,a,c,d,i,j):\n", C6)
