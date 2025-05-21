```markdown
# Chapter 3: Working with Multiple Dimensions: `IndexList`

In the previous chapters, we explored some of Mojo's fundamental building blocks for memory management, like `AddressSpace` for understanding different memory regions and `UnsafePointer` for directly accessing memory locations. Now, we're going to shift our focus to a common task in programming, especially in fields like graphics, scientific computing, and AI: working with multi-dimensional data.

Imagine you're working with an image. An image is 2-dimensional (it has a width and a height). To specify a single pixel in that image, you need two numbers: a row and a column. Or, think about a 3D model; you'd need three coordinates (x, y, z) to define a point in space.

Mojo provides a handy tool for exactly this: `IndexList`.

## What is `IndexList`?

`IndexList` is a **fixed-size list**, much like a tuple in Python. Its primary job is to represent **multi-dimensional coordinates (indices)** or the **shape of an N-dimensional array**.

Think of it like this:
*   **Coordinates on a map**: If you have a 2D map (like an image), an `IndexList` could hold `(row, column)` to pinpoint a specific location (a pixel).
*   **Dimensions of a box**: If you have a 3D box (like a 3D array of data), an `IndexList` could hold `(depth, height, width)` to describe its size.

It's a simple but powerful structure that helps us talk about locations and sizes in multi-dimensional spaces. As we'll see in later chapters, `IndexList` is used internally by more complex types like `NDBuffer` (Mojo's N-dimensional buffer, similar to a NumPy array or a tensor) to store its dimensions and the "strides" that help calculate memory offsets.

## Why Do We Need `IndexList`?

You might wonder, "Can't I just use a regular tuple of integers?" While you could, `IndexList` offers several advantages:

1.  **Clarity and Type Safety**: Using `IndexList` makes your code more explicit about its intent. When you see an `IndexList`, you know it represents a set of indices or a shape. This is clearer than a generic tuple. Mojo's type system can also leverage this specificity.
2.  **Fixed Size at Compile Time**: A key feature of `IndexList` is that its size (the number of dimensions it holds) is known when your Mojo program is compiled. This allows Mojo to perform many optimizations for better performance.
3.  **Specialized Operations**: `IndexList` is designed for working with indices and comes with useful built-in functionalities like element-wise arithmetic and type casting.

## Creating an `IndexList`

There are a couple of common ways to create an `IndexList`.

### 1. Direct Initialization: `IndexList[size](...)`

You can directly create an `IndexList` by specifying its `size` (the number of elements it will hold) as a compile-time parameter, and then providing the values.

```mojo
from utils import IndexList
from builtin import DType // For specifying element types

fn main_direct_init():
    // A 2D coordinate (e.g., row, column)
    // Size is 2. Elements are (by default) 64-bit integers.
    var coord2d = IndexList[2](10, 25)
    print("2D Coordinate:", coord2d) // Output: (10, 25)

    // A 3D shape (e.g., depth, height, width)
    // Size is 3.
    var shape3d = IndexList[3](3, 64, 128)
    print("3D Shape:", shape3d) // Output: (3, 64, 128)

    // You can also specify the element type.
    // Here, we use 32-bit integers.
    var coord2d_int32 = IndexList[2, element_type=DType.int32](5, 15)
    print("2D Coordinate (Int32):", coord2d_int32) // Output: (5, 15)
```

*   `IndexList[size]`: `size` is a compile-time constant telling Mojo how many elements this list will hold.
*   `element_type`: This optional parameter specifies the data type of the numbers within the `IndexList`. If you don't specify it, it defaults to `DType.int64` (a 64-bit integer). `IndexList` is designed to hold integral types.

### 2. Using the `Index()` Factory Function

Mojo also provides a convenient `Index()` factory function (which you import from `utils`) that often feels more natural, especially if you're used to Python. It infers the size from the number of arguments you provide.

```mojo
from utils import Index, IndexList // IndexList is often good to have for type annotations
from builtin import DType

