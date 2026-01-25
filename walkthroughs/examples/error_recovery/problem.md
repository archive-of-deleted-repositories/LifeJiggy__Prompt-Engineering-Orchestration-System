# Error Recovery Example

## Problem Statement
A code generation request produces buggy output. How to recover?

## Initial Attempt

```python
def calculate_average(numbers):
    return sum(numbers) / len(numbers)
```

**Issues Found:**
1. Division by zero if list is empty
2. No input validation
3. Doesn't handle non-numeric input

## Self-Critique

### What's Wrong
- Edge case (empty list) not handled
- Type checking missing
- Error messages unclear

### How to Fix
1. Add empty list check
2. Add type validation
3. Include informative error messages

## Recovery Steps

### Step 1: Identify Edge Cases
- Empty list
- Non-numeric values
- None input

### Step 2: Implement Fixes
```python
def calculate_average(numbers):
    if numbers is None:
        raise ValueError("Input cannot be None")
    
    if not isinstance(numbers, (list, tuple)):
        raise TypeError("Input must be a list or tuple")
    
    if len(numbers) == 0:
        raise ValueError("Cannot calculate average of empty list")
    
    if not all(isinstance(n, (int, float)) for n in numbers):
        raise ValueError("All elements must be numeric")
    
    return sum(numbers) / len(numbers)
```

### Step 3: Add Tests
```python
def test_calculate_average():
    assert calculate_average([1, 2, 3]) == 2.0
    assert calculate_average([2.5, 3.5]) == 3.0
    
    try:
        calculate_average([])
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    
    print("All tests passed!")
```

## Final Working Solution

```python
def calculate_average(numbers):
    """Calculate the average of a list of numbers.
    
    Args:
        numbers: List or tuple of numeric values
        
    Returns:
        float: The average value
        
    Raises:
        ValueError: If input is empty or contains non-numeric values
        TypeError: If input is not a list or tuple
    """
    if numbers is None:
        raise ValueError("Input cannot be None")
    
    if not isinstance(numbers, (list, tuple)):
        raise TypeError("Input must be a list or tuple")
    
    if len(numbers) == 0:
        raise ValueError("Cannot calculate average of empty list")
    
    if not all(isinstance(n, (int, float)) for n in numbers):
        raise ValueError("All elements must be numeric")
    
    return sum(numbers) / len(numbers)
```

## Lessons Learned
1. Always consider edge cases
2. Add input validation
3. Include proper error messages
4. Write comprehensive tests
5. Document function behavior
