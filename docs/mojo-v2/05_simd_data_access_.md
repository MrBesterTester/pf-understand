# Chapter 5: Speeding Up with SIMD - Loading and Storing Data in Chunks

Welcome to Chapter 5! We've covered a lot about `NDBuffer`:
*   How it uses `UnsafePointer` to find its data's starting point ([Chapter 1](01_unsafepointer__as_used_by_ndbuffer__.md)).
*   How `Dim` and `DimList` define its shape ([Chapter 2](02_dimlist_and_dim_.md)).
*   The `NDBuffer` structure itself ([Chapter 3](03_ndbuffer_.md)).
*   How strides and offset computation help locate any single element ([Chapter 4](04_strides_and_offset_computation_.md)).

Now, we're going to explore how `NDBuffer` helps you work with data much faster by processing multiple elements at once. This is achieved through **SIMD** operations.

`NDBuffer` facilitates high-performance data access through SIMD (Single Instruction, Multiple Data) operations. Methods like `load[width=W]` and `store[width=W]` allow reading or writing `W` data elements (a "vector") at once, rather than one by one. This can significantly speed up computations. The module also provides `partial_simd_load` and `partial_simd_store` utility functions to handle situations where the memory access for a full SIMD vector would go out of bounds, allowing for safe vectorized processing of edge cases with padding or masking.

Think of SIMD access as using a wide tray to carry multiple teacups (data elements) at once between a shelf (memory) and a table (CPU registers), instead of carrying them individually. This is much faster. The `partial_` functions are like carefully using the tray when you're at the end of the shelf and only have a few cups left, or the shelf doesn't perfectly fit a full tray width, ensuring you don't drop any or pick up empty air.

## What is SIMD? (Single Instruction, Multiple Data)

Imagine you're a chef, and you have a dozen potatoes to peel.
*   **Scalar operation (one by one)**: You pick up one potato, peel it, put it down. Pick up the next, peel it, put it down. And so on for all twelve.
*   **SIMD operation (multiple at once)**: You have a special peeler that can handle, say, four potatoes simultaneously! You load four potatoes into your super-peeler, activate it once, and all four are peeled. You'd do this three times to peel all twelve.

SIMD works on a similar principle inside your computer's processor. Modern CPUs have special hardware units that can perform the same operation (like addition, multiplication, etc.) on multiple pieces of data *at the same time* with a single instruction. This "chunk" of data is often called a **SIMD vector**.

Using SIMD can lead to massive speedups in programs that process large amounts of data, like in scientific computing, graphics, machine learning, and image processing.

## Full Chunks: `NDBuffer.load[width=W]` and `NDBuffer.store[width=W]`

`NDBuffer` provides convenient methods to perform SIMD operations:
*   `load[width=W](index) -> SIMD[type, W]`: Reads `W` elements starting from the memory location corresponding to `index` in the `NDBuffer`. It returns these `W` elements as a `SIMD[type, W]` object.
*   `store[width=W](index, value: SIMD[type, W])`: Writes the `W` elements from the `SIMD` vector `value` to the `NDBuffer`, starting at the memory location corresponding to `index`.

Here, `W` is a parameter you specify, representing the number of data elements in your SIMD vector (e.g., 2, 4, 8, depending on the data type and CPU capabilities). `type` is the `DType` of the elements in your `NDBuffer`.

**How it Works (Simplified):**
1.  You call `my_ndbuffer.load[width=W](some_index)`.
2.  `NDBuffer` uses its magic (strides and the `_offset()` method we saw in Chapter 4) to calculate the precise 1D memory address for `some_index`. Let's call this `target_address_pointer`.
3.  It then effectively tells this `target_address_pointer` (which is an `UnsafePointer`): "Load `W` elements starting from here."
4.  The `UnsafePointer` performs the SIMD load from memory.
Storing works similarly but in reverse.