fn main_factory_func():
    // The Index() function infers the size
    var point_a = Index(100, 200) // Creates an IndexList[2]
    print("Point A:", point_a)     // Output: (100, 200)

    var dimensions = Index(800, 600, 3) // Creates an IndexList[3]
    print("Dimensions:", dimensions)      // Output: (800, 600, 3)

    // You can also specify the element type with Index()
    var point_b_int32 = Index[dtype=DType.int32](50, 75)
    print("Point B (Int32):", point_b_int32) // Output: (50, 75)
```
The `Index()` function is often a more concise way to create `IndexList` instances.

## Working with `IndexList`

Once you have an `IndexList`, here are some common things you can do:

### Accessing Elements

You can access individual elements of an `IndexList` using the square bracket `[]` operator, just like with Python lists or tuples. Indexing starts at 0.

```mojo
from utils import Index

fn main_access_elements():
    var my_coords = Index(15, 30, 45) // An IndexList[3]

    var x = my_coords[0] // Get the first element
    var y = my_coords[1] // Get the second element
    var z = my_coords[2] // Get the third element

    print("X:", x) // Output: X: 15
    print("Y:", y) // Output: Y: 30
    print("Z:", z) // Output: Z: 45

    // You can also modify elements if the IndexList is mutable (declared with `var`)
    my_coords[0] = 16
    print("Modified X:", my_coords[0]) // Output: Modified X: 16
```

### Getting the Length (Size)

The `len()` function tells you how many elements are in the `IndexList` (which matches the `size` parameter it was created with).

```mojo
from utils import Index

fn main_get_length():
    var coord2d = Index(10, 20)
    var shape3d = Index(5, 8, 12)

    print("Length of coord2d:", len(coord2d)) // Output: Length of coord2d: 2
    print("Length of shape3d:", len(shape3d)) // Output: Length of shape3d: 3
```

### Converting to String (Printing)

`IndexList` knows how to represent itself as a string, so you can easily print it.

```mojo
from utils import Index, IndexList

fn main_to_string():
    var il_multi = Index(1, 2, 3)
    print(il_multi) // Output: (1, 2, 3)

    // For single-element IndexLists, it prints with a trailing comma,
    // just like single-element tuples in Python.
    var il_single = IndexList[1](42)
    print(il_single) // Output: (42,)
```

### Comparing `IndexList`s

You can compare two `IndexList`s for equality (`==`) or inequality (`!=`). The comparison is element-wise: two `IndexList`s are equal if they have the same size and all their corresponding elements are equal.

```mojo
from utils import Index

fn main_compare():
    var p1 = Index(10, 20)
    var p2 = Index(10, 20)
    var p3 = Index(10, 30)

    if p1 == p2:
        print("p1 is equal to p2") // This will print
    else:
        print("p1 is not equal to p2")

    if p1 == p3:
        print("p1 is equal to p3")
    else:
        print("p1 is not equal to p3") // This will print
```
`IndexList` also supports other comparison operators like `<`, `<=`, `>`, `>=`. These also perform element-wise comparisons, meaning *all* elements must satisfy the condition for the overall result to be true (this is different from a lexicographical comparison you might see in Python tuples).

### Casting Element Types

Sometimes, you might have an `IndexList` with one integer type (e.g., `DType.int64`) but need to convert it to another (e.g., `DType.int32`). The `cast[NewDType]()` method lets you do this.

```mojo
from utils import Index
from builtin import DType

fn main_casting():
    var original_indices = Index(100, 200, -50) // Default DType.int64
    print("Original:", original_indices)

    // Cast to DType.int32
    var casted_indices_i32 = original_indices.cast[DType.int32]()
    print("Casted to Int32:", casted_indices_i32)
    // Note: The print output looks the same, but internally
    // the elements are now 32-bit integers.

    // Cast to DType.uint64 (unsigned 64-bit integer)
    // Be careful with signed to unsigned casts if there are negative numbers!
    // For positive numbers, it's usually fine.
    var positive_indices = Index(5, 10)
    var casted_indices_u64 = positive_indices.cast[DType.uint64]()
    print("Casted to UInt64:", casted_indices_u64)
