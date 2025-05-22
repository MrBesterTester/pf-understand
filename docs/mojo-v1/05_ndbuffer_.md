---
layout: default
title: "Chapter 5: NDBuffer"
parent: "My Tutorial for Mojo v1"
nav_order: 5
---
# Chapter 5: NDBuffer

Okay, here is Chapter 5 on `NDBuffer`, designed to be very beginner-friendly and in Markdown format.

```markdown
# Chapter 5: The N-Dimensional Buffer: `NDBuffer`

Welcome to Chapter 5! So far, we've explored some fundamental Mojo concepts:
*   [Chapter 1: `AddressSpace`](01_addressspace_.md) (memory "neighborhoods")
*   [Chapter 2: `UnsafePointer`](02_unsafepointer_.md) (direct memory addresses)
*   [Chapter 3: `IndexList`](03_indexlist_.md) (for multi-dimensional coordinates)
*   [Chapter 4: `Dim` and `DimList`](04_dimlist_.md) (for describing dimension sizes, statically or dynamically)

Now, we're going to put these pieces together to understand one of Mojo's most powerful data structures for numerical computing: `NDBuffer`.

## What is `NDBuffer`?

The official description states:

> `NDBuffer` represents a multi-dimensional array or tensor, commonly used in numerical computing and machine learning. Think of it as a smart "view" or a "lens" that lets you interpret a flat, one-dimensional block of memory as a structured grid (like a 2D image, 3D volume, or higher-dimensional data). It doesn't own the memory itself but holds essential metadata: the data type of elements, the shape (dimensions of the grid), and strides (how many memory elements to skip to move to the next item along each dimension). This design allows for flexible data layouts (e.g., row-major, column-major) and efficient access without needing to copy the underlying data.

Let's break that down:

*   **Multi-dimensional array/tensor**: Imagine a Python list, but it can have multiple dimensions.
    *   A 1D `NDBuffer` is like a simple list or vector: `[1, 2, 3, 4]`
    *   A 2D `NDBuffer` is like a grid or matrix (think spreadsheet or image):
        ```
        [[1, 2, 3],
         [4, 5, 6]]
        ```
    *   A 3D `NDBuffer` is like a cube or volume of data:
        ```
        [[[1,2], [3,4]],
         [[5,6], [7,8]]]
        ```
    And it can go to even higher dimensions!

*   **"View" or "Lens"**: This is super important! Most of the time, an `NDBuffer` doesn't hold the actual data values itself. Instead, it *points* to some memory (managed by an `UnsafePointer` internally) and tells Mojo how to interpret that raw memory as a structured N-dimensional grid.
    *   *Analogy*: Imagine you have a long, single line of LEGO bricks (this is your flat memory). An `NDBuffer` is like a special pair of glasses that lets you see those bricks as if they were arranged in a 2x2 square or a 3x4 rectangle, without actually moving the bricks.

*   **Metadata**: To act as this "lens," `NDBuffer` stores crucial information:
    *   **Data Type (`DType`)**: What kind of data is in each cell (e.g., `Float32`, `Int64`).
    *   **Shape (`DimList`)**: The size of each dimension (e.g., a 2x3 matrix has shape `(2, 3)`).
    *   **Strides (`DimList`)**: How many actual memory slots to jump over to get to the next element along each dimension. (We'll dive deeper into strides in the next chapter, but for now, know it helps `NDBuffer` find elements quickly in that flat memory).

This "view" approach is very powerful because it allows for:
*   **Flexibility**: The same underlying data can be viewed in different ways (e.g., as a 4x4 matrix or as a 2x8 matrix, if memory layout allows).
*   **Efficiency**: You can perform operations like transposing a matrix or taking a slice (a sub-section) often without copying any data, just by creating a new `NDBuffer` with different shape/stride metadata.

## Anatomy of an `NDBuffer`

Let's look at the parameters that define an `NDBuffer`. You'll see how concepts from previous chapters fit in:

```mojo
struct NDBuffer[
    mut: Bool, // Is the data mutable (changeable) through this NDBuffer?
    type: DType, // The data type of each element (e.g., DType.float32)
    rank: Int, // The number of dimensions (e.g., 2 for a matrix)
    origin: Origin[mut], // Advanced: Tracks memory validity and source
    shape: DimList = DimList.create_unknown[rank](), // From Ch4: Sizes of dimensions
    strides: DimList = DimList.create_unknown[rank](), // From Ch4: Memory step sizes
    *, // Parameters below are keyword-only
    alignment: Int = 1, // Memory alignment preference
    address_space: AddressSpace = AddressSpace.GENERIC, // From Ch1: Where memory lives
    exclusive: Bool = True, // Advanced: If this is the only pointer to the memory
]
```

Inside an `NDBuffer`, there are important fields:
*   `data: UnsafePointer[...]`: (From Ch2) An `UnsafePointer` to the *actual start* of the data in memory.
*   `dynamic_shape: IndexList[...]`: (From Ch3) If the `shape` `DimList` had dynamic dimensions (`?`), this `IndexList` holds their actual runtime values.
*   `dynamic_stride: IndexList[...]`: (From Ch3) Similar to `dynamic_shape`, but for strides.

For beginners, the most immediately important parameters are `type`, `rank`, and `shape`. `mut` determines if you can change data. `address_space` is often `AddressSpace.GENERIC` for CPU memory.

## Creating an `NDBuffer`

There are a few ways to create an `NDBuffer`.

### 1. Using Existing Memory (e.g., an `InlineArray`)

Often, you'll have some memory already (perhaps in an `InlineArray` which stores data directly, or from another source), and you want `NDBuffer` to provide a view over it.

Let's look at the `test_ndbuffer` example from `stdlib/test/buffer/test_ndbuffer.mojo`:
```mojo
from buffer import NDBuffer, DimList // Import NDBuffer and DimList
from memory import InlineArray // For stack-allocated flat array
from builtin import DType, Scalar // For data types

