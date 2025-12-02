"""
Funciones auxiliares para el sistema Neural Algorithmix.

Incluye generacion de datasets de ejemplo y funciones de visualizacion.
"""

from typing import List, Dict, Any


def create_sample_dataset() -> List[Dict[str, Any]]:
    """
    Crea un dataset de ejemplo para entrenamiento.
    
    Etiquetas:
    - 0: O(1)       Constante
    - 1: O(log n)   Logaritmica
    - 2: O(n)       Lineal
    - 3: O(n log n) Linearitmica
    - 4: O(n^2)     Cuadratica
    - 5: O(n^3)     Cubica
    - 6: O(2^n)     Exponencial
    
    Returns:
        Lista de diccionarios con 'code' y 'complexity'.
    """
    return [
        # O(1) - Constante
        {'code': 'return a + b', 'complexity': 0},
        {'code': 'x = array[0]\nreturn x', 'complexity': 0},
        {'code': 'if n > 0:\n    return True\nelse:\n    return False', 'complexity': 0},
        {'code': 'return array[index]', 'complexity': 0},
        {'code': 'temp = a\na = b\nb = temp', 'complexity': 0},
        
        # O(log n) - Logaritmica
        {'code': '''
def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
        ''', 'complexity': 1},
        {'code': '''
while n > 1:
    n = n // 2
    count += 1
        ''', 'complexity': 1},
        {'code': '''
while low <= high:
    mid = low + (high - low) // 2
    if arr[mid] == x:
        return mid
    elif arr[mid] < x:
        low = mid + 1
    else:
        high = mid - 1
        ''', 'complexity': 1},
        
        # O(n) - Lineal
        {'code': '''
for i in range(n):
    sum += arr[i]
return sum
        ''', 'complexity': 2},
        {'code': '''
def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1
        ''', 'complexity': 2},
        {'code': '''
for i in range(0, n):
    if A[i] > max:
        max = A[i]
return max
        ''', 'complexity': 2},
        {'code': '''
count = 0
for item in array:
    if item > threshold:
        count += 1
return count
        ''', 'complexity': 2},
        {'code': '''
result = []
for i in range(n):
    result.append(arr[i] * 2)
return result
        ''', 'complexity': 2},
        
        # O(n log n) - Linearitmica
        {'code': '''
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)
        ''', 'complexity': 3},
        {'code': '''
def quick_sort(arr, low, high):
    if low < high:
        pivot = partition(arr, low, high)
        quick_sort(arr, low, pivot - 1)
        quick_sort(arr, pivot + 1, high)
        ''', 'complexity': 3},
        {'code': '''
def heap_sort(arr):
    build_heap(arr)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, 0, i)
        ''', 'complexity': 3},
        
        # O(n^2) - Cuadratica
        {'code': '''
for i in range(n):
    for j in range(n):
        if arr[j] > arr[j + 1]:
            arr[j], arr[j + 1] = arr[j + 1], arr[j]
        ''', 'complexity': 4},
        {'code': '''
INSERTION-SORT(A, n)
    for j = 2 to n
        key = A[j]
        i = j - 1
        while i > 0 and A[i] > key
            A[i + 1] = A[i]
            i = i - 1
        A[i + 1] = key
        ''', 'complexity': 4},
        {'code': '''
for i in range(n):
    min_idx = i
    for j in range(i + 1, n):
        if arr[j] < arr[min_idx]:
            min_idx = j
    arr[i], arr[min_idx] = arr[min_idx], arr[i]
        ''', 'complexity': 4},
        {'code': '''
for i in range(0, n):
    for j in range(0, n):
        C[i][j] = A[i][j] + B[i][j]
        ''', 'complexity': 4},
        {'code': '''
BUBBLE-SORT(A, n)
    for i = 1 to n - 1
        for j = 1 to n - i
            if A[j] > A[j + 1]
                exchange A[j] with A[j + 1]
        ''', 'complexity': 4},
        {'code': '''
for i in range(n):
    for j in range(i + 1, n):
        if arr[i] == arr[j]:
            duplicates.append(arr[i])
        ''', 'complexity': 4},
        
        # O(n^3) - Cubica
        {'code': '''
for i in range(n):
    for j in range(n):
        for k in range(n):
            C[i][j] += A[i][k] * B[k][j]
        ''', 'complexity': 5},
        {'code': '''
for i in range(n):
    for j in range(n):
        for k in range(n):
            sum += arr[i][j][k]
        ''', 'complexity': 5},
        {'code': '''
def floyd_warshall(graph):
    for k in range(n):
        for i in range(n):
            for j in range(n):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
        ''', 'complexity': 5},
        
        # O(2^n) - Exponencial
        {'code': '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
        ''', 'complexity': 6},
        {'code': '''
def subsets(arr, index, current):
    if index == len(arr):
        print(current)
        return
    subsets(arr, index + 1, current)
    subsets(arr, index + 1, current + [arr[index]])
        ''', 'complexity': 6},
        {'code': '''
def solve(items, capacity, index):
    if index == 0 or capacity == 0:
        return 0
    if items[index].weight > capacity:
        return solve(items, capacity, index - 1)
    return max(
        items[index].value + solve(items, capacity - items[index].weight, index - 1),
        solve(items, capacity, index - 1)
    )
        ''', 'complexity': 6},
    ]


def create_extended_dataset() -> List[Dict[str, Any]]:
    """
    Crea un dataset extendido con mas ejemplos por clase.
    
    Returns:
        Lista extendida de ejemplos.
    """
    base = create_sample_dataset()
    
    extended = [
        # Mas O(1)
        {'code': 'return n % 2 == 0', 'complexity': 0},
        {'code': 'return hash(key) % table_size', 'complexity': 0},
        {'code': 'stack.push(item)', 'complexity': 0},
        
        # Mas O(log n)
        {'code': '''
def find_power(x, n):
    if n == 0:
        return 1
    if n % 2 == 0:
        half = find_power(x, n // 2)
        return half * half
    else:
        return x * find_power(x, n - 1)
        ''', 'complexity': 1},
        
        # Mas O(n)
        {'code': '''
prev = 0
curr = 1
for i in range(2, n):
    temp = curr
    curr = prev + curr
    prev = temp
return curr
        ''', 'complexity': 2},
        {'code': '''
def reverse_array(arr):
    left = 0
    right = len(arr) - 1
    while left < right:
        arr[left], arr[right] = arr[right], arr[left]
        left += 1
        right -= 1
        ''', 'complexity': 2},
        
        # Mas O(n^2)
        {'code': '''
for i in range(n):
    for j in range(n - i - 1):
        if arr[j] > arr[j + 1]:
            swap(arr, j, j + 1)
        ''', 'complexity': 4},
        
        # Mas O(2^n)
        {'code': '''
def generate_permutations(arr, l, r):
    if l == r:
        print(arr)
    else:
        for i in range(l, r + 1):
            arr[l], arr[i] = arr[i], arr[l]
            generate_permutations(arr, l + 1, r)
            arr[l], arr[i] = arr[i], arr[l]
        ''', 'complexity': 6},
    ]
    
    return base + extended


def get_complexity_distribution(dataset: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calcula la distribucion de clases en un dataset.
    
    Args:
        dataset: Lista de ejemplos.
        
    Returns:
        Diccionario con conteo por clase.
    """
    from .consts import COMPLEXITY_CLASSES
    
    counts = {name: 0 for name in COMPLEXITY_CLASSES.values()}
    
    for item in dataset:
        class_name = COMPLEXITY_CLASSES.get(item['complexity'], 'Unknown')
        counts[class_name] = counts.get(class_name, 0) + 1
    
    return counts


def print_dataset_summary(dataset: List[Dict[str, Any]]) -> None:
    """
    Imprime un resumen del dataset.
    
    Args:
        dataset: Lista de ejemplos.
    """
    distribution = get_complexity_distribution(dataset)
    
    print(f"\nDataset Summary ({len(dataset)} examples)")
    print("-" * 40)
    
    for class_name, count in distribution.items():
        bar = "#" * count
        print(f"  {class_name:12} [{count:2}] {bar}")
