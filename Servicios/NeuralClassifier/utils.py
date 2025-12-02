"""
Funciones auxiliares para el sistema Neural Algorithmix.

Dataset de entrenamiento en pseudocodigo estilo Cormen.
El Parser traduce Cormen -> Python antes de entrenar.

ARCHIVO DE DATOS: Documentos/training_algorithms.json
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path


# Ruta al archivo de algoritmos de entrenamiento
TRAINING_DATA_PATH = Path(__file__).parent.parent.parent / 'Documentos' / 'training_algorithms.json'


COMPLEXITY_MAP = {
    'O(1)': 0,
    'O(log n)': 1,
    'O(n)': 2,
    'O(n log n)': 3,
    'O(n^2)': 4,
    'O(n²)': 4,
    'O(n^3)': 5,
    'O(n³)': 5,
    'O(2^n)': 6,
}


def load_cormen_dataset(filepath: str = None, parser=None) -> List[Dict[str, Any]]:
    """
    Carga dataset desde archivo JSON y traduce Cormen -> Python.
    
    Formato esperado del JSON:
    [
        {"pseudocode": "ALGORITMO(A, n)\\n    ...", "complexity": "O(n^2)"},
        ...
    ]
    
    Args:
        filepath: Ruta al archivo JSON. Por defecto usa Documentos/training_algorithms.json
        parser: Instancia de Parser para traducir. Si es None, usa codigo crudo.
        
    Returns:
        Lista de {'code': python_code, 'complexity': int_label}
    """
    if filepath is None:
        filepath = str(TRAINING_DATA_PATH)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    dataset = []
    for item in raw_data:
        pseudocode = item.get('pseudocode', item.get('code', ''))
        complexity_str = item.get('complexity', 'O(n)')
        
        complexity_label = COMPLEXITY_MAP.get(complexity_str, 2)
        
        if parser is not None:
            try:
                ast_obj = parser.parsear(pseudocode)
                python_code = ast_obj._codigo
            except Exception as e:
                print(f"Warning: Failed to parse, using raw code: {e}")
                python_code = pseudocode
        else:
            python_code = pseudocode
        
        dataset.append({
            'code': python_code,
            'complexity': complexity_label
        })
    
    return dataset


def save_cormen_dataset(dataset: List[Dict[str, Any]], filepath: str):
    """
    Guarda dataset en formato JSON Cormen.
    
    Args:
        dataset: Lista de {'pseudocode': str, 'complexity': str}
        filepath: Ruta de salida.
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)