fn create_ndbuffer_from_inline_array():
    // First, reserve some flat memory.
    // InlineArray creates memory on the "stack" (fast, temporary memory).
    // We need space for 4*4 = 16 elements of type DType.index.
    // DType.index is Mojo's default integer type, often 64-bit.
    var matrix_data_storage = InlineArray[Scalar[DType.index], 16](uninitialized=True)

    // Now, create an NDBuffer to view this memory as a 4x4 matrix.
    var matrix = NDBuffer[
        DType.index,  // Element data type
        2,            // Rank: 2 dimensions (it's a matrix)
        _,            // Origin: We use `_` to let Mojo infer a suitable default.
                      // This is an advanced parameter for tracking memory origin.
        DimList(4, 4) // Shape: A 4x4 matrix (Static dimensions from Chapter 4)
    ](matrix_data_storage) // The NDBuffer will "view" the data in matrix_data_storage

    // At this point, 'matrix' is a 4x4 NDBuffer, but its data is uninitialized.
    // We can now fill it. For example:
    matrix[0, 0] = 0
    matrix[0, 1] = 1
    // ... and so on.
    print("Created matrix. Element at (0,0) after setting:", matrix[0,0])
```
In this case:
*   `matrix_data_storage` holds the raw, flat memory.
*   `matrix` (the `NDBuffer`) doesn't copy the data; it just knows how to interpret the memory in `matrix_data_storage` as a 4x4 grid.
*   `DimList(4, 4)` tells Mojo the shape is fixed at compile time. If the shape were dynamic, we might use `DimList(Dim(), Dim())` and provide an `IndexList` with actual dimensions later.

**Memory Ownership Note**: When you create an `NDBuffer` this way, *you* are responsible for making sure `matrix_data_storage` (or whatever memory `matrix.data` points to) stays valid for as long as `matrix` is used. `NDBuffer` itself doesn't manage this external memory's lifetime.

### 2. Using `NDBuffer.stack_allocation()`

Sometimes, you want an `NDBuffer` that also manages its own small piece of memory, allocated on the stack. This is useful for small, temporary N-dimensional arrays where you know the size at compile time.

From `test_aligned_load_store` in `stdlib/test/buffer/test_ndbuffer.mojo`:
```mojo
from buffer import NDBuffer, DimList
from memory import MutableAnyOrigin // Needed for stack_allocation's origin
from builtin import DType