**An Important Condition: Contiguity!**
SIMD operations usually assume that the `W` elements you want to load or store are sitting right next to each other in memory (i.e., they are **contiguous**).
*   If you're working with a 1D `NDBuffer` (a simple array), its elements are typically contiguous.
*   For a 2D `NDBuffer` (matrix), if its elements are laid out row-by-row contiguously (row-major, stride of 1 for the last dimension), you can use SIMD to load/store parts of a row.

The `load` and `store` methods in `NDBuffer` actually check for this:
```mojo
// Inside NDBuffer's load method (simplified)
fn load[*, width: Int = 1, ...](self, idx: ...) -> SIMD[type, width]:
    debug_assert(
        self.is_contiguous() or width == 1, // This check is important!
        "Function requires contiguous buffer for width > 1.",
    )
    return self._offset(idx).load[width=width, alignment=alignment]()
```
If the `NDBuffer` isn't contiguous (meaning its innermost dimension's stride isn't 1) and you try a `width > 1` SIMD operation, the `debug_assert` will trigger (in debug builds) because the `W` elements at the calculated offset might not correspond to `W` logically adjacent elements in your N-D view. Scalar operations (`width=1`) are always fine.

**Example (Conceptual 1D `NDBuffer`):**
Let's say `my_buffer` is an `NDBuffer` of `Float32`s: `[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, ...]`
```mojo
from memory import DType
from simd import SIMD

// Assume my_buffer is an NDBuffer[True, DType.float32, 1, ...]
// and it's contiguous.

// Load 4 Float32s starting at index 0
let simd_vec: SIMD[DType.float32, 4] = my_buffer.load[width=4](0)
// simd_vec now holds [1.0, 2.0, 3.0, 4.0]

// Let's say we process it (e.g., add 10.0 to each element)
let processed_vec = simd_vec + SIMD[DType.float32, 4](10.0)
// processed_vec is now [11.0, 12.0, 13.0, 14.0]

// Store it back
my_buffer.store[width=4](0, processed_vec)
// my_buffer now starts with: [11.0, 12.0, 13.0, 14.0, 5.0, 6.0, ...]
```

## The "Edge" Problem: Handling Leftovers

The `load[width=W]` and `store[width=W]` methods are great when your data neatly aligns with the SIMD width. But what if your `NDBuffer` has, say, 10 elements, and your SIMD width `W` is 4?
*   You can process elements `0-3` with one SIMD operation.
*   You can process elements `4-7` with another SIMD operation.
*   But then you have elements `8-9` left over (only 2 elements).

If you try to do a `my_buffer.load[width=4](8)`, it will attempt to read 4 elements starting from index 8 (`my_buffer[8]`, `my_buffer[9]`, `my_buffer[10]`, `my_buffer[11]`). But `my_buffer[10]` and `my_buffer[11]` are out of bounds! This can lead to crashes or incorrect data. This is the "edge" problem.

## Safe Edges: `partial_simd_load` and `partial_simd_store`

Mojo's `buffer` module provides utility functions to handle these edge cases safely:
*   `partial_simd_load[type, width](storage_ptr, lbound, rbound, pad_value) -> SIMD[type, width]`
*   `partial_simd_store[type, width](storage_ptr, lbound, rbound, data_vec)`

