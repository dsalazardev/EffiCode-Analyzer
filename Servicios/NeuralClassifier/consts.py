"""
Constantes y configuraciones del clasificador neural de complejidad.

Centraliza diccionarios de patrones, clases de complejidad y parámetros
de configuración para el sistema Neural Algorithmix.
"""

from typing import Dict, List


COMPLEXITY_CLASSES: Dict[int, str] = {
    0: 'O(1)',
    1: 'O(log n)',
    2: 'O(n)',
    3: 'O(n log n)',
    4: 'O(n²)',
    5: 'O(n³)',
    6: 'O(2^n)',
}

COMPLEXITY_TO_INDEX: Dict[str, int] = {v: k for k, v in COMPLEXITY_CLASSES.items()}

NUM_COMPLEXITY_CLASSES: int = len(COMPLEXITY_CLASSES)


ALGORITHM_PATTERNS: Dict[str, str] = {
    'constant': 'return value',
    'logarithmic': 'while n > 0 n = n / 2',
    'linear': 'for i = 0 to n process item',
    'linearithmic': 'merge sort divide conquer for i merge',
    'quadratic_bubble': 'for i = 0 to n for j = 0 to n if a[j] > a[j+1] swap',
    'quadratic_selection': 'for i = 0 to n min = i for j = i to n if a[j] < a[min]',
    'quadratic_insertion': 'for i = 1 to n key = a[i] j = i - 1 while j >= 0 and a[j] > key',
    'cubic': 'for i for j for k triple nested loop',
    'exponential': 'recursive call f(n-1) + f(n-2) fibonacci',
    'binary_search': 'while low <= high mid = (low + high) / 2 if target == mid',
}

PATTERN_NAMES: List[str] = list(ALGORITHM_PATTERNS.keys())


DEFAULT_HIDDEN_LAYER_OPTIONS: List[List[int]] = [
    [8], [16], [32], [64],
    [16, 8], [32, 16], [64, 32],
    [32, 16, 8]
]

DEFAULT_LEARNING_RATE_OPTIONS: List[float] = [0.001, 0.01, 0.05, 0.1]

DEFAULT_HIDDEN_SIZES: List[int] = [32, 16]

DEFAULT_EPOCHS: int = 500
DEFAULT_BATCH_SIZE: int = 32
DEFAULT_LEARNING_RATE: float = 0.01

DEFAULT_PRUNING_THRESHOLD: float = 0.3


NUM_STRUCTURAL_FEATURES: int = 5

NUM_TOTAL_FEATURES: int = NUM_STRUCTURAL_FEATURES + len(ALGORITHM_PATTERNS)

STRUCTURAL_FEATURE_NAMES: List[str] = [
    'loop_depth',
    'n_loops',
    'has_recursion',
    'n_conditionals',
    'n_operations'
]

FEATURE_NORMALIZATION: Dict[str, int] = {
    'loop_depth': 5,
    'n_loops': 10,
    'n_conditionals': 20,
    'n_operations': 50
}


LOOP_KEYWORDS: List[str] = [
    'for ', 'while ', 'para ', 'mientras ', 'repeat ', 'repetir '
]

CONDITIONAL_KEYWORDS: List[str] = [
    'if ', 'else ', 'elif ', 'si ', 'sino '
]

ARITHMETIC_OPERATORS: List[str] = [
    '+', '-', '*', '/', '%', '**', '←', '='
]


DEFAULT_MODEL_FILENAME: str = 'neural_model.json'
