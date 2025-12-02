"""
Buscador de hiperparametros usando Backtracking con poda.

Explora el arbol de configuraciones posibles y poda ramas con
rendimiento bajo el umbral (branch and bound).
"""

from __future__ import annotations
import numpy as np
from typing import List, Dict, Any, Optional

from .model import NeuralNetwork
from .consts import (
    DEFAULT_HIDDEN_LAYER_OPTIONS,
    DEFAULT_LEARNING_RATE_OPTIONS,
    DEFAULT_PRUNING_THRESHOLD
)


class HyperTuner:
    """
    Optimizador de arquitectura usando Backtracking con poda.
    
    Espacio de busqueda:
    - Arquitecturas de capas ocultas: [[8], [16], [32], ...]
    - Learning rates: [0.001, 0.01, 0.05, 0.1]
    
    Estrategia de poda:
    Si accuracy < threshold, no explorar mas learning rates para esa arquitectura.
    """
    
    def __init__(self, X_train: np.ndarray, y_train: np.ndarray,
                 X_val: np.ndarray = None, y_val: np.ndarray = None,
                 pruning_threshold: float = DEFAULT_PRUNING_THRESHOLD):
        """
        Args:
            X_train: Features de entrenamiento.
            y_train: Etiquetas de entrenamiento.
            X_val: Features de validacion (opcional, usa 20% de train si no se da).
            y_val: Etiquetas de validacion (opcional).
            pruning_threshold: Umbral minimo de accuracy para no podar.
        """
        if X_val is None:
            split_idx = int(0.8 * len(X_train))
            self.X_train = X_train[:split_idx]
            self.y_train = y_train[:split_idx]
            self.X_val = X_train[split_idx:]
            self.y_val = y_train[split_idx:]
        else:
            self.X_train = X_train
            self.y_train = y_train
            self.X_val = X_val
            self.y_val = y_val
        
        self.best_accuracy: float = 0.0
        self.best_config: Optional[Dict[str, Any]] = None
        self.best_model: Optional[NeuralNetwork] = None
        
        self.search_history: List[Dict[str, Any]] = []
        self.pruning_threshold = pruning_threshold
        
        self.configs_tested: int = 0
        self.configs_pruned: int = 0
    
    def search(self,
               hidden_layer_options: List[List[int]] = None,
               learning_rate_options: List[float] = None,
               epochs_per_trial: int = 100,
               verbose: bool = True) -> Dict[str, Any]:
        """
        Busca la mejor arquitectura usando Backtracking.
        
        Args:
            hidden_layer_options: Lista de arquitecturas [[8], [16], [8,8], ...].
            learning_rate_options: Lista de learning rates.
            epochs_per_trial: Epocas de entrenamiento por prueba.
            verbose: Mostrar progreso.
            
        Returns:
            Mejor configuracion encontrada.
        """
        if hidden_layer_options is None:
            hidden_layer_options = DEFAULT_HIDDEN_LAYER_OPTIONS
        
        if learning_rate_options is None:
            learning_rate_options = DEFAULT_LEARNING_RATE_OPTIONS
        
        input_size = self.X_train.shape[1]
        output_size = len(np.unique(self.y_train))
        
        if verbose:
            total_configs = len(hidden_layer_options) * len(learning_rate_options)
            print(f"Starting backtracking search...")
            print(f"  Possible configurations: {total_configs}")
            print(f"  Pruning threshold: {self.pruning_threshold}")
        
        self._backtrack_search(
            hidden_layer_options=hidden_layer_options,
            learning_rate_options=learning_rate_options,
            input_size=input_size,
            output_size=output_size,
            epochs=epochs_per_trial,
            current_hidden_idx=0,
            current_lr_idx=0,
            verbose=verbose
        )
        
        if verbose:
            print(f"Search completed.")
            print(f"  Configurations tested: {self.configs_tested}")
            print(f"  Configurations pruned: {self.configs_pruned}")
            print(f"  Best accuracy: {self.best_accuracy:.4f}")
            print(f"  Best config: {self.best_config}")
        
        return self.best_config
    
    def _backtrack_search(self,
                          hidden_layer_options: List[List[int]],
                          learning_rate_options: List[float],
                          input_size: int,
                          output_size: int,
                          epochs: int,
                          current_hidden_idx: int,
                          current_lr_idx: int,
                          verbose: bool) -> None:
        """
        Algoritmo de Backtracking recursivo.
        
        Estructura del arbol:
            [root]
           /  |  \\
        [8]  [16]  [32]  ...  (hidden layers)
        /|\\   /|\\   /|\\
       lr1 lr2 lr3 ...        (learning rates)
        """
        if current_hidden_idx >= len(hidden_layer_options):
            return
        
        hidden_sizes = hidden_layer_options[current_hidden_idx]
        
        for lr_idx in range(current_lr_idx, len(learning_rate_options)):
            lr = learning_rate_options[lr_idx]
            self.configs_tested += 1
            
            config = {
                'hidden_sizes': hidden_sizes,
                'learning_rate': lr
            }
            
            if verbose:
                print(f"  Testing: hidden={hidden_sizes}, lr={lr}...")
            
            model = NeuralNetwork(input_size, hidden_sizes, output_size)
            model.train(
                self.X_train, self.y_train,
                epochs=epochs,
                learning_rate=lr,
                verbose=False
            )
            
            predictions = model.predict(self.X_val)
            accuracy = np.mean(predictions == self.y_val)
            
            self.search_history.append({
                'config': config.copy(),
                'accuracy': accuracy,
                'pruned': False
            })
            
            if verbose:
                marker = "*" if accuracy > self.best_accuracy else " "
                print(f"  {marker} Accuracy: {accuracy:.4f}")
            
            if accuracy > self.best_accuracy:
                self.best_accuracy = accuracy
                self.best_config = config.copy()
                self.best_model = model
            
            if accuracy < self.pruning_threshold:
                remaining_lrs = len(learning_rate_options) - lr_idx - 1
                self.configs_pruned += remaining_lrs
                self.search_history[-1]['pruned'] = True
                
                if verbose:
                    print(f"  Pruning branch (accuracy {accuracy:.4f} < {self.pruning_threshold})")
                
                break
        
        self._backtrack_search(
            hidden_layer_options=hidden_layer_options,
            learning_rate_options=learning_rate_options,
            input_size=input_size,
            output_size=output_size,
            epochs=epochs,
            current_hidden_idx=current_hidden_idx + 1,
            current_lr_idx=0,
            verbose=verbose
        )
    
    def get_best_model(self) -> Optional[NeuralNetwork]:
        """Retorna el mejor modelo encontrado."""
        return self.best_model
    
    def get_search_summary(self) -> Dict[str, Any]:
        """Retorna resumen de la busqueda."""
        return {
            'best_config': self.best_config,
            'best_accuracy': self.best_accuracy,
            'configs_tested': self.configs_tested,
            'configs_pruned': self.configs_pruned,
            'pruning_efficiency': (
                self.configs_pruned / (self.configs_tested + self.configs_pruned)
                if (self.configs_tested + self.configs_pruned) > 0 else 0
            ),
            'total_configs_in_history': len(self.search_history)
        }
    
    def __repr__(self) -> str:
        return (
            f"HyperTuner("
            f"best_acc={self.best_accuracy:.4f}, "
            f"tested={self.configs_tested}, "
            f"pruned={self.configs_pruned})"
        )
