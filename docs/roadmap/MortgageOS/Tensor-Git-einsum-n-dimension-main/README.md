
### ✅ Summary of Expected Outputs: `einsum_adv.py`

| Example | Operation             | Output Shape/Value    | Notes                     |
|---------|-----------------------|------------------------|---------------------------|
| 1       | Dot product            | `140`                  | Scalar result             |
| 2       | Outer product          | `(2, 3)`               | `[[10, 20, 30], [20, 40, 60]]` |
| 3       | Sum over all           | `276`                  | Total sum of all elements |
| 4       | Sum over axis `j`      | `(2, 4)`               | Sums along middle axis    |
| 5       | Bilinear form          | `78`                   | Result of xᵀ M y          |
| 6       | Attention              | `(2, 4, 5, 6)`         | (batch, heads, queries, keys) |
| 7       | Elastic energy         | `1.8`                  | ∑ σ_ij × ε_ij              |
| 8       | Batched outer product  | `(2, 3, 4)`            | One 3×4 matrix per batch  |
| 9       | Tensor contraction     | `(2, 4, 6)`            | Contracts over shared dims |

### Reference

1. [Stackoverflow: Understanding NumPy's einsum](https://stackoverflow.com/questions/26089893/understanding-numpys-einsum)
1. [Einsum is all you need](https://rockt.ai/2018/04/30/einsum)
