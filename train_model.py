#!/usr/bin/env python3
"""
Training script for the Neural Complexity Classifier.

Pipeline:
1. Load Cormen pseudocode dataset
2. Translate each example: Cormen -> Parser -> Python
3. Extract features from Python AST
4. Train neural network

Usage:
    python train_model.py
    python train_model.py --dataset custom.json
    python train_model.py --epochs 1000 --no-tuning
    python train_model.py --export-dataset cormen_data.json
"""

import argparse
import json
import os
import sys
import io
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from Servicios.NeuralClassifier import (
    NeuralComplexityClassifier,
    FeatureExtractor,
)
from Servicios.NeuralClassifier.utils import (
    create_cormen_dataset,
    create_extended_dataset,
    load_cormen_dataset,
    save_cormen_dataset,
    print_dataset_summary,
    COMPLEXITY_MAP,
    TRAINING_DATA_PATH,
)


class MockGrammar:
    """Mock Grammar para Parser standalone."""
    def validar_sentencia(self, pseudocodigo: str) -> bool:
        return True


class MockLLMService:
    """Mock LLMService para Parser standalone."""
    pass


def create_parser():
    """
    Crea instancia de Parser con mocks para entrenamiento standalone.
    El Parser solo necesita su metodo _translate_pseudocode_to_python.
    """
    from Modelos.Parser import Parser
    
    grammar = MockGrammar()
    llm_service = MockLLMService()
    
    return Parser(id=1, gramatica=grammar, llm_service=llm_service)


def translate_cormen_to_python(pseudocode: str, parser, silent: bool = True) -> str:
    """
    Traduce pseudocodigo Cormen a Python usando el Parser.
    
    Args:
        pseudocode: Codigo en formato Cormen.
        parser: Instancia de Parser.
        silent: Suprimir prints del Parser.
        
    Returns:
        Codigo Python traducido.
    """
    try:
        if silent:
            f = io.StringIO()
            with redirect_stdout(f):
                ast_obj = parser.parsear(pseudocode)
            return ast_obj._codigo
        else:
            ast_obj = parser.parsear(pseudocode)
            return ast_obj._codigo
    except Exception as e:
        if not silent:
            print(f"  Warning: Parse failed, using heuristic: {e}")
        return parser._translate_pseudocode_to_python(pseudocode)


def prepare_training_data(cormen_dataset: list, parser, verbose: bool = True) -> list:
    """
    Prepara datos de entrenamiento traduciendo Cormen -> Python.
    
    Args:
        cormen_dataset: Lista de {'pseudocode': str, 'complexity': str}
        parser: Instancia de Parser
        verbose: Mostrar progreso
        
    Returns:
        Lista de {'code': python_code, 'complexity': int_label}
    """
    if verbose:
        print(f"Translating {len(cormen_dataset)} Cormen examples to Python...")
    
    training_data = []
    success_count = 0
    
    for i, item in enumerate(cormen_dataset):
        pseudocode = item.get('pseudocode', item.get('code', ''))
        complexity_raw = item.get('complexity', 'O(n)')
        
        if isinstance(complexity_raw, str):
            complexity_label = COMPLEXITY_MAP.get(complexity_raw, 2)
        else:
            complexity_label = complexity_raw
        
        python_code = translate_cormen_to_python(pseudocode, parser, silent=True)
        
        if python_code and python_code.strip():
            training_data.append({
                'code': python_code,
                'complexity': complexity_label
            })
            success_count += 1
        else:
            if verbose:
                print(f"  Skipped example {i+1}: empty translation")
    
    if verbose:
        print(f"Successfully translated {success_count}/{len(cormen_dataset)} examples")
    
    return training_data


