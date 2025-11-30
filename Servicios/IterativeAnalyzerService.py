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

    def generar_pasos_caso_promedio(self, max_profundidad: int, hay_salida_temprana: bool, 
                                     tiene_comparacion_condicional: bool = True,
                                     tipo_algoritmo: str = "general") -> List[Dict[str, str]]:
        """
        Genera los pasos de resolución matemática para el CASO PROMEDIO.
        
        Basado en el Capítulo 5 de Cormen: Análisis Probabilístico
        Usa Variables Aleatorias Indicadoras para calcular E[T(n)].
        
        Metodología (Cormen Cap. 5):
        1. Definir distribución de entrada (permutaciones uniformes 1/n!)
        2. Identificar operación crítica (comparaciones, swaps, actualizaciones)
        3. Definir variable indicadora X_i para cada evento
        4. Calcular Pr{X_i = 1} usando combinatoria
        5. Aplicar E[X] = Σ E[X_i] (linealidad de esperanza)
        
        Supuesto fundamental: Todas las permutaciones de entrada son equiprobables (1/n!).
        """
        if not sympy:
            return []
        
        steps = []
        
        if max_profundidad == 0:
            # Sin bucles - tiempo constante
            steps.append({
                'step': 1,
                'title': 'Caso Promedio - Algoritmo sin bucles',
                'description': 'Sin bucles, todos los casos son idénticos.',
                'latex': 'E[T(n)] = \\Theta(1)',
                'explanation': 'El tiempo esperado es constante independiente de la entrada.'
            })
            
        elif max_profundidad == 1:
            # Un solo bucle
            if hay_salida_temprana:
                steps.extend(self._pasos_promedio_busqueda_lineal())
            else:
                steps.extend(self._pasos_promedio_bucle_simple())
                
        else:
            # Bucles anidados (profundidad >= 2)
            # Análisis genérico usando variables indicadoras
            steps.extend(self._pasos_promedio_bucles_anidados(max_profundidad, tiene_comparacion_condicional))
        
        return steps
    
    def _pasos_promedio_busqueda_lineal(self) -> List[Dict[str, str]]:
        """Pasos para búsqueda lineal con salida temprana."""
        return [
            {
                'step': 1,
                'title': 'Definición del modelo probabilístico (Cormen, Cap. 5.2)',
                'description': 'Asumimos distribución uniforme: el elemento buscado puede estar en cualquier posición con probabilidad 1/n.',
                'latex': 'Pr\\{\\text{elemento en posición } i\\} = \\frac{1}{n}, \\quad \\forall i \\in [1,n]',
                'explanation': 'Este supuesto es fundamental para el análisis probabilístico.'
            },
            {
                'step': 2,
                'title': 'Variable aleatoria X = número de iteraciones',
                'description': 'Sea X la variable que cuenta iteraciones hasta encontrar el elemento.',
                'latex': 'E[X] = \\sum_{i=1}^{n} i \\cdot Pr\\{\\text{encontrado en posición } i\\} = \\sum_{i=1}^{n} \\frac{i}{n}',
                'explanation': 'Aplicamos la definición de esperanza.'
            },
            {
                'step': 3,
                'title': 'Calcular E[X] - Serie aritmética',
                'description': 'Aplicamos la fórmula de suma aritmética Σi = n(n+1)/2.',
                'latex': 'E[X] = \\frac{1}{n} \\cdot \\frac{n(n+1)}{2} = \\frac{n+1}{2}',
                'explanation': 'En promedio, encontramos el elemento en la posición (n+1)/2.'
            },
            {
                'step': 4,
                'title': 'Resultado final',
                'description': 'El caso promedio es lineal.',
                'latex': 'E[T(n)] = \\Theta\\left(\\frac{n+1}{2}\\right) = \\Theta(n)',
                'explanation': 'Aunque revisamos ~n/2 elementos en promedio, sigue siendo Θ(n).'
            }
        ]
    
    def _pasos_promedio_bucle_simple(self) -> List[Dict[str, str]]:
        """Pasos para bucle simple sin salida temprana."""
        return [
            {
                'step': 1,
                'title': 'Bucle sin salida temprana',
                'description': 'El bucle siempre recorre todos los n elementos.',
                'latex': 'T(n) = \\sum_{i=1}^{n} c = c \\cdot n',
                'explanation': 'Sin condición de salida, el bucle siempre ejecuta n iteraciones.'
            },
            {
                'step': 2,
                'title': 'Caso promedio = Peor caso = Mejor caso',
                'description': 'No hay variabilidad en el número de operaciones.',
                'latex': 'E[T(n)] = T_{\\text{peor}}(n) = T_{\\text{mejor}}(n) = \\Theta(n)',
                'explanation': 'Sin condiciones internas que dependan de la entrada, todos los casos coinciden.'
            }
        ]
    
    def _pasos_promedio_bucles_anidados(self, profundidad: int, tiene_if: bool) -> List[Dict[str, str]]:
        """
        Pasos genéricos para algoritmos con bucles anidados.
        Aplica la metodología de variables indicadoras de Cormen Cap. 5.
        """
        steps = []
        
        # Paso 1: Definir distribución
        steps.append({
            'step': 1,
            'title': 'Paso 1: Definir la Distribución de Entrada (Cormen, Cap. 5.2)',
            'description': 'Asumimos que la entrada es una permutación aleatoria uniforme. Cada una de las n! permutaciones tiene probabilidad 1/n!.',
            'latex': 'Pr\\{\\pi\\} = \\frac{1}{n!}, \\quad \\forall \\pi \\in S_n \\text{ (grupo simétrico)}',
            'explanation': 'Sin esta definición, el "caso promedio" no existe matemáticamente. Es el supuesto estándar para algoritmos de ordenamiento.'
        })
        
        # Paso 2: Identificar operación crítica
        if tiene_if:
            steps.append({
                'step': 2,
                'title': 'Paso 2: Aislar la Variable Aleatoria X',
                'description': 'Identificamos la operación crítica que se ejecuta condicionalmente (comparación, swap, actualización).',
                'latex': 'X = \\text{número total de veces que se ejecuta la operación crítica}',
                'explanation': 'No medimos "tiempo" abstracto, sino una cantidad discreta y contable.'
            })
        else:
            steps.append({
                'step': 2,
                'title': 'Paso 2: Sin operaciones condicionales',
                'description': 'El algoritmo no tiene operaciones que dependan de la entrada.',
                'latex': 'X = n \\cdot (n-1) / 2 \\text{ (fijo)}',
                'explanation': 'Todos los casos son idénticos.'
            })
        
        # Paso 3: Variables indicadoras
        steps.append({
            'step': 3,
            'title': 'Paso 3: Atomizar con Variables Indicadoras X_ij',
            'description': 'Definimos X_ij = 1 si la operación ocurre en la iteración (i,j), 0 si no.',
            'latex': 'X = \\sum_{i} \\sum_{j} X_{ij}, \\quad \\text{donde } X_{ij} \\in \\{0, 1\\}',
            'explanation': 'Descomponemos el conteo total en eventos binarios simples (Cormen, Lema 5.1).'
        })
        
        # Paso 4: Calcular probabilidad
        if tiene_if:
            steps.append({
                'step': 4,
                'title': 'Paso 4: Calcular Pr{X_ij = 1}',
                'description': 'Para cada par (i,j), calculamos la probabilidad de que la condición se cumpla.',
                'latex': 'E[X_{ij}] = Pr\\{X_{ij} = 1\\} = \\frac{1}{2}',
                'explanation': 'Bajo permutaciones uniformes, la probabilidad de que A[i] > A[j] (o cualquier comparación) es 1/2 por simetría.'
            })
        else:
            steps.append({
                'step': 4,
                'title': 'Paso 4: Probabilidad constante',
                'description': 'Sin condiciones, la operación siempre ocurre.',
                'latex': 'Pr\\{X_{ij} = 1\\} = 1',
                'explanation': 'La operación se ejecuta en cada iteración.'
            })
        
        # Paso 5: Linealidad de la esperanza
        steps.append({
            'step': 5,
            'title': 'Paso 5: Aplicar Linealidad de la Esperanza',
            'description': 'E[X] = Σ E[X_ij] incluso si las variables NO son independientes.',
            'latex': 'E[X] = E\\left[\\sum_{i,j} X_{ij}\\right] = \\sum_{i,j} E[X_{ij}] = \\sum_{i,j} Pr\\{X_{ij}=1\\}',
            'explanation': 'Esta es la propiedad más poderosa: la linealidad aplica SIEMPRE (Cormen, Teorema 5.2).'
        })
        
        # Paso 6: Resolver sumatoria
        if tiene_if:
            steps.append({
                'step': 6,
                'title': 'Paso 6: Resolver la Sumatoria',
                'description': f'Con {profundidad} bucles anidados, hay O(n^{profundidad}) pares. Con probabilidad 1/2 cada uno:',
                'latex': f'E[X] = \\frac{{1}}{{2}} \\cdot \\binom{{n}}{{2}} = \\frac{{1}}{{2}} \\cdot \\frac{{n(n-1)}}{{2}} = \\frac{{n^2 - n}}{{4}}',
                'explanation': 'En promedio, la operación crítica ocurre en la mitad de las iteraciones posibles.'
            })
        else:
            steps.append({
                'step': 6,
                'title': 'Paso 6: Resolver la Sumatoria',
                'description': f'Con {profundidad} bucles anidados y sin condiciones:',
                'latex': f'E[X] = \\binom{{n}}{{2}} = \\frac{{n(n-1)}}{{2}} = \\frac{{n^2 - n}}{{2}}',
                'explanation': 'La operación se ejecuta en cada par posible.'
            })
        
        # Paso 7: Conclusión
        orden = f"n^{profundidad}" if profundidad > 1 else "n"
        factor_promedio = "1/4" if tiene_if else "1/2"
        factor_peor = "1/2" if tiene_if else "1/2"
        
        steps.append({
            'step': 7,
            'title': 'Paso 7: Conclusión del Caso Promedio',
            'description': f'El caso promedio tiene el mismo orden asintótico que el peor caso.',
            'latex': f'E[T(n)] = \\Theta\\left(\\frac{{{orden}}}{{{factor_promedio.split("/")[1] if "/" in factor_promedio else "1"}}}\\right) = \\Theta({orden})',
            'explanation': f'Aunque el factor constante es menor ({factor_promedio} vs {factor_peor}), el orden asintótico O({orden}) se mantiene.'
        })
        
        # Paso 8: Resumen
        steps.append({
            'step': 8,
            'title': 'Resumen Metodológico',
            'description': 'Lista de chequeo completada según Cormen Cap. 5:',
            'latex': '\\boxed{E[T(n)] = \\Theta(' + orden + ')}',
            'explanation': '✓ Distribución definida (1/n!) ✓ Variable aislada ✓ Indicadoras ✓ Probabilidad local ✓ Linealidad aplicada'
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
        Analiza la estructura del AST para determinar:
        - Profundidad de bucles anidados
        - Condiciones de salida temprana (break/return)
        - Presencia de comparaciones condicionales (if dentro de bucles)
        
        Esto permite aplicar el análisis probabilístico correcto.
        """
        max_profundidad = 0
        hay_salida_temprana = False
        tiene_comparacion_condicional = False
        if_dentro_bucle = False
        
        def contar_profundidad(nodo, profundidad_actual=0, dentro_bucle=False):
            nonlocal max_profundidad, hay_salida_temprana, tiene_comparacion_condicional, if_dentro_bucle
            
            es_bucle = isinstance(nodo, (ast.For, ast.While))
            
            if es_bucle:
                profundidad_actual += 1
                if profundidad_actual > max_profundidad:
                    max_profundidad = profundidad_actual
                dentro_bucle = True
            
            if isinstance(nodo, (ast.Break, ast.Return)):
                hay_salida_temprana = True
            
            # Detectar if dentro de bucles (operación condicional)
            if isinstance(nodo, ast.If) and dentro_bucle:
                if_dentro_bucle = True
                tiene_comparacion_condicional = True
            
            # Detectar comparaciones en condiciones (A[i] < A[j], etc.)
            if isinstance(nodo, ast.Compare) and dentro_bucle:
                tiene_comparacion_condicional = True
            
            for hijo in ast.iter_child_nodes(nodo):
                contar_profundidad(hijo, profundidad_actual, dentro_bucle)
        
        contar_profundidad(ast_obj._arbol)
        
        return {
            "max_profundidad": max_profundidad,
            "hay_salida_temprana": hay_salida_temprana,
            "tiene_comparacion_condicional": tiene_comparacion_condicional,
            "if_dentro_bucle": if_dentro_bucle
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
