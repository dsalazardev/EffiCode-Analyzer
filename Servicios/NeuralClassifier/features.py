"""
Extractor de caracteristicas para conversion de codigo a vectores numericos.

Usa Programacion Dinamica (Levenshtein) para medir similitud con patrones
conocidos de algoritmos.
"""

from __future__ import annotations
import ast
import re
import numpy as np
from typing import List, Dict, Optional

from .consts import (
    ALGORITHM_PATTERNS,
    PATTERN_NAMES,
    STRUCTURAL_FEATURE_NAMES,
    LOOP_KEYWORDS,
    CONDITIONAL_KEYWORDS,
    ARITHMETIC_OPERATORS,
    FEATURE_NORMALIZATION
)


class FeatureExtractor:
    """
    Convierte codigo fuente/pseudocodigo en vectores numericos.
    
    Features extraidas:
    - Profundidad maxima de bucles anidados
    - Numero total de bucles
    - Presencia de recursion
    - Numero de condicionales
    - Numero de operaciones aritmeticas
    - Similitud con patrones conocidos (via Levenshtein DP)
    """
    
    def __init__(self):
        self._pattern_cache: Dict[str, float] = {}
    
    def levenshtein_dp(self, s1: str, s2: str) -> int:
        """
        Calcula distancia de Levenshtein usando Programacion Dinamica.
        
        Subproblema: dp[i][j] = distancia minima para s1[0:i] -> s2[0:j]
        
        Recurrencia:
            dp[i][j] = min(
                dp[i-1][j] + 1,      # Eliminacion
                dp[i][j-1] + 1,      # Insercion
                dp[i-1][j-1] + cost  # Sustitucion
            )
        
        Complejidad: O(m * n) tiempo, O(min(m, n)) espacio.
        
        Args:
            s1: Primera cadena.
            s2: Segunda cadena.
            
        Returns:
            Distancia de edicion minima.
        """
        if len(s1) < len(s2):
            s1, s2 = s2, s1
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                
                current_row.append(min(insertions, deletions, substitutions))
            
            previous_row = current_row
        
        return previous_row[-1]
    
    def similarity_score(self, code: str, pattern: str) -> float:
        """
        Calcula score de similitud normalizado [0, 1].
        
        Formula: similarity = 1 - (distance / max_length)
        
        Args:
            code: Codigo a comparar.
            pattern: Patron de referencia.
            
        Returns:
            Score de similitud entre 0 y 1.
        """
        code_normalized = self._normalize_code(code)
        pattern_normalized = self._normalize_code(pattern)
        
        cache_key = f"{hash(code_normalized)}_{hash(pattern_normalized)}"
        if cache_key in self._pattern_cache:
            return self._pattern_cache[cache_key]
        
        distance = self.levenshtein_dp(code_normalized, pattern_normalized)
        max_len = max(len(code_normalized), len(pattern_normalized))
        
        similarity = 1 - (distance / max_len) if max_len > 0 else 1.0
        
        self._pattern_cache[cache_key] = similarity
        return similarity
    
    def _normalize_code(self, code: str) -> str:
        """Normaliza codigo para comparacion justa."""
        code = code.lower()
        code = re.sub(r'#.*', '', code)
        code = re.sub(r'//.*', '', code)
        code = ' '.join(code.split())
        code = re.sub(r'[^\w\s\+\-\*\/\=\<\>\[\]]', ' ', code)
        return code.strip()
    
    def _count_loop_depth(self, code: str) -> int:
        """Cuenta profundidad maxima de bucles anidados."""
        try:
            tree = ast.parse(code)
            return self._max_loop_depth_ast(tree)
        except SyntaxError:
            return self._max_loop_depth_text(code)
    
    def _max_loop_depth_ast(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calcula profundidad usando AST de Python."""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While)):
                max_depth = max(max_depth, self._max_loop_depth_ast(child, current_depth + 1))
            else:
                max_depth = max(max_depth, self._max_loop_depth_ast(child, current_depth))
        
        return max_depth
    
    def _max_loop_depth_text(self, code: str) -> int:
        """Calcula profundidad por analisis de texto (fallback)."""
        lines = code.split('\n')
        max_depth = 0
        current_depth = 0
        
        for line in lines:
            stripped = line.strip().lower()
            
            if any(kw in stripped for kw in LOOP_KEYWORDS):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif stripped in ['end', 'fin', 'endfor', 'endwhile', 'end for', 'end while']:
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def _count_loops(self, code: str) -> int:
        """Cuenta numero total de bucles."""
        code_lower = code.lower()
        count = 0
        for kw in LOOP_KEYWORDS:
            count += code_lower.count(kw)
        return count
    
    def _has_recursion(self, code: str) -> int:
        """Detecta presencia de recursion (1/0)."""
        try:
            return self._has_recursion_ast(code)
        except SyntaxError:
            return self._has_recursion_regex(code)
    
    def _has_recursion_ast(self, code: str) -> int:
        """Detecta recursion usando AST de Python."""
        tree = ast.parse(code)
        
        func_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_names.add(node.name)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call):
                        if isinstance(subnode.func, ast.Name):
                            if subnode.func.id == node.name:
                                return 1
        return 0
    
    def _has_recursion_regex(self, code: str) -> int:
        """Detecta recursion usando patrones regex."""
        patterns = [
            r'(\w+)\s*\([^)]*\)[^{]*\{[^}]*\1\s*\(',
            r'return\s+\w+\s*\([^)]*\)',
        ]
        
        for pattern in patterns:
            if re.search(pattern, code, re.DOTALL):
                return 1
        return 0
    
    def _count_conditionals(self, code: str) -> int:
        """Cuenta estructuras condicionales."""
        code_lower = code.lower()
        count = 0
        for kw in CONDITIONAL_KEYWORDS:
            count += code_lower.count(kw)
        return count
    
    def _count_operations(self, code: str) -> int:
        """Cuenta operaciones aritmeticas y asignaciones."""
        count = 0
        for op in ARITHMETIC_OPERATORS:
            count += code.count(op)
        return count
    
    def extract(self, code: str) -> np.ndarray:
        """
        Extrae vector completo de features del codigo.
        
        Estructura del vector:
        [0]: loop_depth (normalizado)
        [1]: n_loops (normalizado)
        [2]: has_recursion (0/1)
        [3]: n_conditionals (normalizado)
        [4]: n_operations (normalizado)
        [5-14]: similitud con cada patron conocido
        
        Args:
            code: Codigo fuente o pseudocodigo.
            
        Returns:
            Vector numpy de shape (1, n_features).
        """
        features = []
        
        loop_depth = self._count_loop_depth(code)
        normalized_depth = min(loop_depth, FEATURE_NORMALIZATION['loop_depth'])
        features.append(normalized_depth / FEATURE_NORMALIZATION['loop_depth'])
        
        n_loops = self._count_loops(code)
        normalized_loops = min(n_loops, FEATURE_NORMALIZATION['n_loops'])
        features.append(normalized_loops / FEATURE_NORMALIZATION['n_loops'])
        
        features.append(float(self._has_recursion(code)))
        
        n_conditionals = self._count_conditionals(code)
        normalized_cond = min(n_conditionals, FEATURE_NORMALIZATION['n_conditionals'])
        features.append(normalized_cond / FEATURE_NORMALIZATION['n_conditionals'])
        
        n_operations = self._count_operations(code)
        normalized_ops = min(n_operations, FEATURE_NORMALIZATION['n_operations'])
        features.append(normalized_ops / FEATURE_NORMALIZATION['n_operations'])
        
        for pattern_name in PATTERN_NAMES:
            pattern = ALGORITHM_PATTERNS[pattern_name]
            similarity = self.similarity_score(code, pattern)
            features.append(similarity)
        
        return np.array([features])
    
    def get_feature_names(self) -> List[str]:
        """Retorna nombres de todas las features en orden."""
        names = STRUCTURAL_FEATURE_NAMES.copy()
        names.extend([f'sim_{name}' for name in PATTERN_NAMES])
        return names
    
    def clear_cache(self) -> None:
        """Limpia cache de similitudes calculadas."""
        self._pattern_cache.clear()
    
    def __repr__(self) -> str:
        return f"FeatureExtractor(n_patterns={len(ALGORITHM_PATTERNS)}, cache_size={len(self._pattern_cache)})"
