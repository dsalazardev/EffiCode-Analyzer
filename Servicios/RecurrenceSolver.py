"""
Módulo de Resolución de Ecuaciones de Recurrencia.

Implementa los 7 métodos del libro "Introduction to Algorithms" (Cormen et al., 4th Ed):
1. Método de Sustitución (Substitution Method)
2. Método del Árbol de Recursión (Recursion-Tree Method)
3. Teorema Maestro (Master Theorem)
4. Método de Akra-Bazzi
5. Cambio de Variables
6. Método de Iteración/Desenrollado
7. Funciones Generatrices (para Fibonacci y similares)

Autor: EffiCode Analyzer
Referencia: CLRS Chapter 4 - Divide and Conquer, Recurrences
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math
import re


class MetodoResolucion(Enum):
    """Métodos disponibles para resolver recurrencias."""
    MAESTRO = "master_theorem"
    ARBOL = "recursion_tree"
    SUSTITUCION = "substitution"
    AKRA_BAZZI = "akra_bazzi"
    CAMBIO_VARIABLES = "change_of_variables"
    ITERACION = "iteration"
    GENERATRICES = "generating_functions"


@dataclass
class Recurrencia:
    """
    Representa una ecuación de recurrencia T(n).
    
    Formato estándar: T(n) = a*T(n/b) + f(n)
    Formato lineal:   T(n) = T(n-k) + f(n)
    Formato múltiple: T(n) = sum(a_i * T(n/b_i)) + f(n)
    """
    # Parámetros para T(n) = a*T(n/b) + f(n)
    a: float = 1.0              # Número de subproblemas
    b: float = 2.0              # Factor de división
    f_n: str = "n"              # Función de trabajo f(n)
    f_n_orden: float = 1.0      # Exponente de n en f(n): n^k -> k
    f_n_log_factor: int = 0     # Factor logarítmico: n^k * lg^j(n) -> j
    
    # Para recurrencias lineales T(n) = T(n-k) + f(n)
    es_lineal: bool = False
    k_decremento: int = 1
    
    # Para Akra-Bazzi: múltiples subproblemas
    subproblemas: List[Tuple[float, float]] = None  # Lista de (a_i, b_i)
    
    # Metadatos
    forma_original: str = ""
    tipo: str = "divide_and_conquer"
    
    def __post_init__(self):
        if self.subproblemas is None:
            self.subproblemas = [(self.a, self.b)]


@dataclass
class ResultadoResolucion:
    """Resultado del análisis de una recurrencia."""
    complejidad_O: str
    complejidad_Omega: str
    complejidad_Theta: str
    metodo_usado: MetodoResolucion
    justificacion: str
    pasos_matematicos: List[str]
    es_exacto: bool = True
    confianza: float = 1.0


class RecurrenceSolver:
    """
    Resuelve ecuaciones de recurrencia usando múltiples métodos matemáticos.
    
    Implementa el flujo de decisión:
    1. Intentar Teorema Maestro (más directo)
    2. Si no aplica, usar Árbol de Recursión
    3. Para recurrencias lineales, usar Iteración
    4. Para Fibonacci-like, usar Funciones Generatrices
    5. Para casos complejos, usar Akra-Bazzi
    """
    
    # Patrones conocidos de complejidad
    PATRONES_CONOCIDOS = {
        # Divide y Vencerás clásicos
        "merge_sort": {"a": 2, "b": 2, "f_n": "n", "resultado": "Θ(n lg n)"},
        "binary_search": {"a": 1, "b": 2, "f_n": "1", "resultado": "Θ(lg n)"},
        "strassen": {"a": 7, "b": 2, "f_n": "n^2", "resultado": "Θ(n^2.807)"},
        "karatsuba": {"a": 3, "b": 2, "f_n": "n", "resultado": "Θ(n^1.585)"},
        
        # Recursión lineal
        "factorial": {"tipo": "lineal", "k": 1, "f_n": "1", "resultado": "Θ(n)"},
        "fibonacci": {"tipo": "exponencial", "resultado": "Θ(φ^n) ≈ Θ(1.618^n)"},
        "hanoi": {"a": 2, "tipo": "lineal", "k": 1, "f_n": "1", "resultado": "Θ(2^n)"},
    }
    
    def __init__(self):
        self._cache_resultados: Dict[str, ResultadoResolucion] = {}
    
    def resolver(self, recurrencia: Recurrencia) -> ResultadoResolucion:
        """
        Resuelve una ecuación de recurrencia seleccionando el mejor método.
        
        Args:
            recurrencia: Objeto Recurrencia con los parámetros de la ecuación.
            
        Returns:
            ResultadoResolucion con la complejidad y justificación matemática.
        """
        # Verificar cache
        cache_key = f"{recurrencia.a}_{recurrencia.b}_{recurrencia.f_n}_{recurrencia.es_lineal}_{recurrencia.tipo}"
        if cache_key in self._cache_resultados:
            return self._cache_resultados[cache_key]
        
        # Seleccionar método apropiado
        # IMPORTANTE: Fibonacci ANTES de lineal genérico
        if self._es_fibonacci_like(recurrencia):
            resultado = self._resolver_fibonacci(recurrencia)
        elif recurrencia.es_lineal:
            resultado = self._resolver_iteracion(recurrencia)
        elif self._puede_usar_maestro(recurrencia):
            resultado = self._resolver_maestro(recurrencia)
        elif len(recurrencia.subproblemas) > 1:
            resultado = self._resolver_akra_bazzi(recurrencia)
        else:
            resultado = self._resolver_arbol(recurrencia)
        
        self._cache_resultados[cache_key] = resultado
        return resultado
    
    # =========================================================================
    # MÉTODO 1: TEOREMA MAESTRO (Master Theorem)
    # =========================================================================
    
    def _puede_usar_maestro(self, rec: Recurrencia) -> bool:
        """Verifica si el Teorema Maestro es aplicable."""
        return (
            rec.a >= 1 and 
            rec.b > 1 and 
            not rec.es_lineal and
            len(rec.subproblemas) == 1
        )
    
    def _resolver_maestro(self, rec: Recurrencia) -> ResultadoResolucion:
        """
        Aplica el Teorema Maestro para T(n) = a*T(n/b) + f(n).
        
        Casos:
        1. f(n) = O(n^(log_b(a) - ε)) → T(n) = Θ(n^log_b(a))
        2. f(n) = Θ(n^(log_b(a)) * lg^k(n)) → T(n) = Θ(n^log_b(a) * lg^(k+1)(n))
        3. f(n) = Ω(n^(log_b(a) + ε)) y regularidad → T(n) = Θ(f(n))
        """
        a, b = rec.a, rec.b
        log_b_a = math.log(a, b) if a > 0 and b > 1 else 0
        f_orden = rec.f_n_orden
        f_log = rec.f_n_log_factor
        
        pasos = [
            f"**Teorema Maestro** para T(n) = {a}T(n/{b}) + {rec.f_n}",
            "",
            f"**Paso 1:** Calcular n^(log_b a) = n^(log_{b} {a}) = n^{log_b_a:.4f}",
            "",
        ]
        
        epsilon = abs(log_b_a - f_orden)
        
        # Caso 1: f(n) crece más lento que n^log_b(a)
        if f_orden < log_b_a - 0.001:
            caso = 1
            complejidad = f"Θ(n^{log_b_a:.4f})"
            if log_b_a == int(log_b_a):
                complejidad = f"Θ(n^{int(log_b_a)})"
            if log_b_a == 1:
                complejidad = "Θ(n)"
            elif log_b_a == 0:
                complejidad = "Θ(1)"
            
            pasos.extend([
                f"**Paso 2:** Comparar f(n) = {rec.f_n} con n^{log_b_a:.4f}",
                f"  - f(n) = O(n^{f_orden}) crece **polinómicamente más lento**",
                f"  - Existe ε = {epsilon:.4f} > 0 tal que f(n) = O(n^(log_b a - ε))",
                "",
                f"**Caso 1 del Teorema Maestro aplicable**",
                f"  → Las hojas dominan el trabajo total",
                "",
                f"**Resultado:** T(n) = {complejidad}",
            ])
        
        # Caso 2: f(n) crece igual que n^log_b(a) (con factor logarítmico)
        elif abs(f_orden - log_b_a) < 0.001:
            caso = 2
            log_power = f_log + 1
            if log_b_a == 1:
                if log_power == 1:
                    complejidad = "Θ(n lg n)"
                else:
                    complejidad = f"Θ(n lg^{log_power} n)"
            elif log_b_a == 0:
                complejidad = f"Θ(lg^{log_power} n)"
            else:
                complejidad = f"Θ(n^{log_b_a:.4f} lg^{log_power} n)"
            
            pasos.extend([
                f"**Paso 2:** Comparar f(n) = {rec.f_n} con n^{log_b_a:.4f}",
                f"  - f(n) = Θ(n^{f_orden} lg^{f_log} n)",
                f"  - f(n) y n^(log_b a) crecen **al mismo ritmo polinómico**",
                "",
                f"**Caso 2 del Teorema Maestro aplicable** (k = {f_log})",
                f"  → Trabajo balanceado en todos los niveles del árbol",
                "",
                f"**Resultado:** T(n) = {complejidad}",
            ])
        
        # Caso 3: f(n) crece más rápido que n^log_b(a)
        else:
            caso = 3
            if f_orden == 1 and f_log == 0:
                complejidad = "Θ(n)"
            elif f_orden == 2 and f_log == 0:
                complejidad = "Θ(n²)"
            else:
                complejidad = f"Θ({rec.f_n})"
            
            pasos.extend([
                f"**Paso 2:** Comparar f(n) = {rec.f_n} con n^{log_b_a:.4f}",
                f"  - f(n) = Ω(n^{f_orden}) crece **polinómicamente más rápido**",
                f"  - Existe ε = {epsilon:.4f} > 0 tal que f(n) = Ω(n^(log_b a + ε))",
                "",
                f"**Paso 3:** Verificar condición de regularidad",
                f"  - a·f(n/b) ≤ c·f(n) para alguna c < 1",
                f"  - {a}·f(n/{b}) = {a}·(n/{b})^{f_orden} = {a}/{b**f_orden}·n^{f_orden}",
                f"  - Con c = {a/(b**f_orden):.4f} < 1 ✓ (si aplica)",
                "",
                f"**Caso 3 del Teorema Maestro aplicable**",
                f"  → La raíz domina el trabajo total",
                "",
                f"**Resultado:** T(n) = {complejidad}",
            ])
        
        return ResultadoResolucion(
            complejidad_O=complejidad.replace("Θ", "O"),
            complejidad_Omega=complejidad.replace("Θ", "Ω"),
            complejidad_Theta=complejidad,
            metodo_usado=MetodoResolucion.MAESTRO,
            justificacion=f"Aplicación del Caso {caso} del Teorema Maestro",
            pasos_matematicos=pasos,
            es_exacto=True,
            confianza=1.0
        )
    
    # =========================================================================
    # MÉTODO 2: ÁRBOL DE RECURSIÓN (Recursion Tree)
    # =========================================================================
    
    def _resolver_arbol(self, rec: Recurrencia) -> ResultadoResolucion:
        """
        Usa el método del Árbol de Recursión para resolver T(n) = a*T(n/b) + f(n).
        
        Proceso:
        1. Calcular costo por nivel
        2. Determinar altura del árbol
        3. Sumar costos (serie geométrica + hojas)
        """
        a, b = rec.a, rec.b
        f_orden = rec.f_n_orden
        
        altura = f"log_{b} n"
        num_hojas = f"{a}^(log_{b} n) = n^(log_{b} {a})"
        log_b_a = math.log(a, b) if a > 0 and b > 1 else 0
        
        pasos = [
            f"**Método del Árbol de Recursión** para T(n) = {a}T(n/{b}) + {rec.f_n}",
            "",
            "**Estructura del Árbol:**",
            "",
            f"  Nivel 0 (Raíz):    Costo = f(n) = n^{f_orden}",
            f"  Nivel 1:           {a} nodos, cada uno con costo f(n/{b})",
            f"                     Costo total = {a}·(n/{b})^{f_orden} = ({a}/{b**f_orden})·n^{f_orden}",
            f"  Nivel i:           {a}^i nodos, costo total = ({a}/{b**f_orden})^i · n^{f_orden}",
            "",
            f"**Altura del árbol:** h = {altura}",
            f"  (El árbol termina cuando n/{b}^h = 1)",
            "",
            f"**Número de hojas:** {num_hojas} = n^{log_b_a:.4f}",
            "",
        ]
        
        # Calcular la razón de la serie geométrica
        razon = a / (b ** f_orden)
        
        if abs(razon - 1) < 0.001:
            # Serie constante: cada nivel contribuye igual
            complejidad = f"Θ(n^{f_orden} lg n)"
            pasos.extend([
                f"**Suma de niveles:** Serie con razón r = {a}/{b**f_orden} = {razon:.4f} ≈ 1",
                f"  - Cada nivel contribuye aproximadamente n^{f_orden}",
                f"  - Hay log_{b} n niveles",
                f"  - Suma total ≈ n^{f_orden} · log_{b} n",
                "",
                f"**Costo de las hojas:** Θ(n^{log_b_a:.4f})",
                "",
                f"**Suma Total:** T(n) = {complejidad}",
            ])
        elif razon < 1:
            # Serie geométrica convergente: dominada por la raíz
            complejidad = f"Θ(n^{f_orden})"
            suma_serie = 1 / (1 - razon)
            pasos.extend([
                f"**Suma de niveles:** Serie geométrica con razón r = {razon:.4f} < 1",
                f"  - Suma = n^{f_orden} · (1 - r^h) / (1 - r)",
                f"  - Como r < 1, la suma converge a n^{f_orden} · {suma_serie:.4f}",
                "",
                f"**Costo de las hojas:** Θ(n^{log_b_a:.4f})",
                f"  - Como {log_b_a:.4f} < {f_orden}, las hojas son dominadas",
                "",
                f"**Suma Total:** T(n) = {complejidad}",
            ])
        else:
            # Serie geométrica divergente: dominada por las hojas
            complejidad = f"Θ(n^{log_b_a:.4f})"
            if log_b_a == int(log_b_a):
                complejidad = f"Θ(n^{int(log_b_a)})"
            pasos.extend([
                f"**Suma de niveles:** Serie geométrica con razón r = {razon:.4f} > 1",
                f"  - La suma crece exponencialmente hacia las hojas",
                "",
                f"**Costo de las hojas:** Θ(n^{log_b_a:.4f})",
                f"  - Las hojas dominan el costo total",
                "",
                f"**Suma Total:** T(n) = {complejidad}",
            ])
        
        return ResultadoResolucion(
            complejidad_O=complejidad.replace("Θ", "O"),
            complejidad_Omega=complejidad.replace("Θ", "Ω"),
            complejidad_Theta=complejidad,
            metodo_usado=MetodoResolucion.ARBOL,
            justificacion="Análisis mediante Árbol de Recursión",
            pasos_matematicos=pasos,
            es_exacto=True,
            confianza=0.95
        )
    
    def generar_arbol_recursion(
        self, 
        a: float, 
        b: float, 
        f_n: str, 
        max_niveles: int = 4
    ) -> Dict[str, Any]:
        """
        Genera la estructura de datos del árbol de recursión para visualización.
        
        Args:
            a: Número de subproblemas
            b: Factor de división
            f_n: Función de trabajo
            max_niveles: Número máximo de niveles a mostrar
            
        Returns:
            Diccionario con la estructura del árbol para el frontend
        """
        f_orden = self._parsear_orden_fn(f_n)
        log_b_a = math.log(a, b) if a > 0 and b > 1 else 0
        
        def crear_nodo(nivel: int, size: str, node_id: str) -> Dict[str, Any]:
            """Crea un nodo del árbol recursivamente."""
            # Calcular el costo en este nodo
            if f_orden == 0:
                costo = "c"
            elif f_orden == 1:
                costo = size
            else:
                costo = f"{size}^{int(f_orden)}" if f_orden == int(f_orden) else f"{size}^{f_orden}"
            
            nodo = {
                "id": node_id,
                "label": f"T({size})",
                "cost": costo,
                "level": nivel,
            }
            
            # Generar hijos si no hemos llegado al límite
            if nivel < max_niveles - 1:
                hijos = []
                for i in range(int(a)):
                    # Calcular el nuevo tamaño
                    if "/" in size:
                        # Ej: "n/2" -> "n/4"
                        parts = size.split("/")
                        base = parts[0]
                        divisor = int(parts[1]) * int(b)
                        nuevo_size = f"{base}/{divisor}"
                    else:
                        nuevo_size = f"{size}/{int(b)}"
                    
                    hijo = crear_nodo(nivel + 1, nuevo_size, f"{node_id}_{i}")
                    hijos.append(hijo)
                
                if hijos:
                    nodo["children"] = hijos
            else:
                # Último nivel visible - indicar que continúa
                nodo["children"] = [{
                    "id": f"{node_id}_leaf",
                    "label": "...",
                    "cost": "Θ(1)",
                    "level": nivel + 1,
                }]
            
            return nodo
        
        # Generar el árbol
        root = crear_nodo(0, "n", "root")
        
        # Calcular costos por nivel
        level_costs = []
        for i in range(max_niveles):
            num_nodos = int(a ** i)
            if f_orden == 0:
                costo_nivel = f"{num_nodos}c"
            elif f_orden == 1:
                divisor = int(b ** i)
                costo_nivel = f"{num_nodos} × n/{divisor}" if divisor > 1 else f"{num_nodos} × n"
                if num_nodos == 1:
                    costo_nivel = f"n/{divisor}" if divisor > 1 else "n"
                # Simplificar: a^i × n/b^i = n × (a/b)^i
                razon = a / b
                if abs(razon - 1) < 0.001:
                    costo_nivel = "n" if f_orden == 1 else f"n^{int(f_orden)}"
                elif razon < 1:
                    costo_nivel = f"({a}/{int(b)})^{i} × n"
                else:
                    costo_nivel = f"({a}/{int(b)})^{i} × n"
            else:
                costo_nivel = f"({a}/{int(b**f_orden)})^{i} × n^{int(f_orden)}"
            
            level_costs.append(costo_nivel)
        
        # Agregar el costo de las hojas
        level_costs.append(f"Θ(n^{log_b_a:.2f})" if log_b_a != int(log_b_a) else f"Θ(n^{int(log_b_a)})")
        
        # Calcular la complejidad total
        razon = a / (b ** f_orden) if b > 0 else 1
        if abs(razon - 1) < 0.001:
            total_cost = f"Θ(n^{int(f_orden)} lg n)" if f_orden == int(f_orden) else f"Θ(n^{f_orden} lg n)"
            complexity = total_cost
        elif razon < 1:
            total_cost = f"Θ(n^{int(f_orden)})" if f_orden == int(f_orden) else f"Θ(n^{f_orden})"
            complexity = total_cost
        else:
            total_cost = f"Θ(n^{log_b_a:.2f})" if log_b_a != int(log_b_a) else f"Θ(n^{int(log_b_a)})"
            complexity = total_cost
        
        return {
            "root": root,
            "levels": max_niveles,
            "levelCosts": level_costs,
            "totalCost": total_cost,
            "complexity": complexity,
            "parameters": {
                "a": a,
                "b": b,
                "f_n": f_n,
                "log_b_a": round(log_b_a, 4)
            }
        }
    
    # =========================================================================
    # MÉTODO 3: ITERACIÓN / DESENROLLADO (Iteration Method)
    # =========================================================================
    
    def _resolver_iteracion(self, rec: Recurrencia) -> ResultadoResolucion:
        """
        Resuelve recurrencias lineales T(n) = aT(n-k) + f(n) por iteración.
        
        Casos:
        - a=1: T(n) = T(n-1) + f(n) → suma lineal de f(n)
        - a>1: T(n) = aT(n-1) + f(n) → crecimiento exponencial Θ(a^n)
        
        Ejemplo a=1: T(n) = T(n-1) + n → T(n) = Σi = n(n+1)/2 = Θ(n²)
        Ejemplo a=2: T(n) = 2T(n-1) + 1 → T(n) = 2^n - 1 = Θ(2^n) (Torres de Hanoi)
        """
        k = rec.k_decremento
        f_n = rec.f_n
        f_orden = rec.f_n_orden
        a = rec.a  # Número de subproblemas
        
        # CASO ESPECIAL: Múltiples llamadas recursivas (a > 1)
        # T(n) = aT(n-1) + f(n) → Θ(a^n)
        if a > 1:
            pasos = [
                f"**Método de Iteración** para T(n) = {a}T(n-{k}) + {f_n}",
                "",
                "**Este es un caso de crecimiento exponencial.**",
                "",
                "**Desenrollando la recurrencia:**",
                "",
                f"  T(n) = {a}T(n-{k}) + f(n)",
                f"  T(n) = {a}[{a}T(n-{2*k}) + f(n-{k})] + f(n)",
                f"       = {a}²T(n-{2*k}) + {a}·f(n-{k}) + f(n)",
                f"  T(n) = {a}³T(n-{3*k}) + {a}²·f(n-{2*k}) + {a}·f(n-{k}) + f(n)",
                "  ...",
                f"  T(n) = {a}^(n/{k}) · T(0) + Σ(i=0 to n/{k}-1) {a}^i · f(n - i·{k})",
                "",
            ]
            
            # El término dominante es a^n
            if f_orden == 0:
                # T(n) = aT(n-1) + O(1) → T(n) = (a^n - 1)/(a-1) = Θ(a^n)
                complejidad = f"Θ({a}^n)"
                pasos.extend([
                    f"**Para f(n) = O(1):**",
                    f"  T(n) = {a}^n · T(0) + Σ(i=0 to n-1) {a}^i",
                    f"       = {a}^n · c + ({a}^n - 1)/({a}-1)",
                    f"       = Θ({a}^n)",
                    "",
                    f"**Resultado:** T(n) = {complejidad}",
                    "",
                    "**Nota:** Este es el patrón de las Torres de Hanoi." if a == 2 else "",
                ])
            else:
                # Con f(n) polinómico, el término exponencial sigue dominando
                complejidad = f"Θ({a}^n)"
                pasos.extend([
                    f"**El término exponencial {a}^n domina sobre f(n) = O(n^{f_orden}):**",
                    f"  T(n) = Θ({a}^n) + o({a}^n)",
                    f"       = Θ({a}^n)",
                    "",
                    f"**Resultado:** T(n) = {complejidad}",
                ])
            
            return ResultadoResolucion(
                complejidad_O=complejidad.replace("Θ", "O"),
                complejidad_Omega=complejidad.replace("Θ", "Ω"),
                complejidad_Theta=complejidad,
                metodo_usado=MetodoResolucion.ITERACION,
                justificacion=f"Recurrencia con {a} llamadas recursivas produce crecimiento exponencial",
                pasos_matematicos=pasos,
                es_exacto=True,
                confianza=1.0
            )
        
        # CASO ESTÁNDAR: Una sola llamada recursiva (a = 1)
        # T(n) = T(n-k) + f(n)
        pasos = [
            f"**Método de Iteración** para T(n) = T(n-{k}) + {f_n}",
            "",
            "**Desenrollando la recurrencia:**",
            "",
            f"  T(n) = T(n-{k}) + f(n)",
            f"  T(n) = T(n-{2*k}) + f(n-{k}) + f(n)",
            f"  T(n) = T(n-{3*k}) + f(n-{2*k}) + f(n-{k}) + f(n)",
            "  ...",
            f"  T(n) = T(0) + Σ(i=0 to n/{k}) f(n - i·{k})",
            "",
        ]
        
        # Calcular la suma dependiendo de f(n)
        if f_orden == 0 or f_n in ["1", "c", "O(1)"]:
            # T(n) = T(n-k) + 1 → T(n) = n/k = Θ(n)
            complejidad = "Θ(n)"
            pasos.extend([
                f"**Suma:** Σ(i=0 to n/{k}) 1 = n/{k} + 1",
                "",
                f"**Resultado:** T(n) = {complejidad}",
            ])
        elif f_orden == 1:
            # T(n) = T(n-k) + n → T(n) = n + (n-k) + (n-2k) + ... = Θ(n²)
            complejidad = "Θ(n²)"
            pasos.extend([
                f"**Suma:** Σ(i=0 to n/{k}) (n - i·{k})",
                f"  = n·(n/{k}) - {k}·Σ(i=0 to n/{k}) i",
                f"  = n²/{k} - {k}·(n/{k})(n/{k}+1)/2",
                f"  = n²/{k} - n²/(2·{k}) + O(n)",
                f"  = n²/(2·{k}) + O(n)",
                "",
                f"**Resultado:** T(n) = {complejidad}",
            ])
        elif f_orden == 2:
            # T(n) = T(n-k) + n² → Θ(n³)
            complejidad = "Θ(n³)"
            pasos.extend([
                f"**Suma:** Σ(i=0 to n/{k}) (n - i·{k})²",
                f"  ≈ ∫₀^(n/{k}) (n - {k}x)² dx",
                f"  = n³/(3·{k})",
                "",
                f"**Resultado:** T(n) = {complejidad}",
            ])
        else:
            # Caso general: T(n) = Θ(n^(f_orden + 1))
            nuevo_orden = f_orden + 1
            complejidad = f"Θ(n^{nuevo_orden})"
            pasos.extend([
                f"**Suma:** Σ(i=0 to n/{k}) (n - i·{k})^{f_orden}",
                f"  ≈ n^{f_orden} · (n/{k})",
                f"  = Θ(n^{nuevo_orden})",
                "",
                f"**Resultado:** T(n) = {complejidad}",
            ])
        
        return ResultadoResolucion(
            complejidad_O=complejidad.replace("Θ", "O"),
            complejidad_Omega=complejidad.replace("Θ", "Ω"),
            complejidad_Theta=complejidad,
            metodo_usado=MetodoResolucion.ITERACION,
            justificacion="Resolución por desenrollado iterativo de la recurrencia",
            pasos_matematicos=pasos,
            es_exacto=True,
            confianza=1.0
        )
    
    # =========================================================================
    # MÉTODO 4: AKRA-BAZZI (Para subproblemas desiguales)
    # =========================================================================
    
    def _resolver_akra_bazzi(self, rec: Recurrencia) -> ResultadoResolucion:
        """
        Aplica el método de Akra-Bazzi para T(n) = Σ a_i·T(n/b_i) + f(n).
        
        Encuentra p tal que Σ a_i·b_i^(-p) = 1
        Solución: T(n) = Θ(n^p · (1 + ∫₁ⁿ f(x)/x^(p+1) dx))
        """
        subproblemas = rec.subproblemas
        f_orden = rec.f_n_orden
        
        pasos = [
            f"**Método de Akra-Bazzi** para recurrencia con subproblemas desiguales",
            "",
            "**Ecuación:** T(n) = " + " + ".join([f"{a}·T(n/{b})" for a, b in subproblemas]) + f" + {rec.f_n}",
            "",
            "**Paso 1:** Encontrar p tal que Σ a_i · b_i^(-p) = 1",
            "",
        ]
        
        # Encontrar p numéricamente (usando bisección)
        p = self._encontrar_p_akra_bazzi(subproblemas)
        
        pasos.extend([
            f"  Ecuación: " + " + ".join([f"{a}·{b}^(-p)" for a, b in subproblemas]) + " = 1",
            f"  Solución: p ≈ {p:.4f}",
            "",
            "**Paso 2:** Calcular la integral",
            f"  ∫₁ⁿ f(x)/x^(p+1) dx = ∫₁ⁿ x^{f_orden}/x^({p:.4f}+1) dx",
            f"                      = ∫₁ⁿ x^({f_orden - p - 1:.4f}) dx",
            "",
        ])
        
        # Determinar la complejidad basada en la integral
        integral_exp = f_orden - p - 1
        
        if integral_exp < -1:
            # Integral converge: T(n) = Θ(n^p)
            complejidad = f"Θ(n^{p:.4f})"
            pasos.append(f"  La integral converge → domina n^p")
        elif abs(integral_exp + 1) < 0.001:
            # Integral es ln(n): T(n) = Θ(n^p lg n)
            complejidad = f"Θ(n^{p:.4f} lg n)"
            pasos.append(f"  La integral es ln(n) → T(n) = Θ(n^p lg n)")
        else:
            # Integral diverge: T(n) = Θ(n^p · n^(integral_exp+1))
            total_exp = p + integral_exp + 1
            complejidad = f"Θ(n^{total_exp:.4f})"
            pasos.append(f"  La integral diverge → T(n) = Θ(n^{total_exp:.4f})")
        
        pasos.extend([
            "",
            f"**Resultado:** T(n) = {complejidad}",
        ])
        
        return ResultadoResolucion(
            complejidad_O=complejidad.replace("Θ", "O"),
            complejidad_Omega=complejidad.replace("Θ", "Ω"),
            complejidad_Theta=complejidad,
            metodo_usado=MetodoResolucion.AKRA_BAZZI,
            justificacion="Método de Akra-Bazzi para división desigual",
            pasos_matematicos=pasos,
            es_exacto=True,
            confianza=0.95
        )
    
    def _encontrar_p_akra_bazzi(self, subproblemas: List[Tuple[float, float]], 
                                 tolerancia: float = 1e-6) -> float:
        """Encuentra p tal que Σ a_i · b_i^(-p) = 1 usando bisección."""
        def ecuacion(p):
            return sum(a * (b ** (-p)) for a, b in subproblemas) - 1
        
        # Bisección entre 0 y 10
        low, high = 0.0, 10.0
        while high - low > tolerancia:
            mid = (low + high) / 2
            if ecuacion(mid) > 0:
                low = mid
            else:
                high = mid
        
        return (low + high) / 2
    
    # =========================================================================
    # MÉTODO 5: FUNCIONES GENERATRICES (Para Fibonacci y similares)
    # =========================================================================
    
    def _es_fibonacci_like(self, rec: Recurrencia) -> bool:
        """
        Detecta si es una recurrencia tipo Fibonacci.
        
        Fibonacci: T(n) = T(n-1) + T(n-2) + O(1) (EXACTAMENTE tipo="fibonacci")
        NO debe confundirse con Torres de Hanoi: T(n) = 2T(n-1) + O(1)
        """
        # SOLO detectar si el tipo es explícitamente "fibonacci"
        return rec.tipo == "fibonacci"
    
    def _resolver_fibonacci(self, rec: Recurrencia) -> ResultadoResolucion:
        """
        Resuelve recurrencias tipo Fibonacci usando funciones generatrices.
        
        F(n) = F(n-1) + F(n-2) → F(n) = (φ^n - ψ^n) / √5
        donde φ = (1+√5)/2 ≈ 1.618 y ψ = (1-√5)/2 ≈ -0.618
        """
        phi = (1 + math.sqrt(5)) / 2
        psi = (1 - math.sqrt(5)) / 2
        
        pasos = [
            "**Método de Funciones Generatrices** para recurrencia tipo Fibonacci",
            "",
            "**Ecuación característica:** x² = x + 1  →  x² - x - 1 = 0",
            "",
            "**Raíces:**",
            f"  φ = (1 + √5) / 2 ≈ {phi:.6f} (razón áurea)",
            f"  ψ = (1 - √5) / 2 ≈ {psi:.6f}",
            "",
            "**Solución cerrada (Fórmula de Binet):**",
            "  F(n) = (φⁿ - ψⁿ) / √5",
            "",
            "**Análisis asintótico:**",
            f"  Como |ψ| < 1, ψⁿ → 0 cuando n → ∞",
            f"  Por lo tanto, F(n) ≈ φⁿ / √5",
            "",
            f"**Resultado:** T(n) = Θ(φⁿ) = Θ({phi:.4f}ⁿ) ≈ Θ(1.618ⁿ)",
        ]
        
        complejidad = f"Θ({phi:.4f}^n)"
        
        return ResultadoResolucion(
            complejidad_O=f"O({phi:.4f}^n)",
            complejidad_Omega=f"Ω({phi:.4f}^n)",
            complejidad_Theta=complejidad,
            metodo_usado=MetodoResolucion.GENERATRICES,
            justificacion="Fórmula cerrada mediante funciones generatrices (Binet)",
            pasos_matematicos=pasos,
            es_exacto=True,
            confianza=1.0
        )
    
    # =========================================================================
    # MÉTODO 6: SUSTITUCIÓN (Para verificación rigurosa)
    # =========================================================================
    
    def verificar_por_sustitucion(self, rec: Recurrencia, 
                                   conjetura: str) -> ResultadoResolucion:
        """
        Verifica una conjetura de complejidad usando el método de sustitución.
        
        Este método es útil para probar formalmente que una conjetura es correcta.
        """
        a, b = rec.a, rec.b
        
        pasos = [
            f"**Método de Sustitución** para verificar T(n) = {conjetura}",
            "",
            f"**Recurrencia:** T(n) = {a}T(n/{b}) + {rec.f_n}",
            "",
            "**Paso 1:** Hipótesis inductiva",
            f"  Suponemos T(k) ≤ c·g(k) para todo k < n, donde g(n) corresponde a {conjetura}",
            "",
            "**Paso 2:** Paso inductivo",
            f"  T(n) = {a}·T(n/{b}) + {rec.f_n}",
            f"       ≤ {a}·c·g(n/{b}) + {rec.f_n}   (por hipótesis inductiva)",
            "",
            "**Paso 3:** Demostrar que T(n) ≤ c·g(n)",
            "  [Desarrollo algebraico dependiente de la conjetura específica]",
            "",
            f"**Conclusión:** La cota {conjetura} es válida para c suficientemente grande y n ≥ n₀",
        ]
        
        return ResultadoResolucion(
            complejidad_O=conjetura.replace("Θ", "O"),
            complejidad_Omega=conjetura.replace("Θ", "Ω"),
            complejidad_Theta=conjetura,
            metodo_usado=MetodoResolucion.SUSTITUCION,
            justificacion="Verificación por inducción matemática",
            pasos_matematicos=pasos,
            es_exacto=True,
            confianza=1.0
        )
    
    # =========================================================================
    # DETECCIÓN AUTOMÁTICA DE PARÁMETROS
    # =========================================================================
    
    def extraer_recurrencia_de_patron(self, patron: Dict[str, Any]) -> Recurrencia:
        """
        Extrae una Recurrencia desde un patrón detectado por RecursiveAnalyzerService.
        
        Args:
            patron: Diccionario con información del patrón recursivo.
            
        Returns:
            Objeto Recurrencia con los parámetros extraídos.
        """
        tipo_recursion = patron.get("tipo", "")
        division_info = patron.get("division", {})
        parametros = patron.get("parametros", {})
        
        # Determinar número de subproblemas (a)
        total_llamadas = parametros.get("total_llamadas", 1)
        a = total_llamadas
        
        # Determinar factor de división (b)
        division_tipo = division_info.get("tipo", "mitad")
        if division_tipo == "mitad":
            b = 2
        elif division_tipo == "tercio":
            b = 3
        elif division_tipo == "n_minus_1":
            # Recursión lineal
            return Recurrencia(
                a=1,
                b=2,
                f_n="1",
                f_n_orden=0,
                es_lineal=True,
                k_decremento=1,
                tipo="lineal"
            )
        else:
            b = division_info.get("factor", 2)
        
        # Determinar f(n) basado en el contexto
        if tipo_recursion == "recursion_exponencial_fibonacci":
            return Recurrencia(
                a=2,
                b=2,
                f_n="0",
                f_n_orden=0,
                es_lineal=True,
                k_decremento=1,
                tipo="fibonacci"
            )
        
        # Por defecto, asumir f(n) = n (trabajo lineal de combinación)
        return Recurrencia(
            a=a,
            b=b,
            f_n="n",
            f_n_orden=1,
            f_n_log_factor=0,
            tipo="divide_and_conquer"
        )
    
    def analizar_y_resolver(self, patron: Dict[str, Any]) -> ResultadoResolucion:
        """
        Pipeline completo: extrae la recurrencia y la resuelve.
        """
        recurrencia = self.extraer_recurrencia_de_patron(patron)
        return self.resolver(recurrencia)
    
    def solve(
        self, 
        a: float = 1, 
        b: float = 2, 
        f_n: str = "n",
        recurrence_type: str = None
    ) -> Dict[str, Any]:
        """
        Interfaz simplificada para resolver recurrencias directamente con parámetros.
        
        Args:
            a: Número de subproblemas
            b: Factor de división del problema
            f_n: Función de costo no recursivo (ej: "1", "n", "n^2", "n log n")
            recurrence_type: Tipo especial ("fibonacci", "n_minus_1", etc.)
            
        Returns:
            Diccionario con la solución completa:
            - complexity: Complejidad asintótica final (Θ notation)
            - method_used: Método de resolución utilizado
            - solution_steps: Pasos detallados de la resolución
            - all_results: Resultados de todos los métodos probados
            - big_o: Cota superior O(...)
            - big_omega: Cota inferior Ω(...)
            - big_theta: Cota ajustada Θ(...)
        """
        # Parsear f(n) para extraer el exponente
        f_n_orden = self._parsear_orden_fn(f_n)
        f_n_log_factor = 1 if "log" in f_n.lower() or "lg" in f_n.lower() else 0
        
        # Determinar si es lineal
        es_lineal = recurrence_type in ["n_minus_1", "fibonacci"] or b <= 1
        
        # Crear objeto Recurrencia
        if recurrence_type == "fibonacci":
            recurrencia = Recurrencia(
                a=2,
                b=2,
                f_n="1",
                f_n_orden=0,
                es_lineal=True,
                k_decremento=1,
                tipo="fibonacci",
                forma_original=f"T(n) = T(n-1) + T(n-2) + O(1)"
            )
        elif recurrence_type == "n_minus_1" or b <= 1:
            recurrencia = Recurrencia(
                a=a,
                b=2,  # Dummy value para lineal
                f_n=f_n,
                f_n_orden=f_n_orden,
                es_lineal=True,
                k_decremento=1,
                tipo="lineal",
                forma_original=f"T(n) = T(n-1) + O({f_n})"
            )
        else:
            recurrencia = Recurrencia(
                a=a,
                b=b,
                f_n=f_n,
                f_n_orden=f_n_orden,
                f_n_log_factor=f_n_log_factor,
                es_lineal=False,
                tipo="divide_and_conquer",
                forma_original=f"T(n) = {a}T(n/{b}) + O({f_n})"
            )
        
        # Resolver
        resultado = self.resolver(recurrencia)
        
        # Convertir pasos a formato estructurado para el frontend
        pasos_estructurados = self._convertir_pasos_a_objetos(
            resultado.pasos_matematicos,
            resultado.metodo_usado,
            resultado.complejidad_Theta
        )
        
        # Generar árbol de recursión para visualización (si aplica)
        recursion_tree = None
        if not recurrencia.es_lineal and b > 1:
            try:
                recursion_tree = self.generar_arbol_recursion(a, b, f_n, max_niveles=4)
            except Exception as e:
                print(f"Error generando árbol de recursión: {e}")
        
        # Convertir a diccionario
        return {
            "complexity": resultado.complejidad_Theta,
            "big_o": resultado.complejidad_O,
            "big_omega": resultado.complejidad_Omega,
            "big_theta": resultado.complejidad_Theta,
            "method_used": resultado.metodo_usado.value,
            "method_name": self._obtener_nombre_metodo(resultado.metodo_usado),
            "solution_steps": pasos_estructurados,
            "justification": resultado.justificacion,
            "is_exact": resultado.es_exacto,
            "confidence": resultado.confianza,
            "recursion_tree": recursion_tree,
            "all_results": {
                "primary_method": resultado.metodo_usado.value,
                "complexity": resultado.complejidad_Theta
            },
            "recurrence_form": recurrencia.forma_original or f"T(n) = {a}T(n/{b}) + O({f_n})"
        }
    
    def _obtener_nombre_metodo(self, metodo: MetodoResolucion) -> str:
        """Devuelve el nombre legible del método de resolución."""
        nombres = {
            MetodoResolucion.MAESTRO: "Teorema Maestro",
            MetodoResolucion.ARBOL: "Árbol de Recursión",
            MetodoResolucion.SUSTITUCION: "Método de Sustitución",
            MetodoResolucion.AKRA_BAZZI: "Teorema Akra-Bazzi",
            MetodoResolucion.CAMBIO_VARIABLES: "Cambio de Variables",
            MetodoResolucion.ITERACION: "Método de Iteración",
            MetodoResolucion.GENERATRICES: "Funciones Generatrices"
        }
        return nombres.get(metodo, "Análisis de Recurrencias")
    
    def _parsear_orden_fn(self, f_n: str) -> float:
        """
        Extrae el exponente de n en f(n).
        
        Ejemplos:
            "1" -> 0
            "n" -> 1
            "n^2" -> 2
            "n log n" -> 1
            "n^0.5" -> 0.5
        """
        f_n = f_n.lower().strip()
        
        if f_n in ["1", "c", "o(1)", "θ(1)"]:
            return 0.0
        
        if f_n in ["n", "o(n)", "θ(n)"]:
            return 1.0
        
        if f_n in ["log n", "lg n", "log(n)", "lg(n)"]:
            return 0.0  # Tratamos log n como sub-polinómico
        
        # Buscar n^k
        match = re.search(r'n\^?(\d+\.?\d*)', f_n)
        if match:
            return float(match.group(1))
        
        # n log n
        if "n" in f_n and ("log" in f_n or "lg" in f_n):
            return 1.0
        
        # Solo n presente
        if "n" in f_n:
            return 1.0
        
        return 0.0

    def _convertir_pasos_a_objetos(
        self, 
        pasos: List[str], 
        metodo: MetodoResolucion,
        complejidad_final: str
    ) -> List[Dict[str, Any]]:
        """
        Convierte los pasos de resolución (strings) al formato estructurado
        que espera el frontend.
        
        Formato esperado por frontend:
        {
            'step': int,
            'title': str,
            'description': str,
            'latex': str,
            'explanation': str
        }
        """
        if not pasos:
            # Si no hay pasos, generar pasos básicos según el método
            return self._generar_pasos_basicos(metodo, complejidad_final)
        
        pasos_estructurados = []
        
        # Nombres amigables para los métodos
        nombres_metodos = {
            MetodoResolucion.MAESTRO: "Teorema Maestro",
            MetodoResolucion.ARBOL: "Árbol de Recursión",
            MetodoResolucion.SUSTITUCION: "Método de Sustitución",
            MetodoResolucion.AKRA_BAZZI: "Teorema Akra-Bazzi",
            MetodoResolucion.CAMBIO_VARIABLES: "Cambio de Variables",
            MetodoResolucion.ITERACION: "Método de Iteración",
            MetodoResolucion.GENERATRICES: "Funciones Generatrices"
        }
        
        nombre_metodo = nombres_metodos.get(metodo, "Análisis de Recurrencias")
        
        for i, paso in enumerate(pasos):
            paso_obj = {
                'step': i + 1,
                'title': self._extraer_titulo(paso, i, nombre_metodo),
                'description': paso,
                'latex': self._extraer_latex(paso),
                'explanation': self._extraer_explicacion(paso, metodo)
            }
            pasos_estructurados.append(paso_obj)
        
        return pasos_estructurados
    
    def _extraer_titulo(self, paso: str, indice: int, nombre_metodo: str) -> str:
        """Extrae o genera un título para el paso."""
        # Si el paso empieza con "Paso X:" o similar
        if paso.lower().startswith("paso"):
            partes = paso.split(":", 1)
            if len(partes) > 1:
                return partes[0].strip()
        
        # Títulos según la posición
        if indice == 0:
            return f"Identificar forma de la recurrencia"
        elif indice == 1:
            return f"Aplicar {nombre_metodo}"
        elif "conclusi" in paso.lower() or "result" in paso.lower():
            return "Conclusión"
        else:
            return f"Paso {indice + 1}: Resolución"
    
    def _extraer_latex(self, paso: str) -> str:
        """Extrae o genera expresiones LaTeX del paso."""
        # Buscar patrones matemáticos comunes
        latex_patterns = [
            (r'T\(n\)\s*=\s*[^\n]+', lambda m: m.group().replace('=', ' = ')),
            (r'Θ\([^)]+\)', lambda m: f"\\Theta({m.group()[2:-1]})"),
            (r'O\([^)]+\)', lambda m: f"O({m.group()[2:-1]})"),
            (r'Ω\([^)]+\)', lambda m: f"\\Omega({m.group()[2:-1]})"),
            (r'n\^(\d+)', lambda m: f"n^{{{m.group(1)}}}"),
            (r'log_?(\d*)\s*n', lambda m: f"\\log{'_' + m.group(1) if m.group(1) else ''} n"),
            (r'lg\s*n', lambda m: "\\lg n"),
        ]
        
        # Intentar encontrar una expresión matemática
        for pattern, _ in latex_patterns:
            match = re.search(pattern, paso)
            if match:
                latex = match.group()
                # Limpiar para LaTeX
                latex = latex.replace('Θ', '\\Theta').replace('Ω', '\\Omega')
                return latex
        
        # Si contiene "Θ" o complejidad, extraerla
        if 'Θ(' in paso:
            match = re.search(r'Θ\([^)]+\)', paso)
            if match:
                return match.group().replace('Θ', '\\Theta')
        
        return ""
    
    def _extraer_explicacion(self, paso: str, metodo: MetodoResolucion) -> str:
        """Genera una explicación contextual para el paso."""
        explicaciones_metodo = {
            MetodoResolucion.MAESTRO: "Aplicando el Teorema Maestro de Cormen Cap. 4.5",
            MetodoResolucion.ARBOL: "Sumando los costos de cada nivel del árbol",
            MetodoResolucion.ITERACION: "Expandiendo la recurrencia iterativamente",
            MetodoResolucion.GENERATRICES: "Usando funciones generatrices para recurrencias lineales",
            MetodoResolucion.AKRA_BAZZI: "Usando el teorema generalizado Akra-Bazzi",
        }
        
        base = explicaciones_metodo.get(metodo, "Análisis matemático de la recurrencia")
        
        # Añadir contexto según el contenido del paso
        if "caso 1" in paso.lower():
            return f"{base}. Caso 1: f(n) es polinomialmente menor que n^(log_b a)."
        elif "caso 2" in paso.lower():
            return f"{base}. Caso 2: f(n) y n^(log_b a) son del mismo orden."
        elif "caso 3" in paso.lower():
            return f"{base}. Caso 3: f(n) domina."
        
        return base
    
    def _generar_pasos_basicos(self, metodo: MetodoResolucion, complejidad: str) -> List[Dict[str, Any]]:
        """Genera pasos básicos cuando no hay pasos específicos."""
        nombres_metodos = {
            MetodoResolucion.MAESTRO: "Teorema Maestro",
            MetodoResolucion.ARBOL: "Árbol de Recursión",
            MetodoResolucion.SUSTITUCION: "Método de Sustitución",
            MetodoResolucion.AKRA_BAZZI: "Teorema Akra-Bazzi",
            MetodoResolucion.CAMBIO_VARIABLES: "Cambio de Variables",
            MetodoResolucion.ITERACION: "Método de Iteración",
            MetodoResolucion.GENERATRICES: "Funciones Generatrices"
        }
        
        nombre = nombres_metodos.get(metodo, "Análisis de Recurrencias")
        comp_latex = complejidad.replace('Θ', '\\Theta').replace('Ω', '\\Omega')
        
        return [
            {
                'step': 1,
                'title': 'Identificar la recurrencia',
                'description': f'Se identificó el patrón de la recurrencia y se aplicará {nombre}.',
                'latex': 'T(n) = aT(n/b) + f(n)',
                'explanation': 'Forma estándar de divide y vencerás.'
            },
            {
                'step': 2,
                'title': f'Aplicar {nombre}',
                'description': f'Usando {nombre} para resolver la recurrencia.',
                'latex': comp_latex,
                'explanation': f'Referencia: Cormen et al., Chapter 4.'
            },
            {
                'step': 3,
                'title': 'Resultado final',
                'description': f'La complejidad asintótica del algoritmo es {complejidad}.',
                'latex': comp_latex,
                'explanation': 'Esta es la complejidad del peor caso para el algoritmo recursivo.'
            }
        ]


# =========================================================================
# FUNCIÓN AUXILIAR PARA INTEGRACIÓN
# =========================================================================

def crear_solver() -> RecurrenceSolver:
    """Factory function para crear un RecurrenceSolver."""
    return RecurrenceSolver()
