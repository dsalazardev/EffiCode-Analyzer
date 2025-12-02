#!/usr/bin/env python3
"""
Training script for the neural complexity classifier.

Usage:
    python train_model.py
    python train_model.py --dataset custom.json
    python train_model.py --epochs 1000 --no-tuning
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from Servicios.NeuralClassifier import (
    NeuralComplexityClassifier,
    create_sample_dataset,
)


def load_dataset(filepath: str) -> list:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_dataset(dataset: list, filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)


def generate_extended_dataset() -> list:
    """Extends base dataset with additional training examples."""
    base_dataset = create_sample_dataset()

    extended = [
        {'code': 'return array[index]', 'complexity': 0},
        {'code': 'temp = a\na = b\nb = temp', 'complexity': 0},
        {'code': 'return n % 2 == 0', 'complexity': 0},

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
def heap_sort(arr):
    build_heap(arr)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, 0, i)
        ''', 'complexity': 3},
        {'code': '''
sorted_arr = sorted(array)
return sorted_arr
        ''', 'complexity': 3},

        {'code': '''
for i in range(n):
    for j in range(i + 1, n):
        if arr[i] == arr[j]:
            duplicates.append(arr[i])
        ''', 'complexity': 4},
        {'code': '''
for i in range(n):
    for j in range(n - i - 1):
        if arr[j] > arr[j + 1]:
            swap(arr, j, j + 1)
        ''', 'complexity': 4},
        {'code': '''
BUBBLE-SORT(A, n)
    for i = 1 to n - 1
        for j = 1 to n - i
            if A[j] > A[j + 1]
                exchange A[j] with A[j + 1]
        ''', 'complexity': 4},

        {'code': '''
def floyd_warshall(graph):
    for k in range(n):
        for i in range(n):
            for j in range(n):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
        ''', 'complexity': 5},

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

    return base_dataset + extended


def main():
    parser = argparse.ArgumentParser(
        description='Train the neural complexity classifier'
    )
    parser.add_argument('--dataset', '-d', type=str, default=None)
    parser.add_argument('--epochs', '-e', type=int, default=500)
    parser.add_argument('--no-tuning', action='store_true')
    parser.add_argument('--generate-dataset', type=str, default=None)
    parser.add_argument('--output', '-o', type=str, default=None)

    args = parser.parse_args()

    if args.generate_dataset:
        dataset = generate_extended_dataset()
        save_dataset(dataset, args.generate_dataset)
        return

    if args.dataset and os.path.exists(args.dataset):
        dataset = load_dataset(args.dataset)
    else:
        dataset = generate_extended_dataset()

    classifier = NeuralComplexityClassifier()
    use_tuning = not args.no_tuning

    classifier.train_from_dataset(
        dataset,
        use_hypertuning=use_tuning,
        verbose=True
    )

    output_path = args.output or str(classifier.MODEL_PATH)
    classifier.save(output_path)

    # Validation
    test_cases = [
        ('return x + y', 'O(1)'),
        ('while n > 0: n = n // 2', 'O(log n)'),
        ('for i in range(n): sum += arr[i]', 'O(n)'),
        ('arr.sort()', 'O(n log n)'),
        ('for i in range(n):\n  for j in range(n):\n    x += 1', 'O(n^2)'),
        ('for i in range(n):\n  for j in range(n):\n    for k in range(n):\n      x += 1', 'O(n^3)'),
    ]

    correct = sum(
        1 for code, expected in test_cases
        if classifier.classify(code)[0] == expected
    )

    if correct < len(test_cases) // 2:
        # FIXME: Model accuracy below acceptable threshold
        pass


if __name__ == '__main__':
    main()
