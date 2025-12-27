import numpy as np
from itertools import product
from functools import reduce

def my_einsum(expr, *inputs):
    """
    A scratch implementation of numpy.einsum.
    The sample code is adapted from:
    https://stackoverflow.com/questions/42869495/how-to-implement-numpyeinsum 
    """
    # Subscripts processing: split expression into query and result parts
    qry_expr, res_expr = expr.split('->')
    # Split query into individual input subscripts
    inputs_expr = qry_expr.split(',')
    
    # Find unique keys (labels) and their sizes from input arrays
    # Each label must have consistent size across all inputs where it appears
    keys = []
    seen_labels = {}
    for keys_str, input_arr in zip(inputs_expr, inputs):
        for key, size in zip(keys_str, input_arr.shape):
            if key in seen_labels:
                # Check size consistency
                if seen_labels[key] != size:
                    raise ValueError(f"size mismatch for label {key}")
            else:
                seen_labels[key] = size
                keys.append((key, size))
    
    # Get the associated sizes dict (used to initialize output array)
    sizes = dict(keys)
    
    # Create list of keys in order they were discovered
    to_key = [k for k, _ in keys]
    
    # Construct ranges for each label (used to create domain of iteration)
    ranges = [range(size) for _, size in keys]
    
    # Compute cartesian product of ranges - this is our domain of iteration
    domain = product(*ranges)
    
    # Initialize output tensor with shape determined by result expression
    res = np.zeros([sizes[key] for key in res_expr])
    
    # Loop over domain - each iteration represents one point in label space
    for indices in domain:
        # Create mapping: each label -> its current index value
        vals = dict(zip(to_key, indices))
        
        # Compute output array coordinates using result expression
        res_ind = tuple([vals[key] for key in res_expr])
        
        # Compute input array coordinates for each input
        inputs_ind = [tuple([vals[key] for key in expr]) for expr in inputs_expr]
        
        # Multiply all contributing components and accumulate to output
        prod = reduce(lambda x, y: x * y, [M[i] for M, i in zip(inputs, inputs_ind)])
        res[res_ind] += prod
    
    return res

if __name__ == "__main__":
    # Sample inputs/tests
    A = np.array([[1,4,1,7],
                [8,1,2,2],
                [7,4,3,4]])
    B = np.array([[2,5],
                [0,1],
                [5,7],
                [9,2]])

    print("my_einsum ij,jk->ki:\n", my_einsum('ij,jk->ki', A, B))
    print("numpy einsum  ij,jk->ki:\n", np.einsum('ij,jk->ki', A, B))

    v = np.array([2,3,5])
    M = np.array([[1,2,3],
                [4,5,6]])
    print("my_einsum ij,j->i (row-weighted sum):", my_einsum('ij,j->i', M, v))
    print("numpy  ij,j->i:", np.einsum('ij,j->i', M, v))

    x = np.array([7,11,13])
    y = np.array([3,2,5])
    print("my_einsum i,i-> :", my_einsum('i,i->', x, y))
    print("numpy i,i-> :", np.einsum('i,i->', x, y))

    # Additional test samples from StackOverflow

    # Trace (sum of diagonal)
    C = np.arange(9).reshape(3, 3)
    print("\nTrace ii->:")
    print("my_einsum:", my_einsum('ii->', C))
    print("numpy:", np.einsum('ii->', C))

    # Column sum
    print("\nColumn sum ij->j:")
    print("my_einsum:", my_einsum('ij->j', C))
    print("numpy:", np.einsum('ij->j', C))

    # Row sum
    print("\nRow sum ij->i:")
    print("my_einsum:", my_einsum('ij->i', C))
    print("numpy:", np.einsum('ij->i', C))

    # Matrix-vector multiplication
    print("\nMatrix-vector ij,j->i:")
    print("my_einsum:", my_einsum('ij,j->i', C, np.array([1, 2, 3])))
    print("numpy:", np.einsum('ij,j->i', C, np.array([1, 2, 3])))

    # Outer product
    a = np.array([1, 2, 3])
    b = np.array([4, 5])
    print("\nOuter product i,j->ij:")
    print("my_einsum:\n", my_einsum('i,j->ij', a, b))
    print("numpy:\n", np.einsum('i,j->ij', a, b))

    # Batch matrix multiplication
    D = np.random.rand(2, 3, 4)
    E = np.random.rand(2, 4, 5)
    print("\nBatch matmul ijk,ikl->ijl shape:")
    print("my_einsum:", my_einsum('ijk,ikl->ijl', D, E).shape)
    print("numpy:", np.einsum('ijk,ikl->ijl', D, E).shape)

    # Transpose
    print("\nTranspose ij->ji:")
    print("my_einsum:\n", my_einsum('ij->ji', C))
    print("numpy:\n", np.einsum('ij->ji', C))