fn create_ndbuffer_on_stack():
    // Create a 4x4 NDBuffer. The memory will be allocated on the stack.
    var matrix_on_stack = NDBuffer[
        DType.index,      // Element data type
        2,                // Rank: 2 dimensions
        MutableAnyOrigin, // Origin: Special type indicating new, mutable stack memory
        DimList(4, 4)     // Shape: A 4x4 matrix (must be static for stack_allocation)
    ].stack_allocation[alignment=128]() // Allocate memory on stack, specify alignment

    // Now matrix_on_stack is ready to use.
    matrix_on_stack[0, 0] = 123
    print("Stack allocated matrix. Element at (0,0):", matrix_on_stack[0,0])

    // Memory for matrix_on_stack is automatically reclaimed when it goes out of scope.
```
Key differences:
*   The shape (`DimList(4, 4)`) *must* be fully static (no `Dim()`).
*   We use `MutableAnyOrigin` to tell Mojo this is fresh memory.
*   The `.stack_allocation()` call does the memory allocation.
*   **Memory Ownership**: In this case, the `NDBuffer` *does* manage the lifetime of its stack-allocated memory. It's automatically freed when `matrix_on_stack` is no longer in use.

## Working with `NDBuffer` Elements

### Setting Values

You can set values in an `NDBuffer` using square brackets `[]`. You can provide the indices as a sequence of integers or as an `IndexList` (from Chapter 3).

```mojo
from utils import IndexList // For using IndexList explicitly

// Assuming 'matrix' is our 4x4 NDBuffer from earlier:
// Method 1: Multiple integer arguments
matrix[0, 0] = 0
matrix[0, 1] = 1
matrix[0, 2] = 2
matrix[0, 3] = 3
matrix[1, 0] = 4
// ... and so on for all 16 elements.

// Method 2: Using an IndexList
matrix[IndexList[2](3, 3)] = 15 // Set the element at row 3, column 3
```
The `test_ndbuffer` function in `stdlib/test/buffer/test_ndbuffer.mojo` shows populating a 4x4 matrix like this:
```mojo
    // (matrix is a 4x4 NDBuffer[DType.index, 2, _, DimList(4,4)])
    matrix[IndexList[2](0, 0)] = 0
    matrix[IndexList[2](0, 1)] = 1
    // ...
    matrix[IndexList[2](3, 3)] = 15
```
Or, more simply with multiple arguments, as shown in later parts of the same test file for reading: `matrix[0,0]`.

### Getting Values

Similarly, you use `[]` to get values:
```mojo
// Assuming 'matrix' is populated
var val_0_0 = matrix[0, 0]       // val_0_0 will be 0
var val_1_2 = matrix[1, 2]       // val_1_2 will be 6
var val_3_3 = matrix[IndexList[2](3,3)] // val_3_3 will be 15

