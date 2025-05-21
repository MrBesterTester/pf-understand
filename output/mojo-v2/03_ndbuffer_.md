# Chapter 3: `NDBuffer` - Your Lens on N-Dimensional Data

Welcome back! In our Mojo journey so far, we've explored some fundamental building blocks:

*   In [Chapter 1: Meet `UnsafePointer`](01_unsafepointer__as_used_by_ndbuffer__.md), we learned that an `UnsafePointer` is like a direct street address to a location in your computer's memory where data can be stored.
*   In [Chapter 2: Defining Dimensions - `Dim` and `DimList`](02_dimlist_and_dim_.md), we saw how `Dim` represents the size of a single dimension (which can be known at compile-time or runtime) and `DimList` collects these `Dim`s to describe the overall shape of multi-dimensional data.

Now, it's time to bring these concepts together and meet the star of our show: `NDBuffer`.

The `NDBuffer` struct is central to handling multi-dimensional arrays (like vectors, matrices, or tensors) in Mojo. Think of it as a sophisticated "lens" or a "view" that you place over a raw block of memory. It doesn't own the memory itself, but it tells Mojo how to *interpret* that memory as an N-dimensional structure.

As described in the project:
> The `NDBuffer` struct is a non-owning, multi-dimensional view into a block of memory. It describes how to interpret a (potentially flat) piece of memory as an N-dimensional array (like a tensor or matrix). It achieves this by specifying the data type of elements (`type`), the number of dimensions (`rank`), the size of each dimension (`shape`), how to step through memory for each dimension (`strides`), the memory's `origin` (related to aliasing and lifetime), and its `address_space` (e.g., CPU, GPU shared memory). `NDBuffer` itself doesn't own the memory; it's a descriptor or a "lens" for existing memory.

Let's dive into what makes an `NDBuffer` tick!

## What Exactly is an `NDBuffer`?

Imagine you have a large, flat sheet of graph paper, and each square on the paper can hold a single number. This sheet of graph paper is like a block of memory.

An `NDBuffer` is like an adjustable stencil or a set of instructions you lay over this graph paper. This stencil tells you:
*   **What kind of numbers** are in the squares (e.g., integers, decimal numbers).
*   **How many rows and columns** (or even more dimensions, like layers) you should consider.
*   **The size of each row and column**.
*   **How many squares to jump** to get from one number to the next, either across a row or down to the next row.

Crucially, the `NDBuffer` is just the stencil/instructions. It doesn't *contain* the graph paper (the memory) itself. It just knows *how to look at it*. This is why it's called a "non-owning view."

## The Anatomy of an `NDBuffer`

Let's peek inside the `NDBuffer` struct as defined in `stdlib/src/buffer/buffer.mojo`. We won't look at every line, but we'll focus on the main parts a beginner needs to understand.

An `NDBuffer` is defined as a `struct`. When you create an `NDBuffer`, you're creating an instance of this struct. It has several important **parameters** (information you provide when creating it) and internal **fields** (where it stores its state).

### Key Parameters (Compile-Time Information)

These are specified when you declare or create an `NDBuffer`. They help Mojo understand the *intended* structure and properties, often allowing for compile-time optimizations.

```mojo
// Simplified NDBuffer definition from stdlib/src/buffer/buffer.mojo
struct NDBuffer[
    mut: Bool, // Can the data be modified through this NDBuffer?
    type: DType, // What's the data type of each element? (e.g., DType.float32)
    rank: Int, // How many dimensions? (e.g., 2 for a matrix)
    origin: Origin[mut], // Related to memory safety and lifetime tracking

    // These use DimList from Chapter 2!
    shape: DimList = DimList.create_unknown[rank](), // Compile-time description of dimension sizes
    strides: DimList = DimList.create_unknown[rank](), // Compile-time description of memory layout

    *, // Indicates subsequent parameters are keyword-only
    alignment: Int = 1, // Preferred memory alignment for performance
    address_space: AddressSpace = AddressSpace.GENERIC, // Where is the memory? (CPU, GPU)
    exclusive: Bool = True // Is this NDBuffer the only way to access the memory?
] {
    // ... Internal fields and methods ...
}
```

