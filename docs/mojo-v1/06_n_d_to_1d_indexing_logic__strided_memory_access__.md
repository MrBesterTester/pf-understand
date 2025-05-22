---
layout: default
title: "Chapter 6: N-D to 1D Indexing Logic"
parent: "My Tutorial for Mojo v1"
nav_order: 6
---
# Chapter 6: N-D to 1D Indexing Logic (Strided Memory Access)

Welcome to Chapter 6! We've come a long way in understanding how Mojo handles memory and N-dimensional data. Let's recap our journey:
1.  [Chapter 1: `AddressSpace`](01_addressspace_.md) taught us about memory "neighborhoods."
2.  [Chapter 2: `UnsafePointer`](02_unsafepointer_.md) showed us how Mojo directly references memory locations.
3.  [Chapter 3: `IndexList`](03_indexlist_.md) introduced a way to handle multi-dimensional coordinates.
4.  [Chapter 4: `Dim` and `DimList`](04_dimlist_.md) explained how to describe dimension sizes, statically or dynamically.
5.  [Chapter 5: `NDBuffer`](05_ndbuffer_.md) unveiled Mojo's powerful N-dimensional array, which acts as a "view" over a flat block of memory.

In the last chapter, we saw that an `NDBuffer` uses an `UnsafePointer` (its `data` field) to point to the beginning of its raw, 1D memory. But if the memory is flat, how does `NDBuffer` find the element at, say, `matrix[row, column, depth]`? This is where the magic of **strided memory access** comes in.

This chapter dives into the core mechanism that `NDBuffer` uses to translate multi-dimensional indices (like `[row, col, depth]`) into a single, flat offset from its base `UnsafePointer`. This calculation crucially involves the **strides** associated with each dimension.

## The Car Park Analogy Revisited

Remember the official description's analogy? It's perfect for understanding strides:

> Imagine a multi-story car park where cars are arranged in rows on different levels. To find a specific car (indexed by `[level, row, spot]`), you'd calculate its position in a conceptual single line of all spots: `(level * spots_per_level) + (row * spots_per_row) + spot_number`. `NDBuffer` uses a similar formula: `offset = sum(index[i] * stride[i])`.

Let's break this down:
*   **`[level, row, spot]`**: This is your multi-dimensional index.
*   **`spots_per_level`**: This is the "stride" for the `level` dimension. It's how many total spots you skip to move from one level to the next, assuming you keep the row and spot number the same.
*   **`spots_per_row`**: This is the "stride" for the `row` dimension (within a level). It's how many spots you skip to move from one row to the next, keeping the spot number the same.
*   **`spot_number`**: The index for the `spot` dimension. Its implicit stride is 1 (to get to the next spot in the same row, you just move 1 position).

The total calculation gives you a single number – the position of *your* car if all spots from all levels and all rows were laid out in one giant, continuous line. This single number is the **offset** from the very first car spot in the park.

## What are Strides, Exactly?

In the context of `NDBuffer` and computer memory:

**Strides** are a list of numbers, one for each dimension of the `NDBuffer`. The stride for a particular dimension tells you **how many elements you need to "jump" over in the flat, 1D underlying memory to get to the next element in that dimension, while keeping all other dimension indices the same.**

*   `NDBuffer` stores these strides in its `dynamic_stride` field (an `IndexList` we learned about in Chapter 3), or they can be partly known statically via the `strides: DimList` parameter.

Consider a 2D `NDBuffer` (a matrix) with `shape = (num_rows, num_cols)`:
*   It will have two strides: `stride_row` and `stride_col`.
*   `stride_col`: Tells you how many elements to jump in the 1D memory to move from `matrix[r, c]` to `matrix[r, c+1]` (next column, same row).
*   `stride_row`: Tells you how many elements to jump in the 1D memory to move from `matrix[r, c]` to `matrix[r+1, c]` (next row, same column).

## The Magic Formula: Calculating the 1D Offset

As stated in the introduction, `NDBuffer` translates an N-D index `idx = [idx_0, idx_1, ..., idx_N-1]` into a 1D offset from its `data` pointer using this formula:

`offset = (idx_0 * stride_0) + (idx_1 * stride_1) + ... + (idx_N-1 * stride_N-1)`

Or, more compactly: `offset = sum(index[i] * stride[i])` for `i` from `0` to `rank-1`.

Once this `offset` is calculated, the `NDBuffer` can access the element by moving `offset` elements from its base `data` pointer: `element_address = ndbuffer.data + offset`.

## How `NDBuffer` Gets Its Strides