print("Value at (0,0) is:", val_0_0)
print("Value at (1,2) is:", val_1_2)
```

The `test_ndbuffer` code prints all elements this way:
```mojo
// CHECK: 0
print(matrix[0, 0])
// CHECK: 1
print(matrix[0, 1])
// ...
// CHECK: 15
print(matrix[3, 3])
```

## Common `NDBuffer` Operations and Methods

`NDBuffer` comes with many useful methods. Let's look at some from `stdlib/test/buffer/test_ndbuffer.mojo`.

### Getting Information

*   **`get_rank() -> Int`**: Returns the number of dimensions.
    ```mojo
    // For our 4x4 matrix:
    print(matrix.get_rank()) // CHECK: 2
    ```
*   **`size() -> Int`** (or **`num_elements() -> Int`**): Returns the total number of elements.
    ```mojo
    // For our 4x4 matrix (4 * 4 = 16 elements):
    print(matrix.size()) // CHECK: 16
    ```
*   **`dim[compile_time_index]() -> Int`** or **`dim(runtime_index: Int) -> Int`**: Gets the size of a specific dimension.
    ```mojo
    var shape_of_matrix = matrix.get_shape() // Returns an IndexList, e.g., (4, 4)
    print("Dim 0:", matrix.dim[0]())   // Compile-time index: matrix.dim[0]() -> 4
    print("Dim 1:", matrix.dim(1))     // Runtime index: matrix.dim(1) -> 4
    ```
*   **`get_shape() -> IndexList[rank]`**: Returns the shape as an `IndexList`.
*   **`get_strides() -> IndexList[rank]`**: Returns the strides (more on this in the next chapter).

### Modifying Content

*   **`fill(value: Scalar[type])`**: Sets all elements in the `NDBuffer` to a single `value`. The buffer must be contiguous (its elements laid out sequentially in memory, which is typical for default NDBuffers).
    ```mojo
    // From test_fill:
    var filled_stack = InlineArray[Scalar[DType.index], 3 * 3](uninitialized=True)
    var filled_buffer = NDBuffer[DType.index, 2, _, DimList(3, 3)](filled_stack)
    filled_buffer.fill(1) // All 9 elements of filled_buffer become 1
    // (The test then compares this to a manually filled buffer)
    ```

### Converting Indices

*   **`get_nd_index(flat_index: Int) -> IndexList[rank]`**: Converts a 1D "flat" index (as if all elements were in a single line) into N-Dimensional coordinates.
    ```mojo
    // From test_get_nd_index:
    // matrix0 is a 2x3 NDBuffer (total 6 elements, indexed 0 to 5)
    // [[(0,0), (0,1), (0,2)],
    //  [(1,0), (1,1), (1,2)]]
    // Flat indices: 0, 1, 2, 3, 4, 5
    // matrix0.get_nd_index(0) -> (0,0)
    // matrix0.get_nd_index(1) -> (0,1)
    // matrix0.get_nd_index(3) -> (1,0)
    // matrix0.get_nd_index(5) -> (1,2)

    // In the test:
    // var matrix0 = NDBuffer[DType.index, 2, _, DimList(2, 3)](...)
    // print(matrix0.get_nd_index(3)) // CHECK: (1, 0)
    // print(matrix0.get_nd_index(5)) // CHECK: (1, 2)
    ```

### Slicing and Viewing (Creating Tiles)

*   **`tile[*tile_sizes: Dim](tile_coords: IndexList[rank]) -> NDBuffer`**: Creates a new `NDBuffer` that is a "view" (not a copy!) of a smaller N-D sub-section of the original buffer. This is powerful for working with parts of larger arrays.
    `*tile_sizes` are the dimensions of the tile you want to extract.
    `tile_coords` are the coordinates *in terms of tiles*.
    ```mojo
    // From test_ndbuffer_tile (simplified conceptual view)
    // buff is an 8x8 NDBuffer
    // Let's get a 4x4 tile starting at the first tile block (0,0)
    // var tile_4x4 = buff.tile[4, 4](Index(0,0))
    // 'tile_4x4' is now a 4x4 NDBuffer viewing the top-left 4x4 part of 'buff'.
    // Changes to 'tile_4x4' will affect 'buff' and vice-versa.

    // The test code iterates to show tiling:
    // alias M = 8, N = 8, m0_tile_size = 4, n0_tile_size = 4
    // var buff = NDBuffer[DType.float32, 2, _, DimList(M, N)](...)
    // ... fill buff ...
    // for tile_i in range(M // m0_tile_size): // 0 to 1
    //     for tile_j in range(N // n0_tile_size): // 0 to 1
    //         print("tile-0[", tile_i, tile_j, "]")
    //         var tile_4x4 = buff.tile[m0_tile_size, n0_tile_size](
    //             tile_coords=Index(tile_i, tile_j)
    //         )
    //         print_buffer(tile_4x4) // Prints the 4x4 tile
    ```
    This is a very efficient way to work with sub-arrays.

### Printing

*   Printing an `NDBuffer` or converting it to a `String` gives a nice, human-readable representation.
    ```mojo
    // From test_print:
    // buffer is a 2x2x3 NDBuffer
    // String(buffer) produces:
    // "NDBuffer([[[0, 1, 2],
    // [3, 4, 5]],
    // [[6, 7, 8],
    // [9, 10, 11]]], dtype=index, shape=2x2x3)"
    ```

### File I/O

*   **`tofile(path: Path)`**: Writes the raw byte contents of the `NDBuffer` to a binary file. The buffer should be contiguous.
    ```mojo
    // From test_ndbuffer_tofile:
    // var buf = NDBuffer[DType.float32, 2, _, DimList(2, 2)](...)
    // buf.fill(2.0)
    // with NamedTemporaryFile(name=String("test_ndbuffer")) as TEMP_FILE:
    //     buf.tofile(TEMP_FILE.name)
    //     // The test then reads it back to verify
    ```

### Performance Features (Brief Mention for Awareness)

`NDBuffer` also has features for advanced performance tuning, which you might encounter later:
*   **`prefetch[PrefetchOptions()](*idx: Int)`**: Hints to the CPU/GPU to start loading data from a specific index into its cache before it's explicitly needed. (See `test_ndbuffer_prefetch`).
*   **`load[width=N](*idx: Int)` / `store[width=N](*idx: Int, value: SIMD[...])`**: Perform vectorized (SIMD) loads and stores, reading/writing multiple elements at once if the hardware supports it and memory is aligned. (See `test_aligned_load_store`). These require contiguous memory.

## Key Takeaways for `NDBuffer`

*   `NDBuffer` is Mojo's primary tool for working with **multi-dimensional data** (vectors, matrices, tensors).
*   It's usually a **"view" or "lens"** over existing memory, defined by metadata (dtype, shape, strides).
*   It **doesn't typically own the memory** unless created with `stack_allocation()`. You must manage the lifetime of the underlying memory if `NDBuffer` is just a view.
*   Creation involves specifying element `DType`, `rank` (number of dimensions), and `shape` (using `DimList`).
*   Elements are accessed and modified using `[index0, index1, ...]`.
*   Provides useful methods like `get_rank()`, `size()`, `fill()`, `get_nd_index()`, `tile()`, and `tofile()`.
*   The ability to mix static and dynamic dimensions (via `DimList`) allows for both compile-time optimization and runtime flexibility.

## Full Example: A Simple 2x3 Matrix

Let's create a small 2x3 matrix, fill it, and print some info.

```mojo
from buffer import NDBuffer, DimList
from memory import InlineArray, MutableAnyOrigin
from builtin import DType, Scalar
from utils import IndexList

