"""
Servicio para análisis de complejidad de algoritmos RECURSIVOS.
Detecta patrones de recursión y genera ecuaciones de recurrencia.

Basado en "Introduction to Algorithms" (Cormen et al.):
- Capítulo 4: Divide y Vencerás, Recurrencias
- Capítulo 7: Quicksort (análisis de caso promedio con variables indicadoras)
- Capítulo 5: Análisis Probabilístico
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, List
import ast
import json

# Importar el solver de recurrencias matemáticas
from Servicios.RecurrenceSolver import RecurrenceSolver

if TYPE_CHECKING:
    from Servicios.Ast import AST
    from Servicios.LLMService import LLMService


class RecursiveAnalyzerService:
    """
    Servicio especializado en análisis de algoritmos recursivos.
    Detecta patrones de recursión, genera ecuaciones de recurrencia
    y utiliza LLM para resolver las ecuaciones.
    
    Soporta análisis de caso promedio para:
    - Quicksort (Θ(n lg n) promedio vs Θ(n²) peor caso)
    - Algoritmos divide y vencerás con pivote aleatorio
    - Recurrencias con división aleatoria
    
    NUEVO: Integra RecurrenceSolver para resolver matemáticamente
    cualquier ecuación de recurrencia usando 7 métodos de Cormen.
    
    OPTIMIZACIÓN: Cache interno para evitar recálculos costosos.
    """

    def __init__(self, llm_service: 'LLMService' = None):
        self._llm_service = llm_service
        # Inicializar el solver matemático de recurrencias
        self._recurrence_solver = RecurrenceSolver()
        # Cache para resultados de análisis (evita recálculos)
        self._cache_analisis: Dict[str, Dict[str, Any]] = {}
        self._cache_ecuaciones: Dict[str, Dict[str, Any]] = {}

    @property
    def llm_service(self) -> 'LLMService':
        return self._llm_service

    @llm_service.setter
    def llm_service(self, value: 'LLMService'):
        self._llm_service = value

    def detectar_recursividad(self, ast_obj: 'AST') -> bool:
        """
        Detecta si la función principal realiza una llamada recursiva a sí misma.
        """
        funciones_definidas = ast_obj.extraer_funciones()
        if not funciones_definidas:
            return False

        nombre_funcion_principal = funciones_definidas[0]
        llamadas = ast_obj.extraer_llamadas()
        
        return nombre_funcion_principal in llamadas

    def detectar_patron_recursivo(self, ast_obj: 'AST') -> Dict[str, Any]:
        """
        Detecta el patrón recursivo específico del algoritmo.
        """
        funciones_definidas = ast_obj.extraer_funciones()
        nombre_funcion_principal = funciones_definidas[0] if funciones_definidas else ""
        
        parametros_recursion = self._analizar_parametros_recursivos(ast_obj, nombre_funcion_principal)
        tipo_recursion = self._clasificar_tipo_recursion(ast_obj, nombre_funcion_principal)
        division_info = self._analizar_division_problema(ast_obj, nombre_funcion_principal)
        
        return {
            "tipo": tipo_recursion,
            "parametros": parametros_recursion,
            "division": division_info,
            "nombre_funcion": nombre_funcion_principal
        }

    def _analizar_parametros_recursivos(self, ast_obj: 'AST', nombre_funcion: str) -> Dict[str, Any]:
        """
        Analiza cómo cambian los parámetros en las llamadas recursivas.
        """
        llamadas_recursivas = []
        
        for node in ast.walk(ast_obj._arbol):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == nombre_funcion:
                    args_analysis = []
                    for arg in node.args:
                        if isinstance(arg, ast.BinOp):
                            args_analysis.append(self._analizar_expresion_recursiva(arg))
                        elif isinstance(arg, ast.Constant):
                            args_analysis.append({"tipo": "constante", "valor": arg.value})
                        else:
                            args_analysis.append({"tipo": "variable", "expresion": ast.unparse(arg)})
                    
                    llamadas_recursivas.append({
                        "nodo": node,
                        "argumentos": args_analysis,
                        "linea": node.lineno
                    })
        
        return {
            "llamadas": llamadas_recursivas,
            "total_llamadas": len(llamadas_recursivas)
        }

    def _analizar_expresion_recursiva(self, node: ast.BinOp) -> Dict[str, Any]:
        """
        Analiza expresiones binarias en argumentos recursivos (n-1, n//2, etc.)
        """
        if isinstance(node, ast.BinOp):
            izquierda = ast.unparse(node.left) if hasattr(node, 'left') else "?"
            derecha = ast.unparse(node.right) if hasattr(node, 'right') else "?"
            operador = type(node.op).__name__
            
            op_map = {
                'Sub': '-',
                'Add': '+',
                'Mult': '*',
                'Div': '/',
                'FloorDiv': '//'
            }
            
            return {
                "tipo": "operacion_binaria",
                "expresion": f"{izquierda}{op_map.get(operador, operador)}{derecha}",
                "operador": operador,
                "operandos": [izquierda, derecha]
            }
        
        return {"tipo": "desconocido", "expresion": ast.unparse(node)}

    def _clasificar_tipo_recursion(self, ast_obj: 'AST', nombre_funcion: str) -> str:
        """
        Clasifica el tipo de recursión: lineal, binaria, múltiple, etc.
        
        IMPORTANTE: Detecta patrones especiales como exponenciación rápida
        donde hay múltiples caminos pero cada uno tiene máximo 1 llamada.
        """
        llamadas_recursivas = []
        for node in ast.walk(ast_obj._arbol):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == nombre_funcion:
                    llamadas_recursivas.append(node)
        
        if not llamadas_recursivas:
            return "no_recursiva"
        
        llamadas_por_camino = self._contar_llamadas_por_camino(ast_obj, nombre_funcion)
        max_llamadas_en_camino = max(llamadas_por_camino.values()) if llamadas_por_camino else 0
        
        # NUEVO: Detectar patrón de exponenciación rápida (repeated squaring)
        # Característica: múltiples caminos, cada uno con max 1 llamada,
        # y uno de los caminos usa n/2 o n//2
        if max_llamadas_en_camino == 1 and len(llamadas_por_camino) > 1:
            if self._es_patron_exponenciacion_rapida(ast_obj, nombre_funcion):
                return "recursion_logaritmica"  # NUEVO tipo
            # NUEVO: Detectar búsqueda binaria y similares
            # Ramas mutuamente excluyentes que dividen el espacio de búsqueda
            if self._es_patron_busqueda_binaria(ast_obj, nombre_funcion):
                return "recursion_logaritmica"
        
        if max_llamadas_en_camino == 2:
            if self._es_patron_fibonacci(ast_obj, nombre_funcion):
                return "recursion_exponencial_fibonacci"
            else:
                return "recursion_binaria"
        
        elif max_llamadas_en_camino == 1:
            if len(llamadas_por_camino) > 1:
                return "recursion_multiple"
            else:
                return "recursion_lineal"
        
        elif max_llamadas_en_camino > 2:
            return "recursion_multiple_compleja"
        
        return "recursion_general"

    def _es_patron_exponenciacion_rapida(self, ast_obj: 'AST', nombre_funcion: str) -> bool:
        """
        Detecta el patrón de exponenciación rápida (repeated squaring):
        - Al menos un camino con división por 2 (n/2, n//2, n div 2)
        - Otro camino con decremento (n-1)
        - Cada camino tiene máximo 1 llamada recursiva
        
        Este patrón tiene complejidad O(log n) porque aunque hay un camino
        con n-1, siempre es seguido por un camino con n/2.
        
        Ejemplos: POWER, exponenciación modular, multiplicación rusa
        """
        tiene_division_mitad = False
        tiene_decremento = False
        
        for node in ast.walk(ast_obj._arbol):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == nombre_funcion:
                    for arg in node.args:
                        arg_str = ast.unparse(arg).lower().replace(" ", "")
                        
                        # Detectar n/2, n//2, n div 2
                        if "//2" in arg_str or "/2" in arg_str or "div2" in arg_str:
                            tiene_division_mitad = True
                        # Detectar n-1
                        elif "-1" in arg_str and ("n-1" in arg_str or arg_str.endswith("-1")):
                            tiene_decremento = True
        
        # Es exponenciación rápida si tiene ambos patrones
        return tiene_division_mitad and tiene_decremento

    def _es_patron_busqueda_binaria(self, ast_obj: 'AST', nombre_funcion: str) -> bool:
        """
        Detecta el patrón de búsqueda binaria y algoritmos similares:
        - Múltiples ramas mutuamente excluyentes (if/else)
        - Cada rama tiene máximo 1 llamada recursiva
        - Los argumentos usan patrones como mid-1, mid+1, low, high
        - O reducen el rango de búsqueda a aproximadamente la mitad
        
        Características clave:
        - Calcula un punto medio (mid, middle, pivot)
        - Las llamadas usan variantes de ese punto medio
        
        Este patrón tiene complejidad O(log n) porque cada llamada
        reduce el espacio de búsqueda a la mitad.
        
        Ejemplos: BINARY-SEARCH, búsqueda en BST, búsqueda ternaria
        """
        tiene_calculo_mid = False
        usa_mid_en_llamadas = False
        
        # Buscar si hay un cálculo de punto medio
        for node in ast.walk(ast_obj._arbol):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        nombre_var = target.id.lower()
                        if any(x in nombre_var for x in ['mid', 'middle', 'pivot', 'centro']):
                            tiene_calculo_mid = True
                            break
        
        # Buscar si las llamadas recursivas usan mid+1, mid-1, o similares
        patrones_division_rango = ['mid', 'middle', 'pivot', '+1', '-1', 'low', 'high']
        llamadas_con_division = 0
        total_llamadas = 0
        
        for node in ast.walk(ast_obj._arbol):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == nombre_funcion:
                    total_llamadas += 1
                    args_str = ' '.join(ast.unparse(arg).lower() for arg in node.args)
                    
                    # Verificar si usa patrones de división de rango
                    if any(patron in args_str for patron in patrones_division_rango):
                        llamadas_con_division += 1
        
        usa_mid_en_llamadas = llamadas_con_division >= 1 and total_llamadas >= 2
        
        # Es búsqueda binaria si tiene mid Y las llamadas dividen el rango
        # O si todas las llamadas usan patrones de división de rango
        return (tiene_calculo_mid and usa_mid_en_llamadas) or (llamadas_con_division == total_llamadas and total_llamadas >= 2)

    def _es_patron_fibonacci(self, ast_obj: 'AST', nombre_funcion: str) -> bool:
        """
        Detecta si el algoritmo sigue el patrón Fibonacci: F(n) = F(n-1) + F(n-2)
        """
        llamadas_n_minus_1 = 0
        llamadas_n_minus_2 = 0
        
        for node in ast.walk(ast_obj._arbol):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == nombre_funcion:
                    for arg in node.args:
                        arg_str = ast.unparse(arg).replace(" ", "")
                        if "n-1" in arg_str or "-1" in arg_str:
                            llamadas_n_minus_1 += 1
                        elif "n-2" in arg_str or "-2" in arg_str:
                            llamadas_n_minus_2 += 1
        
        return llamadas_n_minus_1 >= 1 and llamadas_n_minus_2 >= 1

    def _contar_llamadas_por_camino(self, ast_obj: 'AST', nombre_funcion: str) -> Dict[str, int]:
        """
        Cuenta las llamadas recursivas en cada camino de ejecución (if/else branches).
        """
        contador = {}
        
        def contar_en_nodo(nodo, camino_actual="main"):
            if isinstance(nodo, list):
                for elemento in nodo:
                    contar_en_nodo(elemento, camino_actual)
                return
            
            if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name):
                if nodo.func.id == nombre_funcion:
                    contador[camino_actual] = contador.get(camino_actual, 0) + 1
            
            if isinstance(nodo, ast.If):
                contar_en_nodo(nodo.body, f"{camino_actual}_if")
                if nodo.orelse:
                    contar_en_nodo(nodo.orelse, f"{camino_actual}_else")
            else:
                for nombre_campo, valor in ast.iter_fields(nodo):
                    if isinstance(valor, (ast.AST, list)):
                        contar_en_nodo(valor, camino_actual)
        
        funcion_def = next((n for n in ast.walk(ast_obj._arbol) if isinstance(n, ast.FunctionDef)), None)
        if funcion_def:
            contar_en_nodo(funcion_def.body)
        
        return contador

    def _analizar_division_problema(self, ast_obj: 'AST', nombre_funcion: str) -> Dict[str, Any]:
        """
        Analiza cómo se divide el problema en subproblemas.
        """
        patrones = {
            "mitad": ["//2", "/2", ">>1", "mid", "middle"],
            "tercio": ["//3", "/3"],
            "n_minus_1": ["-1", "n-1", "size-1"],
            "n_minus_k": ["-", "sub", "minus"]
        }
        
        division_detectada = "desconocida"
        factor_division = 2
        
        for node in ast.walk(ast_obj._arbol):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == nombre_funcion:
                    for arg in node.args:
                        arg_str = ast.unparse(arg).lower()
                        
                        if any(patron in arg_str for patron in patrones["mitad"]):
                            division_detectada = "mitad"
                            factor_division = 2
                        elif any(patron in arg_str for patron in patrones["tercio"]):
                            division_detectada = "tercio"
                            factor_division = 3
                        elif any(patron in arg_str for patron in patrones["n_minus_1"]):
                            division_detectada = "n_minus_1"
                            factor_division = 1
                        elif any(patron in arg_str for patron in patrones["n_minus_k"]):
                            division_detectada = "n_minus_k"
                            factor_division = "variable"
        
        return {
            "tipo": division_detectada,
            "factor": factor_division
        }

    def resolver_recurrencia_matematica(self, ast_obj: 'AST') -> Dict[str, Any]:
        """
        Resuelve la ecuación de recurrencia usando métodos matemáticos rigurosos.
        
        Este método integra el RecurrenceSolver que implementa los 7 métodos
        de Cormen para resolver recurrencias:
        
        1. Teorema Maestro (Cap. 4.5): T(n) = aT(n/b) + f(n)
        2. Teorema Akra-Bazzi: Generalización para subproblemas desiguales
        3. Método de Sustitución (Cap. 4.3): Adivinar y demostrar por inducción
        4. Árbol de Recursión (Cap. 4.4): Visualización y suma de costos
        5. Método de Iteración: Expansión directa de la recurrencia
        6. Cambio de Variables (Cap. 4.6): Para recurrencias no algebraicas
        7. Funciones Generadoras (Apéndice A): Para recurrencias lineales
        
        Args:
            ast_obj: Árbol sintáctico abstracto del algoritmo
            
        Returns:
            Dict con la solución completa incluyendo:
            - complexity: Complejidad asintótica final
            - method_used: Método de solución utilizado
            - solution_steps: Pasos detallados de la resolución
            - all_results: Resultados de todos los métodos aplicables
        """
        # 1. Detectar el patrón recursivo
        patron_recursivo = self.detectar_patron_recursivo(ast_obj)
        
        # 2. Generar la ecuación de recurrencia
        ecuacion_info = self.generar_ecuacion_recurrencia(ast_obj)
        
        # 3. Verificar cache antes de resolver
        cache_key = f"{ecuacion_info['a']}_{ecuacion_info['b']}_{ecuacion_info['f_n']}_{ecuacion_info.get('tipo_especial')}"
        if cache_key in self._cache_analisis:
            return self._cache_analisis[cache_key]
        
        # 4. Resolver usando el solver matemático
        resultado_solver = self._recurrence_solver.solve(
            a=ecuacion_info['a'],
            b=ecuacion_info['b'],
            f_n=ecuacion_info['f_n'],
            recurrence_type=ecuacion_info.get('tipo_especial')
        )
        
        # 5. Combinar con información del patrón
        resultado = {
            "ecuacion": ecuacion_info['ecuacion'],
            "patron_detectado": patron_recursivo,
            "parametros_recurrencia": {
                "a": ecuacion_info['a'],
                "b": ecuacion_info['b'],
                "f_n": ecuacion_info['f_n'],
                "tipo_especial": ecuacion_info.get('tipo_especial')
            },
            "solucion_matematica": resultado_solver,
            "complejidad_final": resultado_solver.get('complexity', 'No determinada'),
            "metodo_solucion": resultado_solver.get('method_used', 'Análisis general'),
            "pasos_resolucion": resultado_solver.get('solution_steps', []),
            "todos_resultados": resultado_solver.get('all_results', {}),
            "justificacion": self._generar_justificacion_completa(
                ecuacion_info, patron_recursivo, resultado_solver
            )
        }
        
        # 6. Guardar en cache
        self._cache_analisis[cache_key] = resultado
        return resultado
    
    def _generar_justificacion_completa(
        self, 
        ecuacion_info: Dict[str, Any], 
        patron: Dict[str, Any], 
        solucion: Dict[str, Any]
    ) -> str:
        """
        Genera una justificación matemática completa de la solución.
        """
        tipo_recursion = patron.get('tipo', 'desconocido').replace('_', ' ').title()
        ecuacion = ecuacion_info.get('ecuacion', 'T(n) = ?')
        metodo = solucion.get('method_used', 'Análisis general')
        complejidad = solucion.get('complexity', 'No determinada')
        
        justificacion = f"""
        ══════════════════════════════════════════════════════════════════
                        ANÁLISIS DE RECURRENCIA MATEMÁTICO
                    (Basado en Cormen et al., 4ª edición)
        ══════════════════════════════════════════════════════════════════

        TIPO DE RECURSIÓN DETECTADA: {tipo_recursion}

        ECUACIÓN DE RECURRENCIA:
        {ecuacion}

        Donde:
        • a = {ecuacion_info['a']} (número de subproblemas)
        • b = {ecuacion_info['b']} (factor de división)
        • f(n) = O({ecuacion_info['f_n']}) (trabajo no recursivo)

        MÉTODO DE SOLUCIÓN: {metodo}

        COMPLEJIDAD FINAL: {complejidad}
        """
        
        # Agregar pasos de resolución si existen
        pasos = solucion.get('solution_steps', [])
        if pasos:
            justificacion += "\n📝 PASOS DE RESOLUCIÓN:\n"
            for i, paso in enumerate(pasos, 1):
                if isinstance(paso, dict):
                    titulo = paso.get('title', f'Paso {i}')
                    desc = paso.get('description', '')
                    latex = paso.get('latex', '')
                    justificacion += f"\n   {i}. {titulo}\n"
                    if desc:
                        justificacion += f"      {desc}\n"
                    if latex:
                        justificacion += f"      → {latex}\n"
                else:
                    justificacion += f"\n   {i}. {paso}\n"
        
        # Agregar referencias a Cormen
        justificacion += f"""
        ══════════════════════════════════════════════════════════════════
        📚 REFERENCIAS:
        • Introduction to Algorithms, Cormen et al., 4ª edición
        • Capítulo 4: Divide y Vencerás
        • Secciones 4.3-4.6: Métodos de Resolución de Recurrencias
        ══════════════════════════════════════════════════════════════════
        """
        
        return justificacion

    def generar_ecuacion_recurrencia(self, ast_obj: 'AST') -> Dict[str, Any]:
        """
        Genera la ecuación de recurrencia basada en el análisis estructural.
        
        Detecta correctamente:
        - Recursión lineal: T(n) = T(n-1) + f(n) -> Θ(n) o Θ(n²)
        - Fibonacci: T(n) = T(n-1) + T(n-2) + f(n) -> Θ(φ^n)
        - Hanoi: T(n) = 2T(n-1) + f(n) -> Θ(2^n)
        - Divide y vencerás: T(n) = aT(n/b) + f(n) -> depende de caso
        - Exponenciación rápida: T(n) = T(n/2) + O(1) -> Θ(log n)
        """
        patron_recursivo = self.detectar_patron_recursivo(ast_obj)
        division_info = patron_recursivo["division"]
        
        a = 0
        b = 2
        f_n = "1"
        tipo_especial = None
        
        # Primero: detectar tipo de división (n-1, n/2, etc.)
        es_division_lineal = division_info["tipo"] in ["n_minus_1", "n_minus_k"]
        
        # NUEVO: Manejo especial para exponenciación rápida (repeated squaring)
        if patron_recursivo["tipo"] == "recursion_logaritmica":
            # Exponenciación rápida: aunque hay un camino con n-1,
            # el comportamiento dominante es T(n) = T(n/2) + O(1) -> Θ(log n)
            a = 1
            b = 2
            tipo_especial = "logaritmica"
            f_n = "1"
        
        elif patron_recursivo["tipo"] == "recursion_lineal":
            # Una sola llamada recursiva con decremento
            a = 1
            b = 1
            tipo_especial = "n_minus_1"
            
        elif patron_recursivo["tipo"] == "recursion_exponencial_fibonacci":
            # Fibonacci: T(n-1) + T(n-2)
            a = 2
            b = 1
            tipo_especial = "fibonacci"
            f_n = "1"
            
        elif patron_recursivo["tipo"] == "recursion_binaria":
            a = 2
            # IMPORTANTE: Si la división es n-k (no n/b), es tipo Hanoi
            if es_division_lineal:
                b = 1  # Indicador de decremento lineal
                tipo_especial = "n_minus_1"  # Pero con a=2, el solver sabe que es exponencial
            else:
                # Divide y vencerás clásico: MergeSort, etc.
                if division_info["tipo"] == "mitad":
                    b = 2
                elif division_info["tipo"] == "tercio":
                    b = 3
                else:
                    b = 2
            
        elif patron_recursivo["tipo"] == "recursion_multiple":
            a = patron_recursivo["parametros"]["total_llamadas"]
            if es_division_lineal:
                b = 1
                tipo_especial = "n_minus_1"
            
        else:
            a = patron_recursivo["parametros"]["total_llamadas"]
        
        # Para divide y vencerás (no lineal), detectar el factor de división
        if not es_division_lineal and patron_recursivo["tipo"] not in ["recursion_lineal", "recursion_exponencial_fibonacci", "recursion_logaritmica"]:
            if division_info["tipo"] == "mitad":
                b = 2
            elif division_info["tipo"] == "tercio":
                b = 3
            elif division_info["tipo"] == "n_minus_1":
                b = 1
                tipo_especial = "n_minus_1"
            else:
                b = 2
        
        f_n = self._detectar_costo_no_recursivo(ast_obj, patron_recursivo["tipo"])
        
        # Generar ecuación según el tipo
        if tipo_especial == "logaritmica":
            # Exponenciación rápida: dominado por división a la mitad
            ecuacion = f"T(n) = T(n/2) + O({f_n})"
        elif tipo_especial == "fibonacci":
            ecuacion = f"T(n) = T(n-1) + T(n-2) + O({f_n})"
        elif tipo_especial == "n_minus_1":
            if a > 1:
                # Hanoi y similares: T(n) = aT(n-1) + f(n) -> Θ(a^n)
                ecuacion = f"T(n) = {a}T(n-1) + O({f_n})"
            else:
                # Factorial y similares: T(n) = T(n-1) + f(n) -> Θ(n) o Θ(n²)
                ecuacion = f"T(n) = T(n-1) + O({f_n})"
        else:
            # Divide y vencerás: T(n) = aT(n/b) + f(n)
            ecuacion = f"T(n) = {a}T(n/{b}) + O({f_n})"
        
        return {
            "ecuacion": ecuacion,
            "a": a,
            "b": b,
            "f_n": f_n,
            "tipo_especial": tipo_especial,
            "patron": patron_recursivo
        }

    def _detectar_costo_no_recursivo(self, ast_obj: 'AST', tipo_recursion: str) -> str:
        """
        Detecta el costo del trabajo no recursivo.
        """
        if tipo_recursion == "recursion_binaria":
            if self._buscar_evidencia_operacion_lineal(ast_obj):
                return "n"
            else:
                return "1"
        
        analisis_estructural = self._analizar_estructura_ast(ast_obj)
        profundidad = analisis_estructural["max_profundidad"]
        
        if profundidad > 1:
            return f"n^{profundidad}"
        elif profundidad == 1:
            return "n"
        else:
            return "1"

    def _analizar_estructura_ast(self, ast_obj: 'AST') -> Dict[str, Any]:
        """
        Analiza la estructura del AST para determinar profundidad de bucles.
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

    def generar_pasos_caso_promedio_recursivo(self, patron: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Genera los pasos de resolución para el CASO PROMEDIO de algoritmos recursivos.
        
        Basado en Cormen Cap. 7.4.2 (Quicksort) y Cap. 5 (Análisis Probabilístico).
        Usa variables aleatorias indicadoras para contar comparaciones esperadas.
        """
        tipo = patron.get("tipo", "recursion_general")
        steps = []
        
        if tipo == "recursion_binaria":
            # Análisis estilo Quicksort (Cormen 7.4.2)
            steps.append({
                'step': 1,
                'title': 'Modelo Probabilístico (Cormen, Cap. 7.4)',
                'description': 'Asumimos que el pivote se elige aleatoriamente o que la entrada es una permutación aleatoria uniforme.',
                'latex': 'Pr\\{\\text{pivote en posición } q\\} = \\frac{1}{n}, \\quad \\forall q \\in [0, n-1]',
                'explanation': 'Esta es la base del análisis aleatorizado de Quicksort.'
            })
            steps.append({
                'step': 2,
                'title': 'Variable Indicadora X_ij',
                'description': 'Sea z₁,...,zₙ los elementos ordenados. X_ij = 1 si zᵢ se compara con zⱼ.',
                'latex': 'X = \\sum_{i=1}^{n-1} \\sum_{j=i+1}^{n} X_{ij}',
                'explanation': 'Contamos comparaciones usando indicadoras (Cormen, Sección 7.4.2).'
            })
            steps.append({
                'step': 3,
                'title': 'Probabilidad de comparación',
                'description': 'zᵢ y zⱼ se comparan solo si uno es elegido como pivote antes que cualquier elemento entre ellos.',
                'latex': 'Pr\\{z_i \\text{ comparado con } z_j\\} = \\frac{2}{j - i + 1}',
                'explanation': 'De los j-i+1 elementos en {zᵢ,...,zⱼ}, solo zᵢ o zⱼ causan la comparación.'
            })
            steps.append({
                'step': 4,
                'title': 'Esperanza por linealidad',
                'description': 'Aplicamos linealidad de la esperanza: E[X] = ΣE[X_ij].',
                'latex': 'E[X] = \\sum_{i=1}^{n-1} \\sum_{j=i+1}^{n} \\frac{2}{j-i+1} = \\sum_{i=1}^{n-1} \\sum_{k=1}^{n-i} \\frac{2}{k+1}',
                'explanation': 'Sustituimos k = j - i para simplificar la sumatoria.'
            })
            steps.append({
                'step': 5,
                'title': 'Simplificación con serie armónica',
                'description': 'La suma interna está acotada por la serie armónica.',
                'latex': 'E[X] < \\sum_{i=1}^{n-1} \\sum_{k=1}^{n} \\frac{2}{k} = 2(n-1) \\cdot H_n \\approx 2(n-1)\\ln n',
                'explanation': 'H_n = Σ(1/k) ≈ ln(n) + γ (constante de Euler-Mascheroni).'
            })
            steps.append({
                'step': 6,
                'title': 'Conclusión Caso Promedio',
                'description': 'El número esperado de comparaciones es O(n lg n).',
                'latex': 'E[T(n)] = \\Theta(n \\lg n)',
                'explanation': 'A pesar de que el peor caso es Θ(n²), el caso promedio es Θ(n lg n).'
            })
            
        elif tipo == "recursion_exponencial_fibonacci":
            steps.append({
                'step': 1,
                'title': 'Caso Promedio = Peor Caso para Fibonacci',
                'description': 'En Fibonacci recursivo, no hay aleatorización posible.',
                'latex': 'T(n) = T(n-1) + T(n-2) + \\Theta(1)',
                'explanation': 'La estructura del problema es determinista.'
            })
            steps.append({
                'step': 2,
                'title': 'Todos los casos son idénticos',
                'description': 'El árbol de recursión siempre tiene la misma forma para un n dado.',
                'latex': 'E[T(n)] = T_{\\text{peor}}(n) = T_{\\text{mejor}}(n) = \\Theta(\\phi^n)',
                'explanation': 'No hay variabilidad en la entrada que afecte el tiempo de ejecución.'
            })
            
        elif tipo == "recursion_lineal":
            steps.append({
                'step': 1,
                'title': 'Recursión lineal T(n-1)',
                'description': 'El algoritmo reduce el problema en 1 unidad por cada llamada.',
                'latex': 'T(n) = T(n-1) + O(f(n))',
                'explanation': 'Ejemplos: factorial, suma de lista, búsqueda lineal recursiva.'
            })
            steps.append({
                'step': 2,
                'title': 'Caso promedio con trabajo constante',
                'description': 'Si f(n) = O(1), el tiempo esperado es lineal.',
                'latex': 'E[T(n)] = \\sum_{i=1}^{n} O(1) = \\Theta(n)',
                'explanation': 'Cada nivel de recursión contribuye trabajo constante.'
            })
            steps.append({
                'step': 3,
                'title': 'Conclusión',
                'description': 'Para recursión lineal, todos los casos son típicamente iguales.',
                'latex': 'E[T(n)] = O(T(n)) = \\Omega(T(n)) = \\Theta(n)',
                'explanation': 'No hay aleatorización en la estructura de la recursión.'
            })
            
        else:
            steps.append({
                'step': 1,
                'title': 'Análisis de recurrencia general',
                'description': 'Para determinar el caso promedio, debemos identificar la fuente de aleatoriedad.',
                'latex': 'E[T(n)] = \\frac{1}{n}\\sum_{q=0}^{n-1} (T(q) + T(n-q-1)) + \\Theta(f(n))',
                'explanation': 'Esta es la recurrencia "promediada" cuando la división es aleatoria.'
            })
            steps.append({
                'step': 2,
                'title': 'Método de análisis',
                'description': 'Usar el método de sustitución o generación de funciones.',
                'latex': '\\text{Se requiere análisis específico según el patrón}',
                'explanation': 'Consulte Cormen, Capítulo 4 para técnicas de resolución.'
            })
        
        return steps

    def _buscar_evidencia_operacion_lineal(self, ast_obj: 'AST') -> bool:
        """
        Busca evidencia de operaciones O(n) como 'merge'.
        """
        codigo_completo = ast.unparse(ast_obj._arbol).lower()
        
        palabras_clave_lineales = ["merge", "combine", "fusion", "join", "concatenate"]
        if any(palabra in codigo_completo for palabra in palabras_clave_lineales):
            return True
        
        for node in ast.walk(ast_obj._arbol):
            if isinstance(node, ast.For):
                return True
        
        return False

    def resolver_recurrencia_con_llm(self, ecuacion: str, patron: Dict[str, Any], pseudocodigo: str) -> Dict[str, Any]:
        """
        Usa LLM para resolver la ecuación de recurrencia de manera precisa.
        Incluye análisis de caso promedio usando variables indicadoras.
        """
        if not self._llm_service:
            return self.resolver_recurrencia_local(ecuacion, patron)
        
        prompt = f"""
            Eres un experto en análisis de algoritmos del libro "Introduction to Algorithms" (Cormen et al.).

            **Pseudocódigo a analizar:**
            ```pseudocode
            {pseudocodigo}
            ```

            Patrón detectado automáticamente:
            - Tipo de recursión: {patron['tipo']}
            - División del problema: {patron['division']['tipo']}
            - Factor de división: {patron['division']['factor']}

            Ecuación de recurrencia generada:
            {ecuacion}

            Instrucciones:
            1. Resuelve la ecuación de recurrencia usando los métodos apropiados (Teorema Maestro, sustitución, árbol de recursión)
            2. Proporciona las cotas asintóticas EXACTAS para:
            - **Peor caso (O)**: cota superior
            - **Mejor caso (Ω)**: cota inferior  
            - **Caso promedio (E[T(n)])**: usando análisis probabilístico con variables aleatorias indicadoras
            3. Para el CASO PROMEDIO (Capítulo 5 y 7 de Cormen):
            - Define la distribución de probabilidad asumida (ej. permutaciones uniformes)
            - Usa variables indicadoras X_ij para contar operaciones
            - Aplica E[X] = Σ E[X_i] (linealidad de la esperanza)
            4. Incluye referencias específicas a "Introduction to Algorithms" (capítulo, sección)
            5. Para Quicksort, el caso promedio es Θ(n lg n) aunque el peor sea Θ(n²)

            Formato de respuesta JSON:
            {{
                "notacion_o": "O(...)",
                "notacion_omega": "Ω(...)",
                "notacion_theta": "Θ(...)",
                "caso_promedio": {{
                    "notacion": "E[T(n)] = Θ(...)",
                    "distribucion_asumida": "Descripción de la distribución probabilística",
                    "constante_factor": "Factor constante si aplica (ej. n²/4 vs n²/2)"
                }},
                "justificacion_matematica": "Explicación detallada incluyendo caso promedio...",
                "referencias": "Capítulo X, Sección Y",
                "metodo_utilizado": "Teorema Maestro/Método de Sustitución/Variables Indicadoras"
            }}

            Responde ÚNICAMENTE con el JSON válido, sin texto adicional.
            """
            
        try:
            respuesta = self._llm_service.analizar_complejidad(prompt)
            respuesta_limpia = self._limpiar_respuesta_json(respuesta)
            return json.loads(respuesta_limpia)
        except Exception as e:
            print(f"Error al resolver recurrencia con LLM: {e}")
            return self.resolver_recurrencia_local(ecuacion, patron)

    def _limpiar_respuesta_json(self, respuesta: str) -> str:
        """
        Limpia la respuesta del LLM para extraer solo el JSON.
        """
        inicio = respuesta.find('{')
        fin = respuesta.rfind('}') + 1

        if inicio != -1 and fin != -1:
            return respuesta[inicio:fin]

        return respuesta.strip()

    def resolver_recurrencia_local(self, ecuacion: str, patron: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback: Resuelve la recurrencia con lógica local cuando el LLM falla.
        Incluye análisis de caso promedio basado en Cormen.
        """
        tipo_recursion = patron["tipo"]

        if tipo_recursion == "recursion_exponencial_fibonacci":
            return {
                "notacion_o": "O(2^n)",
                "notacion_omega": "Ω(φ^n)",
                "notacion_theta": "Θ(φ^n)",
                "caso_promedio": {
                    "notacion": "E[T(n)] = Θ(φ^n)",
                    "distribucion_asumida": "No aplica - estructura determinista",
                    "constante_factor": "Mismo para todos los casos"
                },
                "justificacion_matematica": "Ecuación de Fibonacci: T(n) = T(n-1) + T(n-2) + O(1). Solución exacta: Θ(φ^n) donde φ ≈ 1.618. **Caso promedio**: No hay aleatorización posible; el árbol de recursión es idéntico para cada n.",
                "referencias": "Capítulo 27, Sección 27.1",
                "metodo_utilizado": "Ecuación Característica"
            }
        elif tipo_recursion == "recursion_binaria":
            return {
                "notacion_o": "O(n²)",  # Peor caso (pivote siempre mínimo/máximo)
                "notacion_omega": "Ω(n log n)",  # Mejor caso (división perfecta)
                "notacion_theta": "Θ(n log n)",  # Caso promedio
                "caso_promedio": {
                    "notacion": "E[T(n)] = Θ(n lg n)",
                    "distribucion_asumida": "Permutaciones uniformes (cada permutación tiene probabilidad 1/n!)",
                    "constante_factor": "≈ 1.39n lg n comparaciones esperadas"
                },
                "justificacion_matematica": (
                    "**Análisis de Quicksort (Cormen 7.4.2):**\n"
                    "- Peor caso: O(n²) cuando el pivote siempre es el mínimo/máximo\n"
                    "- Mejor caso: Ω(n lg n) con división perfecta T(n) = 2T(n/2) + Θ(n)\n"
                    "- **Caso promedio**: Usando variables indicadoras X_ij:\n"
                    "  E[comparaciones] = Σᵢ Σⱼ₌ᵢ₊₁ 2/(j-i+1) ≈ 2n ln n = Θ(n lg n)\n"
                    "  El factor constante es ≈1.39 (vs 1.0 en Mergesort)"
                ),
                "referencias": "Capítulo 7, Sección 7.4.2 (Análisis con Variables Indicadoras)",
                "metodo_utilizado": "Variables Aleatorias Indicadoras + Linealidad de Esperanza"
            }
        elif tipo_recursion == "recursion_lineal":
            return {
                "notacion_o": "O(n)",
                "notacion_omega": "Ω(n)",
                "notacion_theta": "Θ(n)", 
                "caso_promedio": {
                    "notacion": "E[T(n)] = Θ(n)",
                    "distribucion_asumida": "No aplica - recursión determinista",
                    "constante_factor": "Mismo para todos los casos"
                },
                "justificacion_matematica": "T(n) = T(n-1) + O(1). Expansión: T(n) = T(0) + n*c = Θ(n). **Caso promedio**: La estructura de recursión lineal es determinista; todos los casos coinciden.",
                "referencias": "Capítulo 4, Sección 4.3",
                "metodo_utilizado": "Método de Sustitución"
            }
        else:
            return {
                "notacion_o": "O(n)",
                "notacion_omega": "Ω(1)", 
                "notacion_theta": "Complejidad variable",
                "caso_promedio": {
                    "notacion": "Requiere análisis específico",
                    "distribucion_asumida": "Depende del algoritmo",
                    "constante_factor": "N/A"
                },
                "justificacion_matematica": f"Análisis de recurrencia: {ecuacion}. Se requiere análisis específico para determinar cotas exactas y caso promedio.",
                "referencias": "Capítulo 4 y 5",
                "metodo_utilizado": "Análisis General"
            }

    def generar_justificacion_combinada(self, analisis_recurrencia: Dict[str, Any], solucion_llm: Dict[str, Any]) -> str:
        """
        Genera la justificación combinada para el análisis recursivo.
        Incluye análisis de caso promedio basado en Cormen Cap. 5 y 7.
        """
        caso_promedio = solucion_llm.get('caso_promedio', {})
        
        base = (
            f"**ANÁLISIS DE ALGORITMO RECURSIVO**\n\n"
            f"**Tipo de Recursión Detectada:** {analisis_recurrencia['patron']['tipo'].replace('_', ' ').title()}\n"
            f"**Ecuación de Recurrencia:** {analisis_recurrencia['ecuacion']}\n"
            f"**Método de Análisis:** {solucion_llm.get('metodo_utilizado', 'Análisis Matemático')}\n\n"
            f"**Análisis Estructural Automático:**\n"
            f"- Subproblemas (a): {analisis_recurrencia['a']}\n"
            f"- Factor de división (b): {analisis_recurrencia['b']}\n"
            f"- Trabajo no recursivo: O({analisis_recurrencia['f_n']})\n\n"
        )
        
        caso_promedio_str = ""
        if caso_promedio:
            caso_promedio_str = (
                f"**ANÁLISIS DE CASO PROMEDIO (Cormen, Cap. 5 y 7):**\n"
                f"- Complejidad esperada: {caso_promedio.get('notacion', 'N/A')}\n"
                f"- Distribución asumida: {caso_promedio.get('distribucion_asumida', 'N/A')}\n"
                f"- Factor constante: {caso_promedio.get('constante_factor', 'N/A')}\n\n"
            )
        
        justificacion_mat = solucion_llm.get('justificacion_matematica', 
                                              solucion_llm.get('justificacion', 'Análisis de recurrencia'))
        referencias = solucion_llm.get('referencias', 'Cormen et al.')
        
        return (
            base +
            caso_promedio_str +
            f"**Resolución Matemática:**\n{justificacion_mat}\n\n"
            f"**Referencia:** {referencias} - Introduction to Algorithms"
        )