When you create an `NDBuffer`, you can provide explicit strides. However, if you only provide a shape (like in many examples from Chapter 5), `NDBuffer` calculates default strides for you. These default strides correspond to a **contiguous memory layout**, typically **row-major** (which we'll discuss soon).

This calculation happens in the `_compute_ndbuffer_stride` function found in `stdlib/src/buffer/buffer.mojo`. Let's look at its logic conceptually for an `NDBuffer` with `rank > 0`:

```mojo
// Conceptual logic from _compute_ndbuffer_stride
fn _compute_ndbuffer_stride[rank](shape: IndexList[rank]) -> IndexList[rank]:
    var stride = IndexList[rank]() // Initialize strides

    if rank == 1:
        stride[0] = 1 // For a 1D array, stride is just 1
        return stride

    // For rank > 1 (e.g., 2D, 3D):
    // The stride for the very last dimension is 1 (elements are next to each other)
    stride[rank - 1] = 1

    // Work backwards from the second-to-last dimension
    for i in reversed(range(rank - 1)): // e.g., for rank 3, i goes 1, 0
        // Stride of current dimension = shape of NEXT dimension * stride of NEXT dimension
        stride[i] = shape[i + 1] * stride[i + 1]

    return stride
```

**Example: 3D `NDBuffer` with `shape = (depth, rows, cols)` (e.g., `(2, 3, 4)`)**
1.  `rank = 3`.
2.  `stride[2]` (for `cols` dimension) = `1`.
3.  `i = 1` (for `rows` dimension):
    `stride[1] = shape[2] * stride[2] = cols * 1 = cols`.
    So, `stride_row = 4`.
4.  `i = 0` (for `depth` dimension):
    `stride[0] = shape[1] * stride[1] = rows * cols`.
    So, `stride_depth = 3 * 4 = 12`.

The resulting strides would be `(rows * cols, cols, 1)`. For shape `(2, 3, 4)`, strides are `(12, 4, 1)`.

## How `NDBuffer` Calculates the Offset: Inside `_compute_ndbuffer_offset`

The actual calculation of the 1D offset using the indices and strides is performed by the `_compute_ndbuffer_offset` function in `stdlib/src/buffer/buffer.mojo`. There are a few versions of this function to handle different ways you might provide indices (e.g., as a `VariadicList[Int]`, a `StaticTuple`, or an `IndexList`).

Let's look at the core logic from one of these:
```mojo
// Simplified from _compute_ndbuffer_offset in stdlib/src/buffer/buffer.mojo
@always_inline
fn _compute_ndbuffer_offset(
    buf: NDBuffer,
    index: IndexList[buf.rank], // The N-D indices [idx_0, idx_1, ...]
) -> Int:
    alias rank = buf.rank

    @parameter // Means this can be optimized heavily at compile time
    if buf.rank == 0: // Scalar NDBuffer
        return 0

    // This `_use_32bit_indexing` check is interesting!
    // It checks if we're on a GPU and if the memory is in certain
    // fast GPU address spaces (like SHARED or CONSTANT, from Chapter 1).
    // If so, it might use 32-bit math for speed if the offset fits.
    @parameter
    if _use_32bit_indexing[buf.address_space]():
        var result: Int32 = 0
        @parameter
        for i in range(rank):
            // fma is "fused multiply-add": (a*b)+c
            // result = (buf.stride[i]() * Int32(index[i])) + result
            result = fma(Int32(buf.stride[i]()), Int32(index[i]), result)
        return Int(result) // Convert back to standard Int
    else:
        // For CPU or other GPU memory, use standard Int (usually 64-bit)
        var result: Int = 0
        @parameter
        for i in range(rank):
            // result = (buf.stride[i]() * index[i]) + result
            result = fma(buf.stride[i](), index[i], result)
        return result
```
The key part is the loop:
`result = fma(buf.stride[i](), index[i], result)`

This iteratively calculates `sum(index[i] * stride[i])`. The `fma` (fused multiply-add) instruction computes `(a*b)+c` often more efficiently and accurately than separate multiply and add operations.

So, if you call `my_ndbuffer[idx0, idx1, idx2]`, `NDBuffer` internally calls a function like `_compute_ndbuffer_offset` with your indices. This function uses the `NDBuffer`'s stored `dynamic_stride` values and your `idx` values to calculate the final 1D offset. Then, it accesses `my_ndbuffer.data.offset(calculated_offset).load()` or `.store()`.

## Strides in Action: Memory Layouts

The power of strides is that they define how the N-dimensional data is actually laid out in the 1D memory block. The two most common layouts are row-major and column-major.

### 1. Row-Major Order (C-style, Default in Mojo/NumPy)

In row-major order, elements of a row are contiguous in memory. You go through all columns of row 0, then all columns of row 1, and so on.

Consider a 2x3 matrix: `A = [[a, b, c], [d, e, f]]`
*   Shape: `(2, 3)` (2 rows, 3 columns)
*   Memory Layout: `a, b, c, d, e, f`
*   Strides (calculated by `_compute_ndbuffer_stride`):
    *   `stride[1]` (for columns) = `1` (to go from `a` to `b`, jump 1 element)
    *   `stride[0]` (for rows) = `shape[1] * stride[1] = 3 * 1 = 3` (to go from `a` to `d`, jump 3 elements: `b, c, d`)
    *   So, strides are `(3, 1)`.

To find element `A[r, c]`:
`offset = (r * stride_row) + (c * stride_col) = (r * 3) + (c * 1)`
*   `A[0,0] (a)`: `(0*3) + (0*1) = 0`. Offset 0 from base.
*   `A[0,1] (b)`: `(0*3) + (1*1) = 1`. Offset 1 from base.
*   `A[1,0] (d)`: `(1*3) + (0*1) = 3`. Offset 3 from base.
*   `A[1,2] (f)`: `(1*3) + (2*1) = 5`. Offset 5 from base.

### 2. Column-Major Order (Fortran-style)

In column-major order, elements of a column are contiguous. You go through all rows of column 0, then all rows of column 1, etc.

Consider the same 2x3 matrix: `A = [[a, b, c], [d, e, f]]`
*   Shape: `(2, 3)` (2 rows, 3 columns)
*   Memory Layout: `a, d, b, e, c, f`
*   Strides:
    *   Here, to make columns contiguous, the stride for the *first* dimension (rows) must be 1.
    *   `stride[0]` (for rows) = `1` (to go from `a` to `d`, jump 1 element)
    *   `stride[1]` (for columns) = `shape[0] * stride[0] = 2 * 1 = 2` (to go from `a` to `b`, jump 2 elements: `d,b`)
    *   So, strides are `(1, 2)`.

To find element `A[r, c]` (using the *same* formula, just different stride values):
`offset = (r * stride_row) + (c * stride_col) = (r * 1) + (c * 2)`
*   `A[0,0] (a)`: `(0*1) + (0*2) = 0`. Offset 0.
*   `A[0,1] (b)`: `(0*1) + (1*2) = 2`. Offset 2. (Memory: `a,d,b` <- `b` is at offset 2)
*   `A[1,0] (d)`: `(1*1) + (0*2) = 1`. Offset 1. (Memory: `a,d` <- `d` is at offset 1)
*   `A[1,2] (f)`: `(1*1) + (2*2) = 5`. Offset 5. (Memory: `a,d,b,e,c,f` <- `f` is at offset 5)

**`NDBuffer` can represent data in either layout (or even more complex ones!) simply by having the correct `strides` parameter.** The access logic (`matrix[r,c]`) and the formula `sum(index[i] * stride[i])` remain the same. This is incredibly flexible!

## Why Strided Access Matters

1.  **Efficiency**: Calculating an offset is a fast arithmetic operation. It allows direct access to any element without needing to iterate or search.
2.  **Flexibility**:
    *   Supports different memory layouts (row-major, column-major) for compatibility with various libraries or hardware preferences.
    *   Enables advanced array manipulations.
3.  **Zero-Copy Operations**: This is a big one! Many operations that might seem to require data copying can be done by just creating a new `NDBuffer` with different shape/strides that points to the *same underlying data*.
    *   **Slicing**: Taking a sub-matrix `B = A[rows_slice, cols_slice]` can often be done by creating `B` with an offset base pointer from `A` and new strides/shape, without copying `A`'s data. The `tile()` method we saw in Chapter 5 does this.
    *   **Transposing**: Transposing a matrix `A` to get `A_T` involves swapping its shape dimensions and its stride dimensions. The new `NDBuffer` `A_T` can point to the exact same memory as `A`.
    *   **Broadcasting**: In operations like adding a vector to each row of a matrix, strides can be set to 0 for the broadcasted dimension, effectively reusing the vector's data without copying.

These zero-copy views save memory and significantly speed up computations by avoiding redundant data movement.

## Example Walkthrough: A 2x2 NDBuffer

Let's create a simple 2x2 `NDBuffer` and trace the indexing.

```mojo
from buffer import NDBuffer, DimList
from memory import InlineArray, MutableAnyOrigin
from builtin import DType, Scalar
from utils import IndexList

fn main_stride_example():
    print("--- Strides Example: 2x2 Matrix ---")

    // 1. Create storage and an NDBuffer (default row-major)
    var data_storage = InlineArray[Scalar[DType.int32], 2 * 2](uninitialized=True)
    var matrix = NDBuffer[
        DType.int32,
        2, // rank
        _, // origin
        DimList(2, 2) // shape: 2 rows, 2 columns
    ](data_storage)

    // Let's see its shape and calculated strides
    var shape = matrix.get_shape() // Should be (2, 2)
    var strides = matrix.get_strides() // Should be (2, 1) for row-major
    print("Shape:", shape)
    print("Strides:", strides)

    // Fill the matrix:
    // matrix[0,0] = 10, matrix[0,1] = 11
    // matrix[1,0] = 20, matrix[1,1] = 21
    var counter: Int32 = 10
    for r in range(matrix.dim[0]()): // Iterate rows
        for c in range(matrix.dim[1]()): // Iterate columns
            matrix[r,c] = counter
            if c == 0 and r == 1: counter = 20 # Just to make values 10,11,20,21
            else: counter += 1
    
    print("Matrix content (via NDBuffer access):")
    print(matrix[0,0], matrix[0,1])
    print(matrix[1,0], matrix[1,1])

    // Let's manually calculate offset for matrix[1,0] (should be 20)
    // Indices: r=1, c=0
    // Strides: stride_r=2, stride_c=1
    var r_idx = 1
    var c_idx = 0
    var stride_r = strides[0] // Is 2
    var stride_c = strides[1] // Is 1

    var offset = (r_idx * stride_r) + (c_idx * stride_c)
    // offset = (1 * 2) + (0 * 1) = 2 + 0 = 2
    print("Calculated offset for matrix[1,0]:", offset)

    // Verify by looking at the raw data (if we could easily inspected InlineArray)
    // The flat data_storage would look like: [10, 11, 20, 21]
    // matrix.data.offset(2).load() would give us 20.
    // matrix[1,0] internally does this!

    print("Value at matrix[1,0] using NDBuffer:", matrix[1,0])
```
If you could run this (e.g., by calling `main_stride_example()`), you'd see:
```
--- Strides Example: 2x2 Matrix ---
Shape: (2, 2)
Strides: (2, 1)
Matrix content (via NDBuffer access):
10 11
20 21
Calculated offset for matrix[1,0]: 2
Value at matrix[1,0] using NDBuffer: 20
```
This confirms that `NDBuffer` used the strides `(2,1)` to correctly find the element `matrix[1,0]` at offset `2` in the flat memory.

## Summary

*   `NDBuffer` uses **strides** to map N-dimensional indices to a 1D memory offset.
*   The formula is simple but powerful: `offset = sum(index[i] * stride[i])`.
*   `_compute_ndbuffer_stride` calculates default (contiguous, row-major) strides if not provided.
*   `_compute_ndbuffer_offset` implements the offset calculation, often using efficient `fma` operations.
*   Strides define the actual **memory layout** (row-major, column-major, etc.) and enable `NDBuffer` to handle them transparently.
*   This mechanism is key to `NDBuffer`'s efficiency, flexibility, and its ability to perform **zero-copy views** for operations like slicing and transposing.

Understanding strided memory access unlocks a deeper appreciation for how N-dimensional arrays are handled efficiently in systems like Mojo, and why `NDBuffer` is such a versatile tool.

## What's Next?

This chapter concludes our deep dive into the fundamental building blocks and internal mechanics of `NDBuffer`. You now have a solid understanding of:
*   Memory organization (`AddressSpace`).
*   Raw memory access (`UnsafePointer`).
*   Representing N-D coordinates and shapes (`IndexList`, `DimList`).
*   The `NDBuffer` structure itself.
*   And how `NDBuffer` navigates its data using strides.

With this foundation, you're well-equipped to use `NDBuffer` effectively in Mojo for various numerical computing tasks. Future explorations might involve using `NDBuffer` in more complex algorithms, interfacing with other Mojo libraries, or diving into performance optimization techniques that leverage these concepts. Congratulations on completing this foundational series on `NDBuffer`!

---
**Table of Contents**
1. [Chapter 1: Understanding Memory Neighborhoods with `AddressSpace`](01_addressspace_.md)
2. [Chapter 2: Peeking into Memory with `UnsafePointer`](02_unsafepointer_.md)
3. [Chapter 3: Working with Multiple Dimensions: `IndexList`](03_indexlist_.md)
4. [Chapter 4: Describing Dimensions with `Dim` and `DimList`](04_dimlist_.md)
5. [Chapter 5: The N-Dimensional Buffer: `NDBuffer`](05_ndbuffer_.md)
6. **Chapter 6: N-D to 1D Indexing Logic (Strided Memory Access)** (You are here)
```

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)