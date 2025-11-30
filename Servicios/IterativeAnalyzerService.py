"""
Servicio para análisis de complejidad de algoritmos ITERATIVOS.
Incluye resolución paso a paso de sumatorias para justificación matemática.

Basado en "Introduction to Algorithms" (Cormen et al.):
- Capítulo 5: Análisis Probabilístico y Variables Aleatorias Indicadoras
- Capítulo 2: Análisis de Insertion Sort (casos peor, mejor y promedio)
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Any
import ast

try:
    import sympy
    from sympy import Symbol, latex
except ImportError:
    sympy = None

if TYPE_CHECKING:
    from Servicios.Ast import AST


class IterativeAnalyzerService:
    """
    Servicio especializado en análisis de algoritmos iterativos.
    Genera pasos de resolución matemática y análisis estructural del AST.
    
    Soporta análisis de:
    - Peor caso (Big O): Cota superior asintótica
    - Mejor caso (Big Ω): Cota inferior asintótica
    - Caso promedio (Big Θ esperado): Usando análisis probabilístico
    """

    def __init__(self):
        pass

    def _sanitize_latex(self, tex: str) -> str:
        """Limpia la salida LaTeX de sympy para compatibilidad con KaTeX."""
        try:
            if not isinstance(tex, str):
                tex = str(tex)
            tex = tex.replace('\\left', '').replace('\\right', '')
            tex = ' '.join(tex.split())
            return tex
        except Exception:
            return str(tex)

    def generar_pasos_peor_caso(self, max_profundidad: int) -> List[Dict[str, str]]:
        """
        Genera los pasos de resolución matemática para el PEOR CASO.
        Usa sumatorias estándar del libro de Cormen.
        """
        if not sympy:
            return []
        
        steps = []
        
        if max_profundidad == 0:
            steps.append({
                'step': 1,
                'title': 'Identificación del algoritmo',
                'description': 'El algoritmo no contiene bucles iterativos.',
                'latex': 'T(n) = c_1',
                'explanation': 'Solo operaciones de tiempo constante.'
            })
            steps.append({
                'step': 2,
                'title': 'Resultado final',
                'description': 'Complejidad constante.',
                'latex': 'T(n) = \\Theta(1)',
                'explanation': 'El tiempo de ejecución no depende del tamaño de entrada.'
            })
            
        elif max_profundidad == 1:
            steps.append({
                'step': 1,
                'title': 'Identificación de la estructura',
                'description': 'El algoritmo contiene un bucle simple que itera n veces.',
                'latex': 'T(n) = c_1 + \\sum_{j=1}^{n} c_2',
                'explanation': 'El bucle externo se ejecuta n veces, cada iteración tiene costo c₂.'
            })
            steps.append({
                'step': 2,
                'title': 'Resolver la sumatoria',
                'description': 'Aplicamos la fórmula de suma de constantes.',
                'latex': '\\sum_{j=1}^{n} c_2 = c_2 \\cdot n',
                'explanation': 'La suma de una constante n veces es n por esa constante.'
            })
            steps.append({
                'step': 3,
                'title': 'Expresión simplificada',
                'description': 'Combinamos los términos.',
                'latex': 'T(n) = c_1 + c_2 \\cdot n',
                'explanation': 'Función lineal en n.'
            })
            steps.append({
                'step': 4,
                'title': 'Notación asintótica',
                'description': 'Identificamos el término dominante.',
                'latex': 'T(n) = \\Theta(n)',
                'explanation': 'El término c₂·n domina cuando n → ∞, por lo tanto es O(n).'
            })
            
        else:  # max_profundidad >= 2 (bucles anidados como Insertion Sort)
            steps.append({
                'step': 1,
                'title': 'Función de tiempo T(n) - Peor Caso',
                'description': 'Sumamos los costos de cada línea del algoritmo. En el peor caso (array en orden inverso), el bucle while se ejecuta j-1 veces para cada j.',
                'latex': 'T(n) = c_1 \\cdot n + c_2(n-1) + c_4(n-1) + c_3\\sum_{j=2}^{n} j + c_5\\sum_{j=2}^{n}(j-1) + c_6\\sum_{j=2}^{n}(j-1) + c_7(n-1)',
                'explanation': 'Cada línea contribuye: bucle for (c₁·n), asignaciones (c₂, c₄, c₇ ejecutadas n-1 veces), y el while con sus operaciones internas que dependen de j.'
            })
            steps.append({
                'step': 2,
                'title': 'Resolver sumatoria del while (iteraciones)',
                'description': 'Calculamos cuántas veces se ejecuta el bucle while en total.',
                'latex': '\\sum_{j=2}^{n} j = \\frac{n(n+1)}{2} - 1 = \\frac{n^2 + n - 2}{2}',
                'explanation': 'Usamos la fórmula de suma aritmética: Σj = n(n+1)/2, restamos 1 porque empezamos en j=2.'
            })
            steps.append({
                'step': 3,
                'title': 'Resolver sumatoria del cuerpo del while',
                'description': 'Las operaciones dentro del while se ejecutan (j-1) veces por cada j.',
                'latex': '\\sum_{j=2}^{n} (j-1) = \\sum_{k=1}^{n-1} k = \\frac{(n-1)n}{2} = \\frac{n^2 - n}{2}',
                'explanation': 'Sustitución k = j-1. Aplicamos fórmula de suma: Σk = (n-1)n/2.'
            })
            steps.append({
                'step': 4,
                'title': 'Sustituir las sumatorias resueltas',
                'description': 'Reemplazamos las sumatorias por sus valores calculados.',
                'latex': 'T(n) = c_1 n + c_2(n-1) + c_4(n-1) + c_3\\frac{n^2+n-2}{2} + (c_5+c_6)\\frac{n^2-n}{2} + c_7(n-1)',
                'explanation': 'Sustituimos los resultados de los pasos 2 y 3.'
            })
            steps.append({
                'step': 5,
                'title': 'Expandir y agrupar términos',
                'description': 'Expandimos los productos y agrupamos por potencias de n.',
                'latex': 'T(n) = \\left(\\frac{c_3}{2} + \\frac{c_5+c_6}{2}\\right)n^2 + \\left(c_1 + c_2 + c_4 + \\frac{c_3}{2} - \\frac{c_5+c_6}{2} + c_7\\right)n + (\\text{constantes})',
                'explanation': 'Reorganizamos para ver claramente los coeficientes de n², n y términos constantes.'
            })
            steps.append({
                'step': 6,
                'title': 'Forma general cuadrática',
                'description': 'Expresamos T(n) en forma polinomial.',
                'latex': 'T(n) = an^2 + bn + c',
                'explanation': 'Donde a, b, c son constantes positivas. Esta es una función cuadrática.'
            })
            steps.append({
                'step': 7,
                'title': 'Análisis asintótico',
                'description': 'Identificamos el término dominante cuando n → ∞.',
                'latex': '\\lim_{n \\to \\infty} \\frac{T(n)}{n^2} = \\lim_{n \\to \\infty} \\frac{an^2 + bn + c}{n^2} = a',
                'explanation': 'El coeficiente a es una constante positiva, confirmando que n² es el término dominante.'
            })
            steps.append({
                'step': 8,
                'title': 'Conclusión Peor Caso',
                'description': 'Determinamos la notación Big-O.',
                'latex': 'T(n) = \\Theta(n^2) \\implies O(n^2)',
                'explanation': 'En el peor caso, Insertion Sort tiene complejidad cuadrática O(n²).'
            })
        
        return steps

    def generar_pasos_caso_promedio(self, max_profundidad: int, hay_salida_temprana: bool) -> List[Dict[str, str]]:
        """
        Genera los pasos de resolución matemática para el CASO PROMEDIO.
        
        Basado en el Capítulo 5 de Cormen: Análisis Probabilístico
        Usa Variables Aleatorias Indicadoras para calcular E[T(n)].
        
        Supuesto fundamental: Todas las permutaciones de entrada son equiprobables (1/n!).
        """
        if not sympy:
            return []
        
        steps = []
        
        if max_profundidad == 0:
            steps.append({
                'step': 1,
                'title': 'Caso Promedio - Algoritmo sin bucles',
                'description': 'Sin bucles, todos los casos son idénticos.',
                'latex': 'E[T(n)] = \\Theta(1)',
                'explanation': 'El tiempo esperado es constante independiente de la entrada.'
            })
            
        elif max_profundidad == 1:
            if hay_salida_temprana:
                steps.append({
                    'step': 1,
                    'title': 'Definición del modelo probabilístico',
                    'description': 'Asumimos distribución uniforme: el elemento buscado puede estar en cualquier posición con probabilidad 1/n.',
                    'latex': 'Pr\\{\\text{elemento en posición } i\\} = \\frac{1}{n}, \\quad \\forall i \\in [1,n]',
                    'explanation': 'Este supuesto es fundamental para el análisis probabilístico (Cormen, Cap. 5.2).'
                })
                steps.append({
                    'step': 2,
                    'title': 'Variable aleatoria indicadora',
                    'description': 'Sea X_i = 1 si el bucle realiza i iteraciones antes de encontrar el elemento.',
                    'latex': 'X = \\sum_{i=1}^{n} i \\cdot Pr\\{\\text{encontrado en iteración } i\\} = \\sum_{i=1}^{n} \\frac{i}{n}',
                    'explanation': 'Definimos la variable X como el número esperado de iteraciones.'
                })
                steps.append({
                    'step': 3,
                    'title': 'Calcular E[X] - Serie aritmética',
                    'description': 'Aplicamos la fórmula de suma aritmética.',
                    'latex': 'E[X] = \\frac{1}{n} \\sum_{i=1}^{n} i = \\frac{1}{n} \\cdot \\frac{n(n+1)}{2} = \\frac{n+1}{2}',
                    'explanation': 'En promedio, encontramos el elemento en la posición (n+1)/2.'
                })
                steps.append({
                    'step': 4,
                    'title': 'Resultado final',
                    'description': 'El caso promedio es lineal pero con constante menor.',
                    'latex': 'E[T(n)] = \\Theta\\left(\\frac{n}{2}\\right) = \\Theta(n)',
                    'explanation': 'Aunque es Θ(n), en promedio revisamos la mitad de los elementos.'
                })
            else:
                steps.append({
                    'step': 1,
                    'title': 'Bucle sin salida temprana',
                    'description': 'El bucle siempre recorre todos los elementos.',
                    'latex': 'E[T(n)] = \\sum_{j=1}^{n} c = c \\cdot n = \\Theta(n)',
                    'explanation': 'Sin condición de salida, mejor, peor y promedio coinciden.'
                })
                
        else:  # Bucles anidados (ej. Insertion Sort)
            steps.append({
                'step': 1,
                'title': 'Modelo Probabilístico (Cormen, Cap. 5.2)',
                'description': 'Asumimos que la entrada es una permutación aleatoria uniforme. Cada una de las n! permutaciones tiene probabilidad 1/n!.',
                'latex': 'Pr\\{\\pi\\} = \\frac{1}{n!}, \\quad \\forall \\pi \\in S_n',
                'explanation': 'Este supuesto es la base del análisis de caso promedio (distribución uniforme sobre permutaciones).'
            })
            steps.append({
                'step': 2,
                'title': 'Variable Aleatoria Indicadora X_ij',
                'description': 'Definimos X_ij = 1 si la operación crítica ocurre en la j-ésima iteración del bucle externo en la i-ésima del interno.',
                'latex': 'X = \\sum_{j=2}^{n} \\sum_{i=1}^{j-1} X_{ij}, \\quad \\text{donde } E[X_{ij}] = Pr\\{X_{ij} = 1\\}',
                'explanation': 'Descomponemos el conteo total en eventos binarios (Lema de linealidad).'
            })
            steps.append({
                'step': 3,
                'title': 'Probabilidad de comparación en Insertion Sort',
                'description': 'Para cada j, el elemento A[j] debe compararse con ~j/2 elementos en promedio.',
                'latex': 'E[X_j] = \\frac{1}{j} \\sum_{k=1}^{j} k = \\frac{1}{j} \\cdot \\frac{j(j+1)}{2} \\cdot \\frac{1}{2} = \\frac{j}{4}',
                'explanation': 'En promedio, A[j] está en la posición media de los j primeros elementos ordenados.'
            })
            steps.append({
                'step': 4,
                'title': 'Sumatoria del caso promedio',
                'description': 'Sumamos las contribuciones esperadas de cada iteración.',
                'latex': 'E[T(n)] = \\sum_{j=2}^{n} \\frac{j-1}{2} = \\frac{1}{2} \\sum_{j=1}^{n-1} j = \\frac{(n-1)n}{4}',
                'explanation': 'En promedio, el bucle interno hace la mitad de iteraciones que en el peor caso.'
            })
            steps.append({
                'step': 5,
                'title': 'Simplificación algebraica',
                'description': 'Expandimos la expresión.',
                'latex': 'E[T(n)] = \\frac{n^2 - n}{4} = \\frac{n^2}{4} - \\frac{n}{4}',
                'explanation': 'Identificamos los términos cuadrático y lineal.'
            })
            steps.append({
                'step': 6,
                'title': 'Análisis asintótico',
                'description': 'Determinamos el orden de crecimiento.',
                'latex': 'E[T(n)] = \\Theta\\left(\\frac{n^2}{4}\\right) = \\Theta(n^2)',
                'explanation': 'Las constantes no afectan el orden asintótico.'
            })
            steps.append({
                'step': 7,
                'title': 'Conclusión Caso Promedio',
                'description': 'Aunque la constante es menor (n²/4 vs n²/2), la complejidad sigue siendo cuadrática.',
                'latex': 'E[T(n)] = \\Theta(n^2), \\quad \\text{pero con constante } \\frac{1}{4} \\text{ vs } \\frac{1}{2}',
                'explanation': 'El caso promedio es asintóticamente igual al peor caso, pero con factor constante menor (Cormen, Teorema 2.2).'
            })
        
        return steps

    def generar_pasos_mejor_caso(self, max_profundidad: int, hay_salida_temprana: bool) -> List[Dict[str, str]]:
        """
        Genera los pasos de resolución matemática para el MEJOR CASO.
        """
        if not sympy:
            return []
        
        steps = []
        
        if max_profundidad == 0:
            steps.append({
                'step': 1,
                'title': 'Mejor caso',
                'description': 'Sin bucles, el mejor y peor caso son iguales.',
                'latex': 'T(n) = \\Theta(1)',
                'explanation': 'Complejidad constante en todos los casos.'
            })
            
        elif max_profundidad == 1:
            if hay_salida_temprana:
                steps.append({
                    'step': 1,
                    'title': 'Mejor caso con salida temprana',
                    'description': 'El elemento buscado está al inicio o se cumple la condición inmediatamente.',
                    'latex': 'T(n) = c_1 + c_2 = \\Theta(1)',
                    'explanation': 'El bucle termina en la primera iteración.'
                })
            else:
                steps.append({
                    'step': 1,
                    'title': 'Mejor caso',
                    'description': 'El bucle debe recorrer todos los elementos.',
                    'latex': 'T(n) = \\Theta(n)',
                    'explanation': 'Igual al peor caso para un bucle simple sin salida temprana.'
                })
                
        else:  # Bucles anidados (Insertion Sort)
            steps.append({
                'step': 1,
                'title': 'Función de tiempo T(n) - Mejor Caso',
                'description': 'En el mejor caso, el array ya está ordenado. El bucle while nunca ejecuta su cuerpo porque A[i] ≤ key siempre.',
                'latex': 'T(n) = c_1 \\cdot n + c_2(n-1) + c_4(n-1) + c_3(n-1) + c_7(n-1)',
                'explanation': 'El test del while (c₃) se ejecuta 1 vez por iteración (solo verifica y sale), pero el cuerpo (c₅, c₆) no se ejecuta nunca.'
            })
            steps.append({
                'step': 2,
                'title': 'Simplificar la expresión',
                'description': 'Agrupamos los términos lineales.',
                'latex': 'T(n) = c_1 n + (c_2 + c_3 + c_4 + c_7)(n-1)',
                'explanation': 'Factorizamos (n-1) de los términos que se ejecutan n-1 veces.'
            })
            steps.append({
                'step': 3,
                'title': 'Expandir',
                'description': 'Distribuimos y combinamos.',
                'latex': 'T(n) = c_1 n + (c_2 + c_3 + c_4 + c_7)n - (c_2 + c_3 + c_4 + c_7)',
                'explanation': 'Expandimos el producto.'
            })
            steps.append({
                'step': 4,
                'title': 'Forma lineal',
                'description': 'Expresamos como función lineal.',
                'latex': 'T(n) = (c_1 + c_2 + c_3 + c_4 + c_7)n - (c_2 + c_3 + c_4 + c_7)',
                'explanation': 'T(n) = an + b, donde a y b son constantes.'
            })
            steps.append({
                'step': 5,
                'title': 'Análisis asintótico',
                'description': 'Identificamos el término dominante.',
                'latex': '\\lim_{n \\to \\infty} \\frac{T(n)}{n} = a > 0',
                'explanation': 'El término lineal domina, la constante se vuelve despreciable.'
            })
            steps.append({
                'step': 6,
                'title': 'Conclusión Mejor Caso',
                'description': 'Determinamos la notación Omega.',
                'latex': 'T(n) = \\Theta(n) \\implies \\Omega(n)',
                'explanation': 'En el mejor caso, Insertion Sort tiene complejidad lineal Ω(n).'
            })
        
        return steps

    def analizar_estructura_ast(self, ast_obj: 'AST') -> Dict[str, Any]:
        """
        Analiza la estructura del AST para determinar profundidad de bucles
        y condiciones de salida temprana.
        """
        max_profundidad = 0
        hay_salida_temprana = False
        
        def contar_profundidad(nodo, profundidad_actual=0):
            nonlocal max_profundidad, hay_salida_temprana
            
            if isinstance(nodo, (ast.For, ast.While)):
                profundidad_actual += 1
                if profundidad_actual > max_profundidad:
                    max_profundidad = profundidad_actual
            
            if isinstance(nodo, (ast.Break, ast.Return)):
                hay_salida_temprana = True
            
            for hijo in ast.iter_child_nodes(nodo):
                contar_profundidad(hijo, profundidad_actual)
        
        contar_profundidad(ast_obj._arbol)
        
        return {
            "max_profundidad": max_profundidad,
            "hay_salida_temprana": hay_salida_temprana
        }

    def determinar_complejidades(self, max_profundidad: int, hay_salida_temprana: bool) -> Dict[str, str]:
        """
        Determina las complejidades basadas en la estructura de bucles.
        Incluye caso promedio basado en análisis probabilístico.
        """
        if max_profundidad == 0:
            orden_peor_str = "1"
            orden_mejor_str = "1"
            orden_promedio_str = "1"
        elif max_profundidad == 1:
            orden_peor_str = "n"
            orden_mejor_str = "n" if not hay_salida_temprana else "1"
            # Caso promedio para búsqueda lineal: n/2 → O(n)
            orden_promedio_str = "n" if not hay_salida_temprana else "n/2"
        else:
            orden_peor_str = f"n^{max_profundidad}"
            orden_mejor_str = "n" if hay_salida_temprana or max_profundidad >= 2 else f"n^{max_profundidad}"
            # Caso promedio: n²/4 para Insertion Sort → Θ(n²)
            orden_promedio_str = f"n^{max_profundidad}"

        notacion_o = f"O({orden_peor_str})"
        notacion_omega = f"Ω({orden_mejor_str})"
        
        # Theta solo aplica cuando mejor y peor caso coinciden
        if orden_peor_str == orden_mejor_str:
            notacion_theta = f"Θ({orden_peor_str})"
        else:
            notacion_theta = "No aplicable"
        
        # E[T(n)] - Caso promedio esperado
        notacion_promedio = f"E[T(n)] = Θ({orden_promedio_str})"

        return {
            "orden_peor_str": orden_peor_str,
            "orden_mejor_str": orden_mejor_str,
            "orden_promedio_str": orden_promedio_str,
            "notacion_o": notacion_o,
            "notacion_omega": notacion_omega,
            "notacion_theta": notacion_theta,
            "notacion_promedio": notacion_promedio
        }

    def generar_justificacion(self, max_profundidad: int, notacion_o: str, notacion_omega: str, notacion_promedio: str = None) -> str:
        """
        Genera justificación textual basada en la estructura del algoritmo.
        Incluye análisis de caso promedio basado en Cormen Cap. 5.
        """
        if max_profundidad == 0:
            return "El algoritmo no contiene bucles iterativos, por lo que su tiempo de ejecución es constante O(1). Mejor, peor y caso promedio son idénticos."
        elif max_profundidad == 1:
            base = f"El algoritmo contiene un bucle simple que itera sobre los elementos de entrada, resultando en complejidad lineal {notacion_o}."
            promedio = " En el caso promedio, asumiendo distribución uniforme, el elemento se encuentra en la posición n/2, pero asintóticamente sigue siendo Θ(n)."
            return base + promedio
        else:
            return (
                f"El algoritmo contiene bucles anidados con profundidad {max_profundidad}. "
                f"**Peor caso** (ej. array en orden inverso): el bucle interno se ejecuta O(n) veces "
                f"por cada iteración del bucle externo, resultando en {notacion_o}. "
                f"**Mejor caso** (ej. array ya ordenado): el bucle interno se ejecuta en tiempo constante por iteración, resultando en {notacion_omega}. "
                f"**Caso promedio** (Cormen, Cap. 5): Asumiendo que todas las permutaciones son equiprobables (1/n!), "
                f"el bucle interno hace aproximadamente (j-1)/2 iteraciones por cada j, "
                f"resultando en E[T(n)] = n²/4 = Θ(n²). La constante es menor pero el orden es el mismo que el peor caso."
            )

    def procesar_desglose_costos(self, raw_desglose: List) -> List[Dict[str, Any]]:
        """
        Procesa el desglose de costos para formato LaTeX.
        """
        line_costs = []
        for entry in raw_desglose:
            ln = None
            desc = ''
            cost_latex = ''
            if isinstance(entry, (list, tuple)) and len(entry) == 3:
                ln, cost_str, desc = entry
                cost_latex = self._sanitize_latex(cost_str) if isinstance(cost_str, str) else self._sanitize_latex(str(cost_str))
            elif isinstance(entry, (list, tuple)) and len(entry) == 4:
                ln, worst_expr, best_expr, desc = entry
                try:
                    worst_tex = self._sanitize_latex(sympy.latex(worst_expr)) if sympy else self._sanitize_latex(str(worst_expr))
                except Exception:
                    worst_tex = self._sanitize_latex(str(worst_expr))
                try:
                    best_tex = self._sanitize_latex(sympy.latex(best_expr)) if sympy else self._sanitize_latex(str(best_expr))
                except Exception:
                    best_tex = self._sanitize_latex(str(best_expr))
                if worst_tex == best_tex:
                    cost_latex = worst_tex
                else:
                    cost_latex = f"Peor: {worst_tex}, Mejor: {best_tex}"
            else:
                try:
                    ln = int(entry[0])
                except Exception:
                    ln = None
                desc = str(entry[-1]) if entry else ''
                cost_latex = str(entry[1]) if len(entry) > 1 else ''

            line_costs.append({
                'line': ln,
                'description': desc,
                'cost': cost_latex
            })
        
        return line_costs

    def formatear_funcion_latex(self, funcion) -> str:
        """
        Formatea una función T(n) a LaTeX.
        """
        try:
            return self._sanitize_latex(sympy.latex(funcion)) if sympy else self._sanitize_latex(str(funcion))
        except Exception:
            return self._sanitize_latex(str(funcion))
