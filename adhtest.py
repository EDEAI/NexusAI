def bubble_sort(arr):
    n = len(arr)
    # Outer loop for the number of passes
    for i in range(n):
        # Inner loop for comparing adjacent elements
        # The largest element "bubbles" to the end in each pass
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# Test bubble sort
test_array = [64, 34, 25, 12, 22, 11, 90]
print("Before sorting:", test_array)
print("After sorting:", bubble_sort(test_array))