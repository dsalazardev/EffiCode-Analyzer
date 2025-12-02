"""
Neural Algorithmix - Clasificacion de Complejidad Algoritmica.

Sistema basado en redes neuronales que combina:
- Programacion Dinamica: Levenshtein para extraccion de features
- Backtracking: Busqueda de arquitectura optima con poda
- Algoritmos Voraces: Descenso de gradiente para entrenamiento

Uso basico:
    from Servicios.NeuralClassifier import NeuralComplexityClassifier
    
    classifier = NeuralComplexityClassifier()
    classifier.load_or_train(dataset)
    complexity, confidence, proba = classifier.classify(code)

Uso avanzado:
    from Servicios.NeuralClassifier import (
        NeuralComplexityClassifier,
        NeuralNetwork,
        FeatureExtractor,
        HyperTuner,
        create_sample_dataset
    )
"""

__version__ = "1.0.0"


from .classifier import NeuralComplexityClassifier
from .model import NeuralNetwork
from .features import FeatureExtractor
from .tuner import HyperTuner

from .utils import (
    create_sample_dataset,
    create_extended_dataset,
    get_complexity_distribution,
    print_dataset_summary
)

from .consts import (
    COMPLEXITY_CLASSES,
    COMPLEXITY_TO_INDEX,
    ALGORITHM_PATTERNS,
    NUM_COMPLEXITY_CLASSES
)


__all__ = [
    "NeuralComplexityClassifier",
    "NeuralNetwork",
    "FeatureExtractor", 
    "HyperTuner",
    "create_sample_dataset",
    "create_extended_dataset",
    "get_complexity_distribution",
    "print_dataset_summary",
    "COMPLEXITY_CLASSES",
    "COMPLEXITY_TO_INDEX",
    "ALGORITHM_PATTERNS",
    "NUM_COMPLEXITY_CLASSES",
]
