---
layout: default
title: "Chapter 2: DimList and Dim"
parent: "My Tutorial for Mojo v2"
nav_order: 2
---
Okay, here's Chapter 2 of the Mojo tutorial, focusing on `DimList` and `Dim`, designed to be very beginner-friendly.

# Chapter 2: Defining Dimensions - `Dim` and `DimList`

In [Chapter 1: Meet `UnsafePointer`](01_unsafepointer__as_used_by_ndbuffer__.md), we learned that `NDBuffer` uses an `UnsafePointer` (its `data` field) to know the starting memory address of its data. This tells `NDBuffer` *where* its numbers, pixels, or other elements begin in the computer's memory.

But just knowing *where* data starts isn't enough. If you have a block of memory, how do you know if it represents:
*   A simple list of 10 numbers? (`[1, 2, ..., 10]`)
*   A 2x5 grid of numbers?
    ```
    1, 2, 3, 4, 5
    6, 7, 8, 9, 10
    ```
*   Or even a 3D cube of data?

To make sense of the raw data pointed to by `UnsafePointer`, `NDBuffer` needs to understand its **structure** or **shape**. It also needs to know how elements are laid out in memory, which involves something called **strides**. For these crucial pieces of information, Mojo uses two important building blocks: `Dim` and `DimList`.

As the project description states:
> `DimList` is a compile-time list that holds dimension-related information, primarily used for an `NDBuffer`'s shape and strides. Each element in a `DimList` is a `Dim`. A `Dim` object can represent either a statically known integer value (e.g., a dimension of size 3, known at compile time) or an unknown value (dynamic size) that will only be determined at runtime. This design allows `NDBuffer` to be flexible, supporting both fully static and partially or fully dynamic tensor shapes and strides.

Let's break these down.

## `Dim`: A Single Dimension's Story

Imagine you're describing one side of a box. That side has a length.
A `Dim` in Mojo represents the size of a single dimension. This "size" can be:

1.  **Statically Known**: The size is a specific, fixed number known when you write your code and when Mojo compiles it. For example, a dimension of size `5`.
2.  **Dynamically Known**: The size isn't known until your program is actually running. It might depend on user input, a file being read, or calculations done earlier in the program. Mojo uses a special internal marker (a `_sentinel` value, which is `-31337` in the `stdlib/src/buffer/dimlist.mojo` code) to represent this "unknown for now" state.

Think of it like this:
*   `Dim(5)` means "This dimension definitely has a size of 5."
*   `Dim()` means "The size of this dimension is currently unknown; we'll find out at runtime."

### Creating and Using `Dim`

Let's look at how you work with `Dim` objects. The code for `Dim` can be found in `stdlib/src/buffer/dimlist.mojo`.

```mojo
// First, you'd typically import Dim if you're using it directly
// (though often it's used implicitly through DimList and NDBuffer)
// from buffer import Dim // We'll assume this for standalone examples

// Creating Dims
let static_dim = Dim(5)    // A dimension known to be 5 at compile time
let another_static_dim: Dim = 10 // You can also assign integers directly
let dynamic_dim = Dim()    // A dimension whose size is unknown at compile time

// Printing Dims
print("Static Dim:", static_dim)       // Output: Static Dim: 5
print("Dynamic Dim:", dynamic_dim)     // Output: Dynamic Dim: ?

// Checking if a Dim has a static value
if static_dim.has_value():
    print("static_dim has a value.") // This will print
else:
    print("static_dim is dynamic.")

if dynamic_dim.has_value():
    print("dynamic_dim has a value.")
else:
    print("dynamic_dim is dynamic.") // This will print

// You can also use a Dim directly in a boolean context
if static_dim: // This is true if static_dim.has_value() is true
    print("static_dim evaluates to true (it has a value).")

if dynamic_dim:
    print("dynamic_dim evaluates to true.")
else:
    print("dynamic_dim evaluates to false (it's dynamic).")


// Getting the static value
if static_dim:
    print("Value of static_dim:", static_dim.get()) // Output: Value of static_dim: 5

// What if you try to .get() a dynamic dimension?
// print(dynamic_dim.get()) // This would give the internal sentinel value (-31337).
// It's safer to check first, or use or_else:
let dynamic_val_or_default = dynamic_dim.or_else(1) // If dynamic_dim is dynamic, use 1
print("Dynamic value or default:", dynamic_val_or_default) // Output: Dynamic value or default: 1

// Checking if a dimension is dynamic
if dynamic_dim.is_dynamic():
    print("dynamic_dim is indeed dynamic!") // This will print
```