def create_cormen_dataset() -> List[Dict[str, Any]]:
    """
    Dataset de entrenamiento en pseudocodigo Cormen puro.
    
    Complejidades:
    - 0: O(1)       Constante
    - 1: O(log n)   Logaritmica  
    - 2: O(n)       Lineal
    - 3: O(n log n) Linearitmica
    - 4: O(n^2)     Cuadratica
    - 5: O(n^3)     Cubica
    - 6: O(2^n)     Exponencial
    
    Returns:
        Lista de {'pseudocode': cormen_code, 'complexity': str_label}
    """
    return [
        # =====================================================================
        # O(1) - CONSTANTE
        # =====================================================================
        {
            'pseudocode': '''CONSTANT-ACCESS(A, i)
    return A[i]''',
            'complexity': 'O(1)'
        },
        {
            'pseudocode': '''SWAP(A, i, j)
    temp ← A[i]
    A[i] ← A[j]
    A[j] ← temp''',
            'complexity': 'O(1)'
        },
        {
            'pseudocode': '''GET-MAX(a, b)
    if a > b then
        return a
    else
        return b''',
            'complexity': 'O(1)'
        },
        {
            'pseudocode': '''INCREMENT(x)
    x ← x + 1
    return x''',
            'complexity': 'O(1)'
        },
        {
            'pseudocode': '''IS-EVEN(n)
    if n mod 2 = 0 then
        return true
    else
        return false''',
            'complexity': 'O(1)'
        },
        
        # =====================================================================
        # O(log n) - LOGARITMICA
        # =====================================================================
        {
            'pseudocode': '''BINARY-SEARCH(A, p, r, x)
    if p > r then
        return -1
    q ← (p + r) div 2
    if A[q] = x then
        return q
    else if A[q] > x then
        return BINARY-SEARCH(A, p, q - 1, x)
    else
        return BINARY-SEARCH(A, q + 1, r, x)''',
            'complexity': 'O(log n)'
        },
        {
            'pseudocode': '''ITERATIVE-BINARY-SEARCH(A, n, x)
    low ← 1
    high ← n
    while low ≤ high do
        mid ← (low + high) div 2
        if A[mid] = x then
            return mid
        else if A[mid] < x then
            low ← mid + 1
        else
            high ← mid - 1
    return -1''',
            'complexity': 'O(log n)'
        },
        {
            'pseudocode': '''HALVING(n)
    count ← 0
    while n > 1 do
        n ← n div 2
        count ← count + 1
    return count''',
            'complexity': 'O(log n)'
        },
        {
            'pseudocode': '''POWER(x, n)
    if n = 0 then
        return 1
    if n mod 2 = 0 then
        half ← POWER(x, n div 2)
        return half * half
    else
        return x * POWER(x, n - 1)''',
            'complexity': 'O(log n)'
        },
        
        # =====================================================================
        # O(n) - LINEAL
        # =====================================================================
        {
            'pseudocode': '''LINEAR-SEARCH(A, n, x)
    for i ← 1 to n do
        if A[i] = x then
            return i
    return -1''',
            'complexity': 'O(n)'
        },
        {
            'pseudocode': '''FIND-MAX(A, n)
    max ← A[1]
    for i ← 2 to n do
        if A[i] > max then
            max ← A[i]
    return max''',
            'complexity': 'O(n)'
        },
        {
            'pseudocode': '''SUM-ARRAY(A, n)
    sum ← 0
    for i ← 1 to n do
        sum ← sum + A[i]
    return sum''',
            'complexity': 'O(n)'
        },
        {
            'pseudocode': '''COUNT-ELEMENT(A, n, x)
    count ← 0
    for i ← 1 to n do
        if A[i] = x then
            count ← count + 1
    return count''',
            'complexity': 'O(n)'
        },
        {
            'pseudocode': '''REVERSE-ARRAY(A, n)
    for i ← 1 to n div 2 do
        temp ← A[i]
        A[i] ← A[n - i + 1]
        A[n - i + 1] ← temp''',
            'complexity': 'O(n)'
        },
        {
            'pseudocode': '''FACTORIAL-ITERATIVE(n)
    result ← 1
    for i ← 2 to n do
        result ← result * i
    return result''',
            'complexity': 'O(n)'
        },
        
        # =====================================================================
        # O(n log n) - LINEARITMICA
        # =====================================================================
        {
            'pseudocode': '''MERGE-SORT(A, p, r)
    if p < r then
        q ← (p + r) div 2
        MERGE-SORT(A, p, q)
        MERGE-SORT(A, q + 1, r)
        MERGE(A, p, q, r)''',
            'complexity': 'O(n log n)'
        },
        {
            'pseudocode': '''QUICKSORT(A, p, r)
    if p < r then
        q ← PARTITION(A, p, r)
        QUICKSORT(A, p, q - 1)
        QUICKSORT(A, q + 1, r)''',
            'complexity': 'O(n log n)'
        },
        {
            'pseudocode': '''PARTITION(A, p, r)
    x ← A[r]
    i ← p - 1
    for j ← p to r - 1 do
        if A[j] ≤ x then
            i ← i + 1
            temp ← A[i]
            A[i] ← A[j]
            A[j] ← temp
    temp ← A[i + 1]
    A[i + 1] ← A[r]
    A[r] ← temp
    return i + 1''',
            'complexity': 'O(n)'
        },
        {
            'pseudocode': '''HEAP-SORT(A, n)
    BUILD-MAX-HEAP(A, n)
    for i ← n downto 2 do
        temp ← A[1]
        A[1] ← A[i]
        A[i] ← temp
        MAX-HEAPIFY(A, 1, i - 1)''',
            'complexity': 'O(n log n)'
        },
        {
            'pseudocode': '''MERGE(A, p, q, r)
    n1 ← q - p + 1
    n2 ← r - q
    for i ← 1 to n1 do
        L[i] ← A[p + i - 1]
    for j ← 1 to n2 do
        R[j] ← A[q + j]
    i ← 1
    j ← 1
    for k ← p to r do
        if L[i] ≤ R[j] then
            A[k] ← L[i]
            i ← i + 1
        else
            A[k] ← R[j]
            j ← j + 1''',
            'complexity': 'O(n)'
        },
        
        # =====================================================================
        # O(n^2) - CUADRATICA
        # =====================================================================
        {
            'pseudocode': '''BURBUJA-SORT(A, n)
    for i ← 1 to n - 1 do
        for j ← n downto i + 1 do
            if A[j] < A[j-1] then
                temp ← A[j]
                A[j] ← A[j-1]
                A[j-1] ← temp''',
            'complexity': 'O(n^2)'
        },
        {
            'pseudocode': '''INSERTION-SORT(A, n)
    for j ← 2 to n do
        key ← A[j]
        i ← j - 1
        while i > 0 and A[i] > key do
            A[i + 1] ← A[i]
            i ← i - 1
        A[i + 1] ← key''',
            'complexity': 'O(n^2)'
        },
        {
            'pseudocode': '''SELECTION-SORT(A, n)
    for i ← 1 to n - 1 do
        smallest ← i
        for j ← i + 1 to n do
            if A[j] < A[smallest] then
                smallest ← j
        temp ← A[i]
        A[i] ← A[smallest]
        A[smallest] ← temp''',
            'complexity': 'O(n^2)'
        },
        {
            'pseudocode': '''MATRIX-ADD(A, B, C, n)
    for i ← 1 to n do
        for j ← 1 to n do
            C[i][j] ← A[i][j] + B[i][j]''',
            'complexity': 'O(n^2)'
        },
        {
            'pseudocode': '''FIND-DUPLICATES(A, n)
    count ← 0
    for i ← 1 to n do
        for j ← i + 1 to n do
            if A[i] = A[j] then
                count ← count + 1
    return count''',
            'complexity': 'O(n^2)'
        },
        {
            'pseudocode': '''BUBBLE-SORT-OPTIMIZED(A, n)
    for i ← 1 to n - 1 do
        swapped ← false
        for j ← 1 to n - i do
            if A[j] > A[j + 1] then
                temp ← A[j]
                A[j] ← A[j + 1]
                A[j + 1] ← temp
                swapped ← true
        if swapped = false then
            return''',
            'complexity': 'O(n^2)'
        },
        
        # =====================================================================
        # O(n^3) - CUBICA
        # =====================================================================
        {
            'pseudocode': '''MATRIX-MULTIPLY(A, B, C, n)
    for i ← 1 to n do
        for j ← 1 to n do
            C[i][j] ← 0
            for k ← 1 to n do
                C[i][j] ← C[i][j] + A[i][k] * B[k][j]''',
            'complexity': 'O(n^3)'
        },
        {
            'pseudocode': '''FLOYD-WARSHALL(D, n)
    for k ← 1 to n do
        for i ← 1 to n do
            for j ← 1 to n do
                if D[i][k] + D[k][j] < D[i][j] then
                    D[i][j] ← D[i][k] + D[k][j]''',
            'complexity': 'O(n^3)'
        },
        {
            'pseudocode': '''TRIPLE-SUM(A, n)
    count ← 0
    for i ← 1 to n do
        for j ← 1 to n do
            for k ← 1 to n do
                count ← count + A[i] + A[j] + A[k]
    return count''',
            'complexity': 'O(n^3)'
        },
        
        # =====================================================================
        # O(2^n) - EXPONENCIAL
        # =====================================================================
        {
            'pseudocode': '''FIBONACCI-RECURSIVE(n)
    if n ≤ 1 then
        return n
    return FIBONACCI-RECURSIVE(n - 1) + FIBONACCI-RECURSIVE(n - 2)''',
            'complexity': 'O(2^n)'
        },
        {
            'pseudocode': '''GENERATE-SUBSETS(A, n, index, current)
    if index = n + 1 then
        PRINT(current)
        return
    GENERATE-SUBSETS(A, n, index + 1, current)
    current ← current + A[index]
    GENERATE-SUBSETS(A, n, index + 1, current)''',
            'complexity': 'O(2^n)'
        },
        {
            'pseudocode': '''KNAPSACK-RECURSIVE(W, wt, val, n)
    if n = 0 or W = 0 then
        return 0
    if wt[n] > W then
        return KNAPSACK-RECURSIVE(W, wt, val, n - 1)
    include ← val[n] + KNAPSACK-RECURSIVE(W - wt[n], wt, val, n - 1)
    exclude ← KNAPSACK-RECURSIVE(W, wt, val, n - 1)
    if include > exclude then
        return include
    else
        return exclude''',
            'complexity': 'O(2^n)'
        },
        {
            'pseudocode': '''TOWER-OF-HANOI(n, source, target, auxiliary)
    if n = 1 then
        MOVE(source, target)
        return
    TOWER-OF-HANOI(n - 1, source, auxiliary, target)
    MOVE(source, target)
    TOWER-OF-HANOI(n - 1, auxiliary, target, source)''',
            'complexity': 'O(2^n)'
        },
    ]


