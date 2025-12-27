# fast-correlation-tensorflow
fast correlation using optimized numpy einsum (CPU) and tensorflow (GPU)

1.  Implements correlation using numpy einsum function (optimized for matrix operations - multiplications, determinant, etc). 
2.  Uses latest numpy einsum function with 'optimize=True' option to further speed it up. Much faster than before.
3.  Implements the same function using tensorflow. tensorflow using GPU (NVIDIA 1080 TI) is actually slower than numpy version. Also
    tensor creation has additonal overhead which makes numpy version better suited for applications which require performing correlation
    operation data read from the disk iteratively. 
    
 
USAGE:

python -i fast-correlation-tensorflow.py

Main File:
          fast-correlation-tensorflow.py

Input Files:
          1.  powerModel_10K.npz - hypothetical power model file. can be assumed as any 2D matrix
          2.  P_10K.npz - measured power, can be assumed as another 2D matrix which is correlated (column-wise) with the powerModel
          
          
          
