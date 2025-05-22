# Chapter 2: Peeking into Memory with `UnsafePointer`

Welcome back! In [Chapter 1: Understanding Memory Neighborhoods with `AddressSpace`](01_addressspace_.md), we learned how Mojo categorizes memory into different "neighborhoods" using `AddressSpace`. This helps Mojo optimize how data is handled, especially with hardware like GPUs.

Now, we're going to zoom in and look at how Mojo can directly refer to a specific spot in memory. Get ready to meet `UnsafePointer`!

## What's a Pointer Anyway?

Imagine you have a giant warehouse full of mailboxes (this is your computer's memory). Each mailbox has a unique address. A **pointer** is like a slip of paper that holds the address of one specific mailbox. It doesn't hold the mail (the data) itself, but it tells you *where* to find the mail.

An `UnsafePointer` in Mojo is exactly this: a raw, direct reference to a location in memory. It stores the memory address where some data begins.

The `NDBuffer` type we'll explore later uses an `UnsafePointer` internally (in its `data` field) to know the starting memory address of the data it manages.

## Why "Unsafe"?

The "unsafe" part of `UnsafePointer` is a bit like having a very precise GPS coordinate but no map, no road signs, and no safety barriers.
*   **No Automatic Memory Management**: If you ask for memory using an `UnsafePointer` (like reserving a mailbox), Mojo won't automatically clean it up for you when you're done. You have to do it manually. Forget, and you get a "memory leak" (mailboxes that are reserved but unused, eventually running out of space).
*   **No Automatic Bounds Checking**: If you have a pointer to a mailbox and you try to access the mailbox 10 doors down, but you only reserved the first one, `UnsafePointer` won't stop you. This can lead to reading garbage data or corrupting other data, often causing your program to crash or behave strangely.
*   **No Automatic Initialization**: When you get memory, it's just raw space. An `UnsafePointer` won't ensure it contains meaningful data until you explicitly put something there.

`UnsafePointer` gives you maximum control and performance by stripping away these safety nets. This is powerful but means *you*, the programmer, are responsible for using it correctly.

## Meet `UnsafePointer[T]`

In Mojo, an `UnsafePointer` is always tied to a specific data **type**. You'd write `UnsafePointer[Int]` for a pointer to an integer, or `UnsafePointer[String]` for a pointer to a string. The `T` in `UnsafePointer[T]` tells Mojo what kind of data to expect at that memory address.

Let's look at its definition from `stdlib/src/memory/unsafe_pointer.mojo` (simplified):

```mojo
@register_passable("trivial")
struct UnsafePointer[
    type: AnyType, // The type of data it points to (e.g., Int, Float32)
    *,
    address_space: AddressSpace = AddressSpace.GENERIC, // Where is this memory? (from Ch 1)
    alignment: Int = _default_alignment[type](),    // How data is arranged for efficiency
    mut: Bool = True,                                // Can we change the data via this pointer?
    origin: Origin[mut] = Origin[mut].cast_from[MutableAnyOrigin].result, // Advanced: Tracks memory validity
](...)
```
Don't worry about all the details yet! The key things are:
*   `type`: What kind of data this pointer "points to."
*   `address_space`: This links back to Chapter 1! It tells Mojo if this memory is in the CPU's main area (`AddressSpace.GENERIC`), on a GPU, etc.
*   `alignment`: A performance detail about how data should be positioned in memory. Usually handled by default.
*   `mut`: Short for "mutable." If `True`, you can change the data the pointer points to.
*   `origin`: An advanced feature for tracking where the memory came from and if it's still valid.

Internally, an `UnsafePointer` just holds the numerical memory address.

## Key Operations with `UnsafePointer`

Let's see how you can use `UnsafePointer`. We'll use examples inspired by `stdlib/test/memory/test_unsafepointer.mojo`.

### 1. Getting Memory: Allocation

To point to new memory, you first need to "allocate" it. This is like reserving one or more mailboxes.
The `alloc()` method is used for this. It needs to know how many items of `type` you want space for.

```mojo
from memory import UnsafePointer

// Allocate memory for 1 integer
var p_int = UnsafePointer[Int].alloc(1)

// Allocate memory for 5 Float32 values
var p_floats = UnsafePointer[Float32].alloc(5)
```
After `alloc()`, `p_int` holds the starting address of a memory block big enough for one `Int`. `p_floats` holds the starting address for five `Float32`s.
**Important**: This memory is **uninitialized**. It contains garbage data.

### 2. Initializing and Writing to Memory

Once you have allocated memory, you need to put meaningful data into it.

*   **For simple types (like `Int`, `Float32`):**
    You can often use the subscript operator `[]` to write values, similar to how you'd use it with an array. `ptr[0]` refers to the first item, `ptr[1]` to the second, and so on. `ptr[]` is a shorthand for `ptr[0]`.

    ```mojo
    // Continuing from above:
    p_int[0] = 100 // Put 100 into the memory p_int points to
    // or p_int[] = 100

    p_floats[0] = 1.0
    p_floats[1] = 2.5
    // ... and so on for p_floats[2] through p_floats[4]
    ```

*   **For more complex types (structs, objects):**
    Mojo provides special methods to initialize the memory location (the "pointee" - what's being pointed to):
    *   `init_pointee_move(value)`: Moves `value` into the memory. The original `value` is no longer valid. This is for types that are `Movable`.
    *   `init_pointee_copy(value)`: Copies `value` into the memory. The original `value` is still valid. This is for types that are `Copyable`.
    *   `init_pointee_explicit_copy(value)`: Similar to copy, for types that require an explicit `.copy()` call.

    Here's an example with a `List[String]` (which is a more complex type) from `stdlib/test/memory/test_unsafepointer.mojo`:
    ```mojo
    from memory import UnsafePointer // Assuming List and String are available
    from collections import List // For List
    // In a real scenario, ensure String is also imported if not built-in for this context

    fn demo_complex_type_init():
        var list_ptr = UnsafePointer[List[String]].alloc(1)
        // Create an empty List[String] and move it into the memory list_ptr points to
        list_ptr.init_pointee_move(List[String]())
        
        // Now list_ptr[0] is an initialized, empty List[String]
        list_ptr[0].append("Hello")
        print(list_ptr[0][0]) // Prints "Hello"

        // Proper cleanup for complex types:
        var taken_list = list_ptr.take_pointee() // Move the list out
        list_ptr.free()                          // Free the raw memory slot
        // taken_list will be destroyed when it goes out of scope, or manage it further.
    ```
    For beginners, knowing these `init_pointee_*` methods exist is important, especially if you work with types beyond simple numbers. The crucial part is that *uninitialized* memory from `alloc()` *must be initialized* before it's reliably read.

### 3. Reading from Memory

To read the value stored at the memory location, you also use the `[]` operator:

```mojo
var my_val = p_int[0] // my_val will be 100, assuming p_int[0] was set to 100
print(p_int[])      // Prints 100

var first_float = p_floats[0] // first_float will be 1.0, assuming p_floats[0] was set to 1.0
print(p_floats[1])          // Prints 2.5, assuming p_floats[1] was set to 2.5
```

### 4. Pointer Arithmetic: Moving Around

You can perform arithmetic on pointers to access adjacent memory locations.
*   `ptr + offset`: Gives a new pointer `offset` elements away from `ptr`.
*   `ptr - offset`: Gives a new pointer `offset` elements before `ptr`.
*   `ptr.offset(idx)`: Another way to get an offset pointer.

```mojo
// Assuming p_floats points to memory for 5 Float32s, initialized earlier
var p_item1 = p_floats + 1 // p_item1 now points to p_floats[1]
print(p_item1[0])        // This is equivalent to p_floats[1]

// You can iterate through allocated memory:
for i in range(5):
    p_floats[i] = Float32(i * 10) // Initialize
for i in range(5):
    print((p_floats + i)[0])    // Read using pointer arithmetic and dereference
    // or simply: print(p_floats[i])
```

### 5. Getting a Pointer to Existing Data

Sometimes, you want a pointer to a variable that already exists. You can use the `UnsafePointer(to=...)` constructor.

```mojo
var my_local_var: Int = 42
var ptr_to_local = UnsafePointer[Int](to=my_local_var)

print(ptr_to_local[]) // Prints 42

// You can modify the original variable through the pointer (if mut is True)
ptr_to_local[] = 50
print(my_local_var) // Prints 50!
```
**Big Safety Note**: This is very "unsafe"! If `my_local_var` goes out of scope (e.g., the function ends) but you still have `ptr_to_local` somewhere, `ptr_to_local` becomes a "dangling pointer." Using it will lead to undefined behavior. The `UnsafePointer` does *not* keep `my_local_var` alive.

### 6. Null Pointers

A null pointer is a pointer that doesn't point to any valid memory location. It's like an address slip that's intentionally blank or points to an invalid address (e.g., address 0).
You can create a null `UnsafePointer`:
```mojo
var null_ptr = UnsafePointer[Int]() // Creates a null pointer
print(null_ptr)                   // Usually prints something like 0x0
```
You can check if a pointer is null. An `UnsafePointer` behaves like `False` in a boolean context if it's null, and `True` if it's not.
```mojo
if null_ptr:
    print("This won't print, null_ptr is null.")
else:
    print("null_ptr is indeed null.")

// Assuming p_int was allocated:
if p_int: 
    print("p_int is not null.")
```
Attempting to read or write through a null pointer will usually crash your program.

### 7. Releasing Memory: `free()`

When you're done with memory you allocated with `alloc()`, you **must** release it using the `free()` method. This returns the "mailboxes" to the system so they can be reused.

```mojo
// After you are finished using p_int and p_floats:
p_int.free()
p_floats.free()
```
If you allocated memory for complex objects (those that might have special cleanup code called a destructor, like `List[String]` in our earlier example), you need to ensure those objects are properly destroyed *before* freeing the raw memory.
*   `ptr.take_pointee()`: Moves the value out of the pointer's location, leaving the memory uninitialized. The moved-out value can then be managed or destroyed according to its own rules.
*   `ptr.destroy_pointee()`: Directly calls the destructor of the object at the pointer's location. This is used when you don't need the value anymore.

For simple types like `Int` or `Float32`, just `free()`-ing the pointer is generally enough as they don't have complex destructors.

```mojo
// For the List[String] example (see full version in section 2):
// After using list_ptr:
// var taken_list = list_ptr.take_pointee() // Or list_ptr.destroy_pointee() if not needed
// list_ptr.free()
```

## The Programmer's Responsibilities (The "Unsafe" Contract)

Using `UnsafePointer` means you agree to:
1.  **Manage Lifetime**: You `alloc`, you `free`. If you get a pointer `to` existing data, ensure the data outlives the pointer.
2.  **Stay In Bounds**: Only access memory you've actually allocated. `ptr[10]` is bad if you only `alloc(5)`.
3.  **Initialize Before Use**: Don't read from `alloc`'d memory until you've put something valid there.
4.  **Handle Null Pointers**: Always check if a pointer could be null before using it, if its validity isn't guaranteed.
5.  **Correctly Destroy Complex Objects**: If pointing to objects with destructors, ensure they are destroyed (e.g., via `take_pointee()` or `destroy_pointee()`) before `free`ing their memory.

Breaking this contract leads to bugs that can be hard to find: crashes, corrupted data, or security vulnerabilities.

## A Complete, Simple Example

Let's tie some of this together with simple integers:

```mojo
from memory import UnsafePointer

fn main():
    print("Chapter 2: UnsafePointer Simple Example")

    # 1. Allocate memory for 3 integers
    # This memory is uninitialized.
    var count = 3
    var int_ptr = UnsafePointer[Int].alloc(count)
    print("Allocated memory for", count, "integers at address:", int_ptr)

    # 2. Initialize the memory locations (pointees)
    # For simple types like Int, we can use direct assignment.
    print("Initializing values...")
    int_ptr[0] = 100
    int_ptr[1] = 200
    int_ptr[2] = 300

    # 3. Read and print the values
    print("Reading values:")
    for i in range(count):
        print("Value at index", i, ":", int_ptr[i])

    # 4. Modify a value
    print("Modifying value at index 1...")
    int_ptr[1] = 250

    # 5. Read and print again
    print("Reading values after modification:")
    for i in range(count):
        print("Value at index", i, ":", int_ptr[i])

    # 6. Free the allocated memory
    # This is crucial!
    print("Freeing memory...")
    int_ptr.free()
    print("Memory freed.")

    # Accessing int_ptr[0] now would be undefined behavior.
    # For example, this might crash or print garbage:
    # print("Trying to access freed memory (DANGEROUS):", int_ptr[0])
```

Run this example (you might need to call `main()` if it's not in a context where `main` runs automatically), and you'll see how you can directly manipulate memory.

## Why Use `UnsafePointer`?

If it's so "unsafe," why does `UnsafePointer` exist?
*   **Building Blocks**: It's a fundamental tool for building safer, higher-level memory abstractions (like `List`, `Dict`, and even `NDBuffer` which uses it internally for its `data` field).
*   **Interfacing with C/C++**: When calling code written in languages like C or C++, you often deal with raw pointers.
*   **Ultimate Performance**: In rare, performance-critical situations, direct memory control can eke out the last bits of speed, but only if you know *exactly* what you're doing.

For most everyday Mojo programming, you'll use safer abstractions. But understanding `UnsafePointer` gives you insight into what's happening "under the hood."

## Summary

*   `UnsafePointer[T]` gives you a direct, raw memory address for data of type `T`.
*   It's "unsafe" because it bypasses automatic memory management and bounds checking, making you responsible for correctness.
*   Key operations include `alloc` (get memory), `[]` (read/write), `init_pointee_*` (initialize complex types), `take_pointee`/`destroy_pointee` (handle complex type cleanup), and `free` (release memory).
*   It's crucial for low-level programming, interfacing with C, and building higher-level types.

## Next Steps

We've seen how `AddressSpace` tells us about memory "neighborhoods" and `UnsafePointer` gives us a specific "street address." These are low-level concepts. Next, we'll start looking at how Mojo builds more structured and often safer ways to handle collections of data, which often use these fundamental tools internally. We'll begin by exploring `IndexList`, a helper for working with multi-dimensional indices, essential for understanding types like `NDBuffer`.

---
1. [Chapter 1: Understanding Memory Neighborhoods with `AddressSpace`](01_addressspace_.md)
2. **Chapter 2: Peeking into Memory with `UnsafePointer`** (You are here)
3. [Chapter 3: Working with Multiple Dimensions: `IndexList`](03_indexlist_.md)
4. [Chapter 4: Describing Dimensions: `DimList`](04_dimlist_.md)
5. [Chapter 5: The N-Dimensional Buffer: `NDBuffer`](05_ndbuffer_.md)
6. [Chapter 6: N-D to 1D Indexing Logic (Strided Memory Access)](06_n_d_to_1d_indexing_logic__strided_memory_access__.md)

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)