def main():
    arg_parser = argparse.ArgumentParser(
        description='Train the Neural Complexity Classifier with Cormen pseudocode'
    )
    arg_parser.add_argument('--dataset', '-d', type=str, default=None,
                           help='Path to JSON dataset (default: Documentos/training_algorithms.json)')
    arg_parser.add_argument('--epochs', '-e', type=int, default=500,
                           help='Training epochs (default: 500)')
    arg_parser.add_argument('--no-tuning', action='store_true',
                           help='Skip hyperparameter tuning')
    arg_parser.add_argument('--export-dataset', type=str, default=None,
                           help='Export Cormen dataset to JSON file')
    arg_parser.add_argument('--output', '-o', type=str, default=None,
                           help='Output path for trained model')
    arg_parser.add_argument('--raw-python', action='store_true',
                           help='Skip Cormen translation, use Python code directly')
    
    args = arg_parser.parse_args()
    
    if args.export_dataset:
        dataset = create_cormen_dataset()
        save_cormen_dataset(dataset, args.export_dataset)
        print(f"Exported {len(dataset)} examples to {args.export_dataset}")
        return
    
    print("=" * 60)
    print("Neural Complexity Classifier - Training Pipeline")
    print("=" * 60)
    
    # Step 1: Initialize Parser
    print("\n[1/4] Initializing Parser...")
    parser = create_parser()
    print("  Parser ready")
    
    # Step 2: Load dataset
    print("\n[2/4] Loading dataset...")
    
    # Determinar ruta del dataset
    dataset_path = args.dataset if args.dataset else str(TRAINING_DATA_PATH)
    
    if os.path.exists(dataset_path):
        print(f"  Loading from: {dataset_path}")
        with open(dataset_path, 'r', encoding='utf-8') as f:
            raw_dataset = json.load(f)
        
        if raw_dataset and 'pseudocode' in raw_dataset[0]:
            cormen_dataset = raw_dataset
        else:
            cormen_dataset = [
                {'pseudocode': item.get('code', item.get('pseudocode', '')), 
                 'complexity': item.get('complexity', 'O(n)')}
                for item in raw_dataset
            ]
    else:
        print(f"  WARNING: Dataset file not found: {dataset_path}")
        print("  Using built-in dataset as fallback")
        cormen_dataset = create_cormen_dataset()
        
        from Servicios.NeuralClassifier.utils import create_extended_dataset as _ext
        extended = _ext()
        
        extended_cormen = []
        for item in extended:
            code = item.get('code', '')
            complexity_int = item.get('complexity', 2)
            
            complexity_str = 'O(n)'
            for k, v in COMPLEXITY_MAP.items():
                if v == complexity_int:
                    complexity_str = k
                    break
            
            extended_cormen.append({
                'pseudocode': code,
                'complexity': complexity_str
            })
        
        cormen_dataset = extended_cormen
    
    print_dataset_summary([
        {'complexity': COMPLEXITY_MAP.get(item['complexity'], item['complexity'])}
        for item in cormen_dataset
    ])
    
    # Step 3: Translate Cormen -> Python
    print("\n[3/4] Translating Cormen to Python...")
    if args.raw_python:
        print("  Skipping translation (--raw-python flag)")
        training_data = [
            {'code': item.get('pseudocode', item.get('code', '')),
             'complexity': COMPLEXITY_MAP.get(item['complexity'], item['complexity'])}
            for item in cormen_dataset
        ]
    else:
        training_data = prepare_training_data(cormen_dataset, parser, verbose=True)
    
    if not training_data:
        print("ERROR: No training data available")
        sys.exit(1)
    
    # Step 4: Train
    print("\n[4/4] Training Neural Network...")
    classifier = NeuralComplexityClassifier()
    use_tuning = not args.no_tuning
    
    if use_tuning:
        print("  Using HyperTuner (Backtracking) for architecture search")
    else:
        print("  Using default architecture [32, 16]")
    
    classifier.train_from_dataset(
        training_data,
        use_hypertuning=use_tuning,
        verbose=True
    )
    
    # Save model
    output_path = args.output or str(classifier.MODEL_PATH)
    classifier.save(output_path)
    print(f"\nModel saved to: {output_path}")
    
    # Validation
    print("\n" + "=" * 60)
    print("Validation Tests")
    print("=" * 60)
    
    test_cases_cormen = [
        ('SIMPLE-RETURN(x)\n    return x', 'O(1)'),
        ('HALVE(n)\n    while n > 1 do\n        n ← n div 2', 'O(log n)'),
        ('SUM(A, n)\n    s ← 0\n    for i ← 1 to n do\n        s ← s + A[i]\n    return s', 'O(n)'),
        ('NESTED(A, n)\n    for i ← 1 to n do\n        for j ← 1 to n do\n            A[i][j] ← 0', 'O(n^2)'),
    ]
    
    print("\nTesting with Cormen pseudocode:")
    correct = 0
    for pseudocode, expected in test_cases_cormen:
        python_code = translate_cormen_to_python(pseudocode, parser, silent=True)
        predicted, confidence, _ = classifier.classify(python_code)
        
        expected_normalized = expected.replace('^2', '²').replace('^3', '³')
        predicted_normalized = predicted.replace('^2', '²').replace('^3', '³')
        
        match = expected_normalized == predicted_normalized or expected == predicted
        status = "PASS" if match else "FAIL"
        if match:
            correct += 1
        
        func_name = pseudocode.split('(')[0].split('\n')[0]
        print(f"  [{status}] {func_name}: {predicted} (expected {expected}, conf={confidence:.2f})")
    
    print(f"\nAccuracy: {correct}/{len(test_cases_cormen)} ({100*correct/len(test_cases_cormen):.1f}%)")
    print("\nTraining complete!")


if __name__ == '__main__':
    main()