def create_sample_dataset() -> List[Dict[str, Any]]:
    """
    Alias de create_cormen_dataset para compatibilidad.
    Retorna dataset en formato listo para entrenar (con 'code' en vez de 'pseudocode').
    
    NOTA: Este dataset contiene pseudocodigo Cormen.
    Debe ser procesado con Parser antes de entrenar.
    """
    cormen = create_cormen_dataset()
    return [
        {'code': item['pseudocode'], 'complexity': COMPLEXITY_MAP[item['complexity']]}
        for item in cormen
    ]


def create_extended_dataset() -> List[Dict[str, Any]]:
    """
    Dataset extendido con variaciones adicionales.
    """
    base = create_cormen_dataset()
    
    extended_cormen = [
        # Mas O(1)
        {
            'pseudocode': '''ARRAY-ACCESS(A, i, j)
    return A[i][j]''',
            'complexity': 'O(1)'
        },
        {
            'pseudocode': '''MIN-OF-TWO(a, b)
    if a < b then
        return a
    return b''',
            'complexity': 'O(1)'
        },
        
        # Mas O(log n)
        {
            'pseudocode': '''FIND-FLOOR(A, n, x)
    low ← 1
    high ← n
    result ← -1
    while low ≤ high do
        mid ← (low + high) div 2
        if A[mid] ≤ x then
            result ← mid
            low ← mid + 1
        else
            high ← mid - 1
    return result''',
            'complexity': 'O(log n)'
        },
        
        # Mas O(n)
        {
            'pseudocode': '''COPY-ARRAY(A, B, n)
    for i ← 1 to n do
        B[i] ← A[i]''',
            'complexity': 'O(n)'
        },
        {
            'pseudocode': '''FIND-MIN-MAX(A, n)
    min ← A[1]
    max ← A[1]
    for i ← 2 to n do
        if A[i] < min then
            min ← A[i]
        if A[i] > max then
            max ← A[i]
    return min, max''',
            'complexity': 'O(n)'
        },
        
        # Mas O(n^2)
        {
            'pseudocode': '''PRINT-PAIRS(A, n)
    for i ← 1 to n do
        for j ← 1 to n do
            PRINT(A[i], A[j])''',
            'complexity': 'O(n^2)'
        },
        {
            'pseudocode': '''TWO-SUM-NAIVE(A, n, target)
    for i ← 1 to n do
        for j ← i + 1 to n do
            if A[i] + A[j] = target then
                return i, j
    return -1, -1''',
            'complexity': 'O(n^2)'
        },
    ]
    
    all_cormen = base + extended_cormen
    return [
        {'code': item['pseudocode'], 'complexity': COMPLEXITY_MAP[item['complexity']]}
        for item in all_cormen
    ]