fn main_ndbuffer_example():
    print("--- NDBuffer Simple 2x3 Matrix Example ---")

    // Method 1: View over InlineArray
    print("\n1. NDBuffer as a view over InlineArray:")
    var flat_data = InlineArray[Scalar[DType.int32], 2 * 3](uninitialized=True)
    var matrix_view = NDBuffer[
        DType.int32,
        2, // rank
        _, // origin (inferred)
        DimList(2, 3) // shape: 2 rows, 3 columns
    ](flat_data)

    // Populate matrix_view
    for r in range(2):
        for c in range(3):
            matrix_view[r, c] = r * 10 + c
    
    print("Matrix View:")
    print(matrix_view)
    print("Rank:", matrix_view.get_rank())
    print("Size:", matrix_view.size())
    print("Shape:", matrix_view.get_shape())
    print("Element (1,1):", matrix_view[1,1])


    // Method 2: Stack-allocated NDBuffer
    print("\n2. Stack-allocated NDBuffer:")
    var matrix_stack = NDBuffer[
        DType.int32,
        2, // rank
        MutableAnyOrigin,
        DimList(2,3) // shape
    ].stack_allocation()

    // Populate matrix_stack
    for r in range(2):
        for c in range(3):
            matrix_stack[r, c] = (r+1) * 100 + (c+1)

    print("Matrix Stack:")
    print(matrix_stack)
    print("Element (0,2):", matrix_stack[0,2])

    print("\n--- End of Example ---")

# To run this, you'd call main_ndbuffer_example()
# main_ndbuffer_example()
```

## Next Steps

`NDBuffer` is incredibly versatile. A key to its power is how it uses **strides** to navigate its underlying flat memory. In the next chapter, we'll delve into "N-D to 1D Indexing Logic (Strided Memory Access)" to understand how `NDBuffer` calculates the exact memory location for an element like `matrix[row, col, depth]` and how strides enable different memory layouts (like row-major vs. column-major). This will complete your foundational understanding of `NDBuffer`!

---
**Table of Contents**
1. [Chapter 1: Understanding Memory Neighborhoods with `AddressSpace`](01_addressspace_.md)
2. [Chapter 2: Peeking into Memory with `UnsafePointer`](02_unsafepointer_.md)
3. [Chapter 3: Working with Multiple Dimensions: `IndexList`](03_indexlist_.md)
4. [Chapter 4: Describing Dimensions with `Dim` and `DimList`](04_dimlist_.md)
5. **Chapter 5: The N-Dimensional Buffer: `NDBuffer`** (You are here)
6. _Coming Soon: Chapter 6: N-D to 1D Indexing Logic (Strided Memory Access)_
```

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)