Let's break these down:
*   `mut: Bool`: Short for "mutable." If `True`, you can change the data elements in the `NDBuffer`. If `False`, it's read-only.
*   `type: DType`: Specifies the data type of the elements stored. `DType` is Mojo's way of representing types like `float32`, `int64`, etc.
*   `rank: Int`: The number of dimensions. A 1D array (vector) has `rank=1`. A 2D array (matrix) has `rank=2`. A 3D array (like a cube of data) has `rank=3`, and so on.
*   `origin: Origin[mut]`: An advanced Mojo concept related to memory ownership and borrowing rules. It helps Mojo track where the permission to access the memory came from, enhancing safety. It's often tied to the `UnsafePointer` that the `NDBuffer` will use.
*   `shape: DimList`: This is where `DimList` (from Chapter 2) comes in! It's a compile-time list of `Dim`s describing the *intended* size of each dimension. Some `Dim`s can be static (e.g., `Dim(10)`), and some can be dynamic (`Dim()`, meaning the size will be known at runtime). By default, it's `DimList.create_unknown[rank]()`, meaning all dimension sizes are initially considered dynamic.
*   `strides: DimList`: Another `DimList`! This describes the *strides* of the buffer at compile time. Strides tell Mojo how many elements to "skip" in memory to move to the next element along a particular dimension. We'll cover strides in detail in the next chapter. Like `shape`, it defaults to all dynamic.
*   `alignment: Int`: For performance, data in memory is sometimes "aligned" to start at addresses that are multiples of a certain number (e.g., 16 bytes, 64 bytes). This parameter specifies the desired alignment.
*   `address_space: AddressSpace`: Tells Mojo where the memory this `NDBuffer` describes is located (e.g., general CPU memory (`AddressSpace.GENERIC`), GPU shared memory, etc.).
*   `exclusive: Bool`: A more advanced flag. If `True`, it suggests that this `NDBuffer` (and its underlying pointer) is the *only* way the program is supposed to access this specific block of memory. This can enable certain optimizations.

### Core Internal Fields (Runtime Information)

Inside every `NDBuffer` instance, there are a few crucial fields that store its runtime state:

```mojo
// Inside the NDBuffer struct definition...
// ...
    var data: UnsafePointer[
        Scalar[type], // Points to elements of the NDBuffer's 'type'
        address_space=address_space, // Inherits from NDBuffer's parameter
        mut=mut, // Inherits from NDBuffer's parameter
        origin=origin // Inherits from NDBuffer's parameter
    ];

    // These store the *actual* runtime dimension sizes and strides
    var dynamic_shape: IndexList[rank, element_type = DType.uint64];
    var dynamic_stride: IndexList[rank, element_type = DType.uint64];
// ...
```

Let's understand these:
1.  `data: UnsafePointer[...]`: This is the direct link to the memory! It's an `UnsafePointer` (from Chapter 1) that holds the memory address where the *first element* of the `NDBuffer`'s data begins.
    *   Notice `Scalar[type]`: If `NDBuffer.type` is `DType.float32`, then `Scalar[type]` becomes `Float32`. The `UnsafePointer` points to individual elements of this type.
    *   Its `address_space`, `mut` (mutability), and `origin` are typically inherited from the `NDBuffer`'s own parameters.

2.  `dynamic_shape: IndexList[rank, ... ]`: This field holds the *actual, runtime* size of each of the `NDBuffer`'s `rank` dimensions.
    *   An `IndexList` is a list of integers.
    *   Even if you provided static dimensions in the `shape: DimList` parameter (e.g., `DimList(Dim(3), Dim(4))`), those values get stored here (e.g., `IndexList(3, 4)`).
    *   If your `shape: DimList` had dynamic dimensions (e.g., `DimList(Dim(3), Dim())`), then `dynamic_shape` would be filled in when the `NDBuffer` is fully initialized with the actual runtime size for that dynamic dimension.

3.  `dynamic_stride: IndexList[rank, ... ]`: Similar to `dynamic_shape`, this field holds the *actual, runtime* stride for each dimension. Strides are crucial for navigating the N-dimensional data in the flat 1D memory. We'll dedicate the next chapter to understanding them.

So, the `NDBuffer` uses its `data` pointer to find the start of the memory, and then uses `dynamic_shape` and `dynamic_stride` to interpret that flat memory as a structured N-dimensional array.

## Bringing It All Together: Initializing an `NDBuffer`

`NDBuffer` has many ways to be initialized (many `__init__` methods). We won't cover them all, but let's look at the general idea with a couple of simplified examples.

**Example 1: A 2D `NDBuffer` with Statically Known Shape**

Imagine you have an `UnsafePointer` called `my_ptr` that points to a block of `Float32` data in memory. You want to view this data as a 2x3 matrix (2 rows, 3 columns).

```mojo
from memory import UnsafePointer, DType, Origin
from buffer import NDBuffer, DimList, Dim

fn main() raises:
    // Assume my_ptr is a valid UnsafePointer to enough Float32 data
    // For this example, we'll just create a dummy one.
    // In a real scenario, this memory would be allocated.
    var my_ptr = UnsafePointer[Float32](); // Dummy pointer

    // Define the NDBuffer's properties
    alias MyOrigin = Origin[True].init() // A dummy origin for the example

    // Create an NDBuffer for a 2x3 matrix of Float32s
    // NDBuffer[mut, type, rank, origin, shape_dimlist](pointer_to_data)
    let matrix_view = NDBuffer[
        True,                 // mut = True (mutable)
        DType.float32,        // type = DType.float32
        2,                    // rank = 2 (2D)
        MyOrigin,             // origin (memory tracking)
        DimList(Dim(2), Dim(3)) // shape = 2 rows, 3 columns (all static)
    ](my_ptr);

    // What happens inside matrix_view?
    // - matrix_view.data will hold my_ptr
    // - matrix_view.dynamic_shape will be an IndexList like (2, 3)
    // - matrix_view.dynamic_stride will be calculated for a contiguous 2x3 layout
    //   (e.g., (3, 1) meaning jump 3 elements for next row, 1 for next column)
    print(matrix_view.get_shape())
```
*Output (conceptual, depends on actual initialization context for dummy pointer)*:
```
(2, 3)
```
In this case, because the shape `DimList(Dim(2), Dim(3))` is fully static, Mojo knows the exact dimensions at compile time. The `NDBuffer` then stores this pointer and shape information. It also computes default strides assuming the data is laid out contiguously (like words in a book, one row after another).