These are **not** methods of `NDBuffer` itself. They are standalone functions that operate on an `UnsafePointer` (which you can get from an `NDBuffer`'s `data` field, appropriately offset).

*   `type`: The `DType` of the elements.
*   `width`: The SIMD vector width (e.g., 4).
*   `storage_ptr: UnsafePointer[Scalar[type], ... ]`: A pointer to the memory location where the data segment begins. For the "leftover" elements, this would be the pointer to the first leftover element.
*   `lbound: Int`: The starting index *within the SIMD vector* where valid data should come from memory. For loading N leftover elements, this is usually `0`.
*   `rbound: Int`: The ending index (exclusive) *within the SIMD vector* for valid data. For loading N leftover elements, this is `N`.
*   `pad_value: Scalar[type]` (for `partial_simd_load`): The value to use for elements in the SIMD vector that are outside the `[lbound, rbound)` range.
*   `data_vec: SIMD[type, width]` (for `partial_simd_store`): The SIMD vector containing data to be stored. Only elements within the `[lbound, rbound)` range will actually be written to memory.

**How they work:**
Internally, these functions use special CPU instructions called **masked loads and stores**. They create a "mask" (a sequence of true/false values, one for each lane of the SIMD vector).
*   `partial_simd_load`: For each lane `i` in the SIMD vector (from `0` to `width-1`):
    *   If `lbound <= i < rbound`, it loads `storage_ptr[i]` into lane `i` of the result.
    *   Otherwise, it fills lane `i` with `pad_value`.
*   `partial_simd_store`: For each lane `i`:
    *   If `lbound <= i < rbound`, it stores `data_vec[i]` into `storage_ptr[i]`.
    *   Otherwise, it does nothing for that memory location (`storage_ptr[i]` is not written to).

This ensures you only read from or write to valid memory locations, even if your data segment is smaller than the SIMD width.

**Example (Handling leftovers from our previous example):**
Suppose `my_buffer` has 10 `Float32` elements, and `width=4`. We've processed elements 0-7.
Leftovers are `my_buffer[8]` and `my_buffer[9]`. There are 2 leftover elements.

```mojo
from memory import UnsafePointer, DType
from simd import SIMD
from buffer import partial_simd_load, partial_simd_store

// Assume my_buffer: NDBuffer[..., DType.float32, ...] of length 10
let W: Int = 4 // SIMD width
let num_leftover: Int = 2
let pad_val: Float32 = 0.0

// Get a pointer to the first leftover element (my_buffer[8])
// In a real NDBuffer, you'd calculate offset for index 8.
// let ptr_to_leftovers = my_buffer.data.offset(my_buffer._offset_of_index(8))
// For simplicity, let's assume we have this UnsafePointer:
var ptr_to_leftovers: UnsafePointer[Float32] = ... ; // Points to my_buffer[8]

// Partial load
let leftover_vec_loaded = partial_simd_load[DType.float32, W](
    ptr_to_leftovers,
    0,                // lbound: valid data starts at SIMD lane 0
    num_leftover,     // rbound: valid data ends before SIMD lane 2 (i.e., lanes 0, 1 are valid)
    pad_val
)
// If my_buffer[8]=8.8, my_buffer[9]=9.9, then
// leftover_vec_loaded is [8.8, 9.9, 0.0, 0.0]

// Process it (e.g., add 10.0)
let processed_leftovers = leftover_vec_loaded + SIMD[DType.float32, W](10.0)
// processed_leftovers is now [18.8, 19.9, 10.0, 10.0]
// Note: We also "processed" the padded parts. This is often fine.

// Partial store
partial_simd_store[DType.float32, W](
    ptr_to_leftovers,
    0,
    num_leftover,
    processed_leftovers
)
// This will write:
// - processed_leftovers[0] (18.8) to ptr_to_leftovers[0] (my_buffer[8])
// - processed_leftovers[1] (19.9) to ptr_to_leftovers[1] (my_buffer[9])
// - It will NOT write processed_leftovers[2] or [3] to memory.
// So, my_buffer is now: [..., 18.8, 19.9]
```

## A Peek at the Standard Library Code

Let's see how these are defined in `stdlib/src/buffer/buffer.mojo`.

**`NDBuffer.load` (and `store` is similar):**
```mojo
@always_inline("nodebug")
fn load[
    *, width: Int = 1, alignment: Int = Self._default_alignment[width]()
](self, idx: StaticTuple[Int, rank]) -> SIMD[type, width]:
    """Loads a simd value from the buffer at the specified index.
    Constraints:
        The buffer must be contiguous or width must be 1.
    ...
    """
    debug_assert(
        self.is_contiguous() or width == 1,
        "Function requires contiguous buffer.",
    )
    // 1. Calculate the flat 1D offset for the N-D index `idx`
    // 2. Get the UnsafePointer at that offset
    // 3. Call the UnsafePointer's own .load() method
    return self._offset(idx).load[width=width, alignment=alignment]()
```
The `alignment` parameter is a hint about memory alignment, which can sometimes improve performance. `_default_alignment` provides a sensible default.

**`partial_simd_load` function:**
```mojo
@always_inline
fn partial_simd_load[
    type: DType, //, width: Int
](
    storage: UnsafePointer[Scalar[type], **_], // The pointer to memory
    lbound: Int,                              // Start of valid data in SIMD vector
    rbound: Int,                              // End of valid data in SIMD vector
    pad_value: Scalar[type],                  // Value for padding
) -> SIMD[type, width]:
    """Loads a vector with dynamic bound.
    Out of bound data will be filled with pad value. ...
    """
    # Create a mask based on input bounds.
    var effective_lbound = max(0, lbound)
    var effective_rbound = min(width, rbound)
    var incr = iota[DType.int32, width]() // Generates [0, 1, 2, ..., width-1]
    var mask = (incr >= effective_lbound) & (incr < effective_rbound)

    // Use the masked_load intrinsic:
    // Loads from `storage` where mask is true, uses `pad_value` where mask is false.
    return masked_load[width](storage, mask, pad_value)
```
`partial_simd_store` is structured similarly, using the `masked_store` intrinsic.

## Putting It All Together: Vectorizing a Loop (Conceptual)

Imagine you want to add a constant `C` to all elements of a large 1D `NDBuffer `my_data`.

```mojo
let N = len(my_data)
let W = simdwidthof[MyDataType]() // Get native SIMD width for the data type

// 1. Main SIMD loop for full vectors
var i: Int = 0
while i + W <= N:
    let data_vec = my_data.load[width=W](i)
    let result_vec = data_vec + SIMD[MyDataType, W](C)
    my_data.store[width=W](i, result_vec)
    i += W

// 2. Handle remaining elements using partial SIMD (if any)
if i < N:
    let num_remaining = N - i
    let ptr_to_remaining = my_data.data.offset(my_data._offset_of_index(i)) // Get pointer

    let partial_data_vec = partial_simd_load[MyDataType, W](
        ptr_to_remaining, 0, num_remaining, Scalar[MyDataType](0) // Pad with 0
    )
    let partial_result_vec = partial_data_vec + SIMD[MyDataType, W](C)
    partial_simd_store[MyDataType, W](
        ptr_to_remaining, 0, num_remaining, partial_result_vec
    )
```
This pattern (a main SIMD loop and a smaller loop or partial operation for the remainder) is very common in high-performance code.

## Key Takeaways for Chapter 5

*   **SIMD (Single Instruction, Multiple Data)** allows processing multiple data elements simultaneously, significantly boosting performance.
*   `NDBuffer` supports full SIMD vector operations via `load[width=W]()` and `store[width=W]()` methods.
    *   These require the `NDBuffer` to be **contiguous** (innermost stride is 1) if `width > 1`.
*   The "edge problem" occurs when the number of elements isn't a perfect multiple of SIMD width `W`.
*   The `buffer` module provides `partial_simd_load` and `partial_simd_store` utility functions to safely handle these edge cases using masking.
    *   These functions operate on `UnsafePointer`s and take `lbound` and `rbound` parameters to define the valid portion of the SIMD vector.
*   Combining full SIMD operations for the bulk of the data and partial SIMD operations for the remainder is a common strategy for vectorization.

By understanding and using these SIMD capabilities, you can write much faster Mojo code for data-intensive tasks!

---
_Navigation_
1. [UnsafePointer (as used by NDBuffer)](01_unsafepointer__as_used_by_ndbuffer__.md)
2. [DimList and Dim](02_dimlist_and_dim_.md)
3. [NDBuffer](03_ndbuffer_.md)
4. [Strides and Offset Computation](04_strides_and_offset_computation_.md)
5. **SIMD Data Access (You are here)**
```

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)