```
Casting is useful when interfacing with functions or data structures that expect indices of a particular integer type.

### Arithmetic Operations

`IndexList` supports element-wise arithmetic operations like addition (`+`), subtraction (`-`), multiplication (`*`), and floor division (`//`).

```mojo
from utils import Index

fn main_arithmetic():
    var v1 = Index(10, 20, 30)
    var v2 = Index(2,  3,  4)

    var sum_v = v1 + v2
    print("v1 + v2 =", sum_v) // Output: v1 + v2 = (12, 23, 34)

    var diff_v = v1 - v2
    print("v1 - v2 =", diff_v) // Output: v1 - v2 = (8, 17, 26)

    var prod_v = v1 * v2
    print("v1 * v2 =", prod_v) // Output: v1 * v2 = (20, 60, 120)

    var div_v = v1 // v2
    print("v1 // v2 =", div_v) // Output: v1 // v2 = (5, 6, 7)
```
These operations create a new `IndexList` containing the results.

## A Practical Example

Let's put some of these concepts together. Imagine we're working with a 2D grid.

```mojo
from utils import Index, IndexList
from builtin import DType

fn main():
    print("--- IndexList Practical Example ---")

    # Define the starting coordinates of an object on a grid
    var start_pos = Index(5, 10) # An IndexList[2] of Int64
    print("Starting position:", start_pos)

    # Define a movement vector
    var move_vector = Index(3, -2)
    print("Movement vector:", move_vector)

    # Calculate the new position by adding the start_pos and move_vector
    var end_pos = start_pos + move_vector
    print("Ending position:", end_pos) # Expected: (5+3, 10-2) = (8, 8)

    # Define the dimensions of a small tile
    var tile_shape = IndexList[2, element_type=DType.int32](16, 16)
    print("Tile shape (Int32):", tile_shape)

    # Access elements
    print("Starting X:", start_pos[0])
    print("Starting Y:", start_pos[1])
    print("Tile width:", tile_shape[0])

    # Check length
    print("Dimensions in start_pos:", len(start_pos))

    print("--- End of Practical Example ---")

```

## Key Takeaways

*   `IndexList` is a **fixed-size list** (like a tuple) used for representing **multi-dimensional indices** or **shapes**.
*   Its size is a **compile-time parameter**, enabling optimizations: `IndexList[size](...)`.
*   The `Index(...)` factory function is a convenient way to create them, inferring the size.
*   Elements are accessed using `[]` (e.g., `my_list[0]`).
*   Supports common operations: `len()`, string conversion, comparisons (`==`, `!=`, etc.), type casting (`.cast[DType]()`), and element-wise arithmetic (`+`, `-`, `*`, `//`).
*   It plays a crucial role in defining and accessing data in multi-dimensional structures like `NDBuffer`.

## What's Next?

Understanding `IndexList` is a stepping stone. It helps us define how many dimensions something has and what its size is in each of those dimensions. In the upcoming chapters, we'll see how types like `DimList` (another way to describe dimensions, often with more static information) and ultimately `NDBuffer` build upon these concepts to provide powerful ways to work with N-dimensional data in Mojo.

---
**Index of Chapters (So Far):**
1. [Chapter 1: Understanding Memory Neighborhoods with `AddressSpace`](01_addressspace_.md)
2. [Chapter 2: Peeking into Memory with `UnsafePointer`](02_unsafepointer_.md)
3. **Chapter 3: Working with Multiple Dimensions: `IndexList`** (You are here)
4. _Coming Soon: Chapter 4: Describing Dimensions: `DimList`_
5. _Coming Soon: Chapter 5: The N-Dimensional Buffer: `NDBuffer`_
6. _Coming Soon: Chapter 6: N-D to 1D Indexing Logic (Strided Memory Access)_
```

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)