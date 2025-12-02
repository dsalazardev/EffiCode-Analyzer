"""
Perceptron Multicapa (MLP) implementado desde cero con NumPy.

Usa descenso de gradiente (greedy) para el entrenamiento.
Soporta arquitectura configurable con inicializacion Xavier/Glorot.
"""

from __future__ import annotations
import json
import numpy as np
from typing import List, Dict, Tuple, Optional

from .consts import COMPLEXITY_CLASSES


class NeuralNetwork:
    """
    Red neuronal multicapa para clasificacion de complejidad algoritmica.
    
    Arquitectura: Input -> [Hidden + ReLU] * n -> Output + Softmax
    Entrenamiento: Mini-batch gradient descent con cross-entropy loss.
    """
    
    def __init__(self, input_size: int, hidden_sizes: List[int], output_size: int):
        """
        Args:
            input_size: Numero de features de entrada.
            hidden_sizes: Lista con tamanos de capas ocultas [h1, h2, ...].
            output_size: Numero de clases de salida.
        """
        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.output_size = output_size
        
        self.weights: List[np.ndarray] = []
        self.biases: List[np.ndarray] = []
        
        self._initialize_weights()
        
        self.activations: List[np.ndarray] = []
        self.z_values: List[np.ndarray] = []
        
        self.training_history: Dict[str, List[float]] = {
            'loss': [],
            'accuracy': []
        }
    
    def _initialize_weights(self) -> None:
        """Inicializa pesos con Xavier/Glorot initialization."""
        layer_sizes = [self.input_size] + self.hidden_sizes + [self.output_size]
        
        for i in range(len(layer_sizes) - 1):
            scale = np.sqrt(2.0 / (layer_sizes[i] + layer_sizes[i + 1]))
            W = np.random.randn(layer_sizes[i], layer_sizes[i + 1]) * scale
            b = np.zeros((1, layer_sizes[i + 1]))
            
            self.weights.append(W)
            self.biases.append(b)
    
    @staticmethod
    def relu(x: np.ndarray) -> np.ndarray:
        """ReLU activation: max(0, x)."""
        return np.maximum(0, x)
    
    @staticmethod
    def relu_derivative(x: np.ndarray) -> np.ndarray:
        """Derivada de ReLU."""
        return (x > 0).astype(float)
    
    @staticmethod
    def softmax(x: np.ndarray) -> np.ndarray:
        """Softmax con estabilidad numerica."""
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)
    
    @staticmethod
    def sigmoid(x: np.ndarray) -> np.ndarray:
        """Sigmoid activation."""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def forward(self, X: np.ndarray) -> np.ndarray:
        """
        Propagacion hacia adelante.
        
        Args:
            X: Matriz de entrada (batch_size, input_size).
            
        Returns:
            Probabilidades de cada clase (batch_size, output_size).
        """
        self.activations = [X]
        self.z_values = []
        
        current_input = X
        
        for i in range(len(self.weights) - 1):
            z = np.dot(current_input, self.weights[i]) + self.biases[i]
            self.z_values.append(z)
            a = self.relu(z)
            self.activations.append(a)
            current_input = a
        
        z_output = np.dot(current_input, self.weights[-1]) + self.biases[-1]
        self.z_values.append(z_output)
        output = self.softmax(z_output)
        self.activations.append(output)
        
        return output
    
    def backward(self, X: np.ndarray, y: np.ndarray, learning_rate: float) -> float:
        """
        Backpropagation con actualizacion de pesos (gradient descent).
        
        Args:
            X: Datos de entrada.
            y: Etiquetas one-hot encoded.
            learning_rate: Tasa de aprendizaje.
            
        Returns:
            Loss (Cross-Entropy).
        """
        batch_size = X.shape[0]
        
        output = self.activations[-1]
        loss = -np.mean(np.sum(y * np.log(output + 1e-8), axis=1))
        
        delta = output - y
        deltas = [delta]
        
        for i in range(len(self.weights) - 2, -1, -1):
            delta = np.dot(deltas[-1], self.weights[i + 1].T) * self.relu_derivative(self.z_values[i])
            deltas.append(delta)
        
        deltas.reverse()
        
        for i in range(len(self.weights)):
            grad_W = np.dot(self.activations[i].T, deltas[i]) / batch_size
            grad_b = np.mean(deltas[i], axis=0, keepdims=True)
            
            self.weights[i] -= learning_rate * grad_W
            self.biases[i] -= learning_rate * grad_b
        
        return loss
    
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 1000,
              learning_rate: float = 0.01, batch_size: int = 32,
              verbose: bool = True) -> Dict[str, List[float]]:
        """
        Entrena la red usando mini-batch gradient descent.
        
        Args:
            X: Datos de entrenamiento (n_samples, n_features).
            y: Etiquetas (n_samples,) o one-hot (n_samples, n_classes).
            epochs: Numero de epocas.
            learning_rate: Tasa de aprendizaje.
            batch_size: Tamano del mini-batch.
            verbose: Mostrar progreso cada 100 epocas.
            
        Returns:
            Historial con 'loss' y 'accuracy' por epoca.
        """
        if len(y.shape) == 1:
            y_onehot = np.zeros((y.shape[0], self.output_size))
            y_onehot[np.arange(y.shape[0]), y.astype(int)] = 1
        else:
            y_onehot = y
        
        n_samples = X.shape[0]
        
        for epoch in range(epochs):
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y_onehot[indices]
            
            epoch_loss = 0
            n_batches = 0
            
            for i in range(0, n_samples, batch_size):
                X_batch = X_shuffled[i:i + batch_size]
                y_batch = y_shuffled[i:i + batch_size]
                
                self.forward(X_batch)
                loss = self.backward(X_batch, y_batch, learning_rate)
                
                epoch_loss += loss
                n_batches += 1
            
            avg_loss = epoch_loss / n_batches
            predictions = self.predict(X)
            y_true = y if len(y.shape) == 1 else np.argmax(y, axis=1)
            accuracy = np.mean(predictions == y_true)
            
            self.training_history['loss'].append(avg_loss)
            self.training_history['accuracy'].append(accuracy)
            
            if verbose and (epoch + 1) % 100 == 0:
                print(f"Epoch {epoch + 1}/{epochs} - Loss: {avg_loss:.4f} - Accuracy: {accuracy:.4f}")
        
        return self.training_history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predice clases para los datos de entrada.
        
        Args:
            X: Datos de entrada (n_samples, n_features).
            
        Returns:
            Indices de clase predichos (n_samples,).
        """
        probabilities = self.forward(X)
        return np.argmax(probabilities, axis=1)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Retorna probabilidades de cada clase.
        
        Args:
            X: Datos de entrada (n_samples, n_features).
            
        Returns:
            Probabilidades (n_samples, n_classes).
        """
        return self.forward(X)
    
    def predict_complexity(self, X: np.ndarray) -> Tuple[str, float]:
        """
        Predice complejidad algoritmica con nivel de confianza.
        
        Args:
            X: Features del codigo (1, n_features).
            
        Returns:
            Tupla (nombre_complejidad, confianza).
        """
        proba = self.predict_proba(X)
        class_idx = np.argmax(proba, axis=1)[0]
        confidence = proba[0, class_idx]
        complexity = COMPLEXITY_CLASSES.get(class_idx, 'Desconocida')
        
        return complexity, float(confidence)
    
    def save(self, filepath: str) -> None:
        """
        Guarda el modelo en formato JSON.
        
        Args:
            filepath: Ruta del archivo de salida.
        """
        data = {
            'architecture': {
                'input_size': self.input_size,
                'hidden_sizes': self.hidden_sizes,
                'output_size': self.output_size
            },
            'weights': [w.tolist() for w in self.weights],
            'biases': [b.tolist() for b in self.biases],
            'training_history': self.training_history
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'NeuralNetwork':
        """
        Carga un modelo desde archivo JSON.
        
        Args:
            filepath: Ruta del archivo de modelo.
            
        Returns:
            Instancia de NeuralNetwork con pesos cargados.
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        arch = data['architecture']
        model = cls(arch['input_size'], arch['hidden_sizes'], arch['output_size'])
        
        model.weights = [np.array(w) for w in data['weights']]
        model.biases = [np.array(b) for b in data['biases']]
        model.training_history = data.get('training_history', {'loss': [], 'accuracy': []})
        
        return model
    
    def __repr__(self) -> str:
        layers = [self.input_size] + self.hidden_sizes + [self.output_size]
        return f"NeuralNetwork(layers={layers})"