**Example 2: A 1D `NDBuffer` with Dynamically Known Shape**

Now, let's say `my_ptr` points to `Int` data, but the number of integers isn't known until runtime.

```mojo
from memory import UnsafePointer, DType, Origin, IndexList
from buffer import NDBuffer, DimList

fn main() raises:
    var my_ptr = UnsafePointer[Int](); // Dummy pointer
    alias MyOrigin = Origin[True].init()

    let num_elements_runtime: Int = 10; // Determined at runtime

    // Create an NDBuffer for a 1D array.
    // The shape DimList parameter defaults to DimList.create_unknown[rank](),
    // so we pass the dynamic shape directly.
    // NDBuffer[mut, type, rank, origin](pointer_to_data, dynamic_shape_indexlist)
    let vector_view = NDBuffer[
        True,          // mut
        DType.int64,   // type
        1,             // rank = 1 (1D)
        MyOrigin       // origin
    ](my_ptr, IndexList[1](num_elements_runtime));

    // Inside vector_view:
    // - vector_view.data holds my_ptr
    // - vector_view.dynamic_shape will be an IndexList like (10)
    // - vector_view.dynamic_stride will be (1) for a contiguous 1D array.
    print(vector_view.get_shape())
```
*Output (conceptual)*:
```
(10)
```
Here, the `NDBuffer` is initialized with `my_ptr` and an `IndexList` containing the runtime size `num_elements_runtime`. The `dynamic_shape` field inside `vector_view` will store this runtime size.

These examples show the core idea: `NDBuffer` combines a pointer to raw memory (`data`) with descriptions of its structure (`dynamic_shape`, `dynamic_stride`) to provide a meaningful N-dimensional view.

## What Can You Do With an `NDBuffer`? (A Sneak Peek)

Once you have an `NDBuffer`, you can perform many operations, such as:

*   **Get its rank**: `let r = my_ndbuffer.get_rank()`
*   **Get its shape (runtime)**: `let s = my_ndbuffer.get_shape()` (returns an `IndexList`)
*   **Get its strides (runtime)**: `let st = my_ndbuffer.get_strides()` (returns an `IndexList`)
*   **Get the total number of elements**: `let count = my_ndbuffer.num_elements()` or `len(my_ndbuffer)`
*   **Access an element**: `let element = my_ndbuffer[idx0, idx1, ...]` (e.g., `matrix_view[0, 1]` for row 0, col 1). This is done via the `__getitem__` method.
*   **Set an element (if mutable)**: `my_ndbuffer[idx0, idx1, ...] = new_value`. This is done via the `__setitem__` method.
*   **Load/Store SIMD vectors**: For performance, you can load or store multiple elements at once using SIMD operations (e.g., `my_ndbuffer.load[width=4](...)`).

We'll explore these operations, especially element access and the role of strides, in more detail in upcoming chapters.

## Key Takeaways for Chapter 3

*   `NDBuffer` is a **non-owning view** or "lens" that interprets a block of memory as an N-dimensional array.
*   It combines an `UnsafePointer` (to the start of the data) with shape and stride information.
*   **Key Parameters** (compile-time info): `mut`, `type`, `rank`, `origin`, `shape: DimList`, `strides: DimList`, `alignment`, `address_space`.
*   **Core Internal Fields** (runtime info): `data: UnsafePointer`, `dynamic_shape: IndexList`, `dynamic_stride: IndexList`.
*   The `shape: DimList` parameter allows specifying static or dynamic dimension sizes at compile time, while `dynamic_shape: IndexList` stores the actual runtime sizes.
*   `NDBuffer` enables Mojo to handle multi-dimensional data flexibly and efficiently.

## What's Next?

We've seen that `NDBuffer` uses `data`, `dynamic_shape`, and `dynamic_stride` to make sense of memory. But how exactly does it use `dynamic_stride` to find, for example, the element at `[row_index, column_index]` in a 2D matrix? This involves understanding **strides** and **offset computation**. That's precisely what we'll unravel in [Chapter 4: Strides and Offset Computation](04_strides_and_offset_computation_.md)!

---
_Navigation_
1. [UnsafePointer (as used by NDBuffer)](01_unsafepointer__as_used_by_ndbuffer__.md)
2. [DimList and Dim](02_dimlist_and_dim_.md)
3. **NDBuffer (You are here)**
4. [Strides and Offset Computation](04_strides_and_offset_computation_.md)
5. [SIMD Data Access](05_simd_data_access_.md)
```

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)