**Key `Dim` features to remember:**
*   **Creation**: `Dim(number)` for static, `Dim()` for dynamic.
*   **Checking**: `has_value()` (or just `if my_dim:`) tells you if it's static. `is_dynamic()` tells you if it's dynamic.
*   **Getting Value**: `get()` retrieves the static value. Be cautious and check `has_value()` first, or use `or_else(default_value)`.
*   **String Representation**: Prints as the number if static, or `?` if dynamic.

The `Dim` struct (defined with `@value struct Dim(...)` in the source code) is designed to be very efficient, especially when its value is known at compile time.

## `DimList`: A Collection of Dimensions

Now that we understand a single `Dim`, `DimList` is straightforward: it's a list of `Dim` objects.

> Imagine `DimList` as the blueprint for the dimensions of a container. Each `Dim` in the list specifies a particular dimension's size, like length, width, or height. Some of these might be fixed values written directly on the blueprint (e.g., "length is 5 units"), while others might be placeholders (e.g., "width is N units, to be measured on-site"). `DimList` collects all these specifications.

For an `NDBuffer`, `DimList` is used for two main things:
1.  **Shape**: Describes the size of the `NDBuffer` in each dimension (e.g., number of rows, number of columns, number of channels).
2.  **Strides**: Describes how many elements you need to "skip" in memory to move from one element to the next along a particular dimension. (We'll cover strides in more detail in a later chapter).

### Creating and Using `DimList`

Let's see how to create and use `DimList`. The code for `DimList` is also in `stdlib/src/buffer/dimlist.mojo`.

```mojo
// from buffer import Dim, DimList // Assuming imports

// --- Creating DimLists ---

// For a 2D shape like 3 rows, 4 columns (all static)
let static_shape_A = DimList(3, 4)
print("Static Shape A:", static_shape_A) // Output: Static Shape A: [3, 4]

// You can also be explicit with Dims
let static_shape_B = DimList(Dim(3), Dim(4))
print("Static Shape B:", static_shape_B) // Output: Static Shape B: [3, 4]

// For a 3D shape: 10 depth, dynamic height, 5 width
let mixed_shape = DimList(10, Dim(), 5)
print("Mixed Shape:", mixed_shape) // Output: Mixed Shape: [10, ?, 5]

// For a 2D shape where both dimensions are dynamic.
// Let's say the rank (number of dimensions) is 2.
let dynamic_shape_rank2 = DimList.create_unknown[2]()
print("Dynamic Shape (Rank 2):", dynamic_shape_rank2) // Output: Dynamic Shape (Rank 2): [?, ?]

// --- Using DimLists ---

// Getting the length (number of dimensions, or rank)
print("Rank of static_shape_A:", len(static_shape_A)) // Output: Rank of static_shape_A: 2
print("Rank of mixed_shape:", len(mixed_shape))       // Output: Rank of mixed_shape: 3

// Accessing a specific Dim at an index (0-based)
let first_dim_of_mixed = mixed_shape.at[0]()
print("First Dim of mixed_shape:", first_dim_of_mixed) // Output: First Dim of mixed_shape: 10

let second_dim_of_mixed = mixed_shape.at[1]()
print("Second Dim of mixed_shape:", second_dim_of_mixed) // Output: Second Dim of mixed_shape: ?

// Checking if a Dim at an index has a static value
print("Is 1st dim of mixed_shape static?", mixed_shape.has_value[0]()) // Output: true
print("Is 2nd dim of mixed_shape static?", mixed_shape.has_value[1]()) // Output: false

// Getting the static value of a Dim at an index (if it's static)
if mixed_shape.has_value[0]():
    print("Value of 1st dim of mixed_shape:", mixed_shape.get[0]()) // Output: 10

// Checking if ALL dimensions in a DimList are statically known
if static_shape_A.all_known[len(static_shape_A)](): // or simply static_shape_A.all_known() in newer Mojo
    print("static_shape_A has all known dimensions.") // This will print

if mixed_shape.all_known[len(mixed_shape)]():
    print("mixed_shape has all known dimensions.")
else:
    print("mixed_shape has at least one dynamic dimension.") // This will print

// Calculating the product of dimensions (e.g., total number of elements)
let product_static = static_shape_A.product()
print("Product of static_shape_A:", product_static) // Output: Product of static_shape_A: 12 (Dim(12))
if product_static:
    print("Value:", product_static.get()) // Output: Value: 12


let product_mixed = mixed_shape.product()
print("Product of mixed_shape:", product_mixed) // Output: Product of mixed_shape: ? (Dim())
if product_mixed.is_dynamic():
    print("Product is dynamic because at least one dimension was dynamic.")
```

**Key `DimList` features to remember:**
*   **Stores `Dim`s**: It's a specialized list for holding dimension information.
*   **Static & Dynamic Mix**: Can hold any combination of static and dynamic `Dim`s.
*   `DimList.create_unknown[RANK]()`: A handy way to make a `DimList` where all dimensions are dynamic for a given `RANK`.
*   `at[INDEX]()`: Gets the `Dim` object at a specific index.
*   `get[INDEX]()`: Gets the *value* of the `Dim` at that index (if static).
*   `product()`: Computes the product of all dimensions. If any `Dim` in the list is dynamic, the resulting product `Dim` will also be dynamic (represented as `?`).

## `DimList` in Action: `NDBuffer`'s Shape and Strides

Now, let's see how `DimList` and `Dim` are fundamental to `NDBuffer`. If we look at the definition of `NDBuffer` in `stdlib/src/buffer/buffer.mojo` (simplified):

```mojo
// Simplified NDBuffer definition from stdlib/src/buffer/buffer.mojo
struct NDBuffer[
    mut: Bool,
    type: DType,
    rank: Int,
    origin: Origin[mut],
    // Here they are!
    shape: DimList = DimList.create_unknown[rank](),
    strides: DimList = DimList.create_unknown[rank](),
    *,
    // ... other parameters ...
]{
    var data: UnsafePointer[...];
    var dynamic_shape: IndexList[rank, ...];
    var dynamic_stride: IndexList[rank, ...];
    // ...
}
```

Notice the `shape: DimList` and `strides: DimList` parameters in the `NDBuffer` definition.
*   `shape: DimList`: This `DimList` tells the `NDBuffer` its size in each of its `rank` dimensions.
*   `strides: DimList`: This `DimList` tells the `NDBuffer` how to navigate its data in memory. (More on this in a future chapter!)

By default, if you don't specify them, `shape` and `strides` are `DimList.create_unknown[rank]()`, meaning all dimensions and strides are initially considered dynamic.

When you create or work with an `NDBuffer`, you might provide these `DimList`s:
*   If `shape` has all static `Dim`s (e.g., `DimList(100, 200)` for a 2D buffer), Mojo knows the exact size of the buffer at compile time.
*   If `shape` has some dynamic `Dim`s (e.g., `DimList(Dim(100), Dim())`), Mojo knows some dimensions statically and will figure out others at runtime. The actual runtime values for dynamic dimensions are stored in fields like `dynamic_shape` inside the `NDBuffer`.

## Why Static vs. Dynamic Matters So Much

This ability to mix static and dynamic dimensions is a superpower of Mojo:

1.  **Flexibility**: You can write code that works with data of varying sizes, where those sizes aren't known until your program runs. This is essential for real-world applications.
2.  **Performance**: When dimension sizes *are* known statically (at compile time), Mojo can perform powerful optimizations. It can unroll loops, pre-calculate memory offsets, and generate highly specialized machine code. This often leads to significantly faster execution compared to situations where all sizes are only known dynamically.

`Dim` and `DimList` are the mechanisms that allow Mojo developers to communicate this static-or-dynamic information to the compiler, enabling this blend of flexibility and performance.

## Key Takeaways for Chapter 2

*   A `Dim` represents a single dimension's size, which can be **statically known** (a fixed number) or **dynamic** (unknown until runtime, represented as `?`).
*   `DimList` is a list of `Dim`s, used by `NDBuffer` to define its `shape` (size in each dimension) and `strides` (memory layout).
*   You can create `DimList`s with all static dimensions (`DimList(2,3,4)`), all dynamic dimensions (`DimList.create_unknown[3]()`), or a mix (`DimList(2, Dim(), 4)`).
*   If any `Dim` in a `DimList` is dynamic, operations like `product()` on that `DimList` will result in a dynamic `Dim` (`?`).
*   This static/dynamic system allows `NDBuffer` (and Mojo in general) to be both **flexible** (handling runtime-determined sizes) and **performant** (optimizing heavily when sizes are compile-time known).

## What's Next?

We've now seen how `NDBuffer` knows *where* its data starts (`UnsafePointer`) and how it understands the *intended structure* of that data (`DimList` for shape).
In the next chapter, [Chapter 3: NDBuffer](03_ndbuffer_.md), we'll take a closer look at the `NDBuffer` struct itself, how it's initialized with these components, and how you start actually using it to access and manipulate N-dimensional data.

---
_Navigation_
1. [UnsafePointer (as used by NDBuffer)](01_unsafepointer__as_used_by_ndbuffer__.md)
2. **DimList and Dim (You are here)**
3. [NDBuffer](03_ndbuffer_.md)
4. [Strides and Offset Computation](04_strides_and_offset_computation_.md)
5. [SIMD Data Access](05_simd_data_access_.md)
```

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)