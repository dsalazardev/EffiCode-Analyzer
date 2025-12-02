"""
Clasificador de complejidad algoritmica basado en redes neuronales.

Patron Facade que integra FeatureExtractor, NeuralNetwork y HyperTuner
en una interfaz simple y coherente.
"""

from __future__ import annotations
import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional

from .model import NeuralNetwork
from .features import FeatureExtractor
from .tuner import HyperTuner
from .consts import (
    COMPLEXITY_CLASSES,
    DEFAULT_HIDDEN_SIZES,
    DEFAULT_EPOCHS,
    DEFAULT_MODEL_FILENAME
)


class NeuralComplexityClassifier:
    """
    Clasificador de complejidad algoritmica.
    
    Flujo de clasificacion:
    1. Codigo -> FeatureExtractor -> vector numerico
    2. Vector -> NeuralNetwork -> prediccion
    3. Retornar complejidad con confianza
    
    Flujo de entrenamiento:
    1. Dataset -> extraer features
    2. (Opcional) HyperTuner busca arquitectura optima
    3. NeuralNetwork entrena
    4. Guardar modelo
    """
    
    MODEL_PATH = Path(__file__).parent.parent.parent / DEFAULT_MODEL_FILENAME
    
    def __init__(self, model_path: str = None):
        """
        Args:
            model_path: Ruta personalizada para el modelo (opcional).
        """
        self.feature_extractor = FeatureExtractor()
        self.model: Optional[NeuralNetwork] = None
        self.is_trained = False
        
        if model_path:
            self.model_path = Path(model_path)
        else:
            self.model_path = self.MODEL_PATH
    
    def train(self, X: np.ndarray, y: np.ndarray,
              use_hypertuning: bool = True,
              epochs: int = DEFAULT_EPOCHS,
              verbose: bool = True) -> Dict[str, Any]:
        """
        Entrena el modelo con datos preprocesados.
        
        Args:
            X: Features de entrenamiento (n_samples, n_features).
            y: Etiquetas de clase (n_samples,).
            use_hypertuning: Usar backtracking para optimizar arquitectura.
            epochs: Epocas de entrenamiento.
            verbose: Mostrar progreso.
            
        Returns:
            Historial de entrenamiento.
        """
        input_size = X.shape[1]
        output_size = len(np.unique(y))
        
        if use_hypertuning and len(X) >= 20:
            if verbose:
                print("Using HyperTuner (Backtracking) to optimize architecture...")
            
            tuner = HyperTuner(X, y)
            best_config = tuner.search(epochs_per_trial=100, verbose=verbose)
            
            self.model = tuner.get_best_model()
            
            if verbose:
                print(f"\nFinal training with optimal architecture...")
            
            history = self.model.train(
                X, y,
                epochs=epochs,
                learning_rate=best_config['learning_rate'],
                verbose=verbose
            )
        else:
            if verbose:
                print("Training with default architecture...")
            
            self.model = NeuralNetwork(input_size, DEFAULT_HIDDEN_SIZES, output_size)
            history = self.model.train(X, y, epochs=epochs, verbose=verbose)
        
        self.is_trained = True
        return history
    
    def train_from_dataset(self, dataset: List[Dict[str, Any]],
                           use_hypertuning: bool = True,
                           verbose: bool = True) -> Dict[str, Any]:
        """
        Entrena desde un dataset de ejemplos codigo-complejidad.
        
        Formato del dataset:
        [
            {'code': 'for i in range(n): ...', 'complexity': 2},
            {'code': 'return x + y', 'complexity': 0},
            ...
        ]
        
        Args:
            dataset: Lista de diccionarios con 'code' y 'complexity'.
            use_hypertuning: Usar backtracking para optimizar.
            verbose: Mostrar progreso.
            
        Returns:
            Historial de entrenamiento.
        """
        if verbose:
            print(f"Extracting features from {len(dataset)} examples...")
        
        X_list = []
        y_list = []
        
        for item in dataset:
            features = self.feature_extractor.extract(item['code'])
            X_list.append(features[0])
            y_list.append(item['complexity'])
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        return self.train(X, y, use_hypertuning=use_hypertuning, verbose=verbose)
    
    def classify(self, code: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Clasifica la complejidad de un codigo.
        
        Args:
            code: Codigo fuente o pseudocodigo.
            
        Returns:
            Tupla de:
            - complejidad: String como 'O(n)', 'O(n^2)', etc.
            - confianza: Float entre 0 y 1.
            - probabilidades: Dict con probabilidad de cada clase.
            
        Raises:
            RuntimeError: Si el modelo no ha sido entrenado.
        """
        if not self.is_trained or self.model is None:
            raise RuntimeError(
                "Model not trained. Call train() or load() first."
            )
        
        features = self.feature_extractor.extract(code)
        complexity, confidence = self.model.predict_complexity(features)
        
        proba = self.model.predict_proba(features)[0]
        probabilities = {
            COMPLEXITY_CLASSES[i]: float(proba[i])
            for i in range(len(proba))
        }
        
        return complexity, confidence, probabilities
    
    def classify_batch(self, codes: List[str]) -> List[Tuple[str, float]]:
        """
        Clasifica multiples codigos.
        
        Args:
            codes: Lista de codigos a clasificar.
            
        Returns:
            Lista de tuplas (complejidad, confianza).
        """
        results = []
        for code in codes:
            complexity, confidence, _ = self.classify(code)
            results.append((complexity, confidence))
        return results
    
    def save(self, filepath: str = None) -> None:
        """
        Guarda el modelo entrenado.
        
        Args:
            filepath: Ruta del archivo (usa model_path por defecto).
        """
        if filepath is None:
            filepath = str(self.model_path)
        
        if self.model:
            self.model.save(filepath)
    
    def load(self, filepath: str = None) -> bool:
        """
        Carga un modelo previamente entrenado.
        
        Args:
            filepath: Ruta del archivo (usa model_path por defecto).
            
        Returns:
            True si se cargo exitosamente.
        """
        if filepath is None:
            filepath = str(self.model_path)
        
        if not os.path.exists(filepath):
            return False
        
        try:
            self.model = NeuralNetwork.load(filepath)
            self.is_trained = True
            return True
        except Exception:
            return False
    
    def load_or_train(self, dataset_path: str = None,
                      dataset: List[Dict] = None) -> bool:
        """
        Intenta cargar modelo existente, si no existe entrena uno nuevo.
        
        Args:
            dataset_path: Ruta al JSON con dataset de entrenamiento.
            dataset: Dataset directamente (alternativa a dataset_path).
            
        Returns:
            True si el modelo esta listo para usar.
        """
        if self.load():
            return True
        
        if dataset_path and os.path.exists(dataset_path):
            with open(dataset_path, 'r') as f:
                dataset = json.load(f)
        
        if dataset:
            print("Model not found. Training new model...")
            self.train_from_dataset(dataset)
            self.save()
            return True
        
        return False
    
    def get_feature_names(self) -> List[str]:
        """Retorna nombres de las features usadas."""
        return self.feature_extractor.get_feature_names()
    
    def get_complexity_classes(self) -> Dict[int, str]:
        """Retorna mapeo de indices a nombres de complejidad."""
        return COMPLEXITY_CLASSES.copy()
    
    def __repr__(self) -> str:
        status = "trained" if self.is_trained else "not trained"
        return f"NeuralComplexityClassifier(status={status})"