def get_complexity_distribution(dataset: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calcula distribucion de clases en un dataset."""
    from .consts import COMPLEXITY_CLASSES
    
    counts = {name: 0 for name in COMPLEXITY_CLASSES.values()}
    
    for item in dataset:
        complexity = item.get('complexity', 2)
        if isinstance(complexity, str):
            complexity = COMPLEXITY_MAP.get(complexity, 2)
        class_name = COMPLEXITY_CLASSES.get(complexity, 'Unknown')
        counts[class_name] = counts.get(class_name, 0) + 1
    
    return counts


def print_dataset_summary(dataset: List[Dict[str, Any]]) -> None:
    """Imprime resumen del dataset."""
    distribution = get_complexity_distribution(dataset)
    
    print(f"\nDataset Summary ({len(dataset)} examples)")
    print("-" * 40)
    
    for class_name, count in distribution.items():
        bar = "#" * count
        print(f"  {class_name:12} [{count:2}] {bar}")


def export_cormen_dataset_json(filepath: str = 'cormen_dataset.json'):
    """
    Exporta el dataset Cormen a un archivo JSON para revision/edicion.
    
    Args:
        filepath: Ruta de salida.
    """
    dataset = create_cormen_dataset()
    save_cormen_dataset(dataset, filepath)
    print(f"Dataset exported to {filepath} ({len(dataset)} examples)")
