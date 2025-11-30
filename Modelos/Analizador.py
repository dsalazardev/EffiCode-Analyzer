"""
Orquestador principal de análisis de complejidad.
Delega el análisis a servicios especializados según el tipo de algoritmo.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Any

from .Algoritmo import Algoritmo
from .Complejidad import Complejidad
from Servicios.EfficiencyVisitor import EfficiencyVisitor
from Servicios.IterativeAnalyzerService import IterativeAnalyzerService
from Servicios.RecursiveAnalyzerService import RecursiveAnalyzerService

try:
    import sympy
except ImportError:
    sympy = None


if TYPE_CHECKING:
    from .Reporte import Reporte
    from .Parser import Parser
    from Servicios.LLMService import LLMService
    from .Usuario import Usuario
    from Servicios.Ast import AST


class Analizador:
    """
    Orquesta el análisis de complejidad a partir del AST generado por el parser.
    Soporta tanto algoritmos iterativos como recursivos, delegando a servicios especializados.
    """

    def __init__(self, id: int, parser: 'Parser', llm_service: 'LLMService'):
        self._id = id
        self._parser = parser
        self._llm_service = llm_service
        self._algoritmos: List[Algoritmo] = []
        self._reporte: 'Reporte' | None = None
        self._complejidad: Complejidad | None = None
        self._usuario: 'Usuario' | None = None
        self._ultimo_analisis: Dict[str, Any] = {}
        
        # Servicios especializados
        self._iterative_service = IterativeAnalyzerService()
        self._recursive_service = RecursiveAnalyzerService(llm_service)

    @property
    def id(self) -> int:
        return self._id

    @property
    def parser(self) -> 'Parser':
        return self._parser

    @parser.setter
    def parser(self, value: 'Parser'):
        self._parser = value

    @property
    def llm_service(self) -> 'LLMService':
        return self._llm_service

    @llm_service.setter
    def llm_service(self, value: 'LLMService'):
        self._llm_service = value
        self._recursive_service.llm_service = value

    def addAlgoritmo(self, algoritmo: Algoritmo):
        self._algoritmos.append(algoritmo)

    def removeAlgoritmo(self, algoritmo: Algoritmo):
        self._algoritmos.remove(algoritmo)

    def _analizar_eficiencia(self, ast_obj: 'AST') -> Dict[str, Any]:
        """Analiza la eficiencia usando el EfficiencyVisitor."""
        visitor = EfficiencyVisitor()
        visitor.visit(ast_obj._arbol)
        return {
            "desglose_costos": visitor.line_costs,
            "funcion_peor_caso": visitor.worst_case_cost,
            "funcion_mejor_caso": visitor.best_case_cost,
            "funcion_peor_caso_str": str(visitor.worst_case_cost),
            "funcion_mejor_caso_str": str(visitor.best_case_cost)
        }

    def analizar(self, algoritmo: Algoritmo) -> Complejidad:
        """
        Analiza algoritmos ITERATIVOS con resolución paso a paso.
        Delega la lógica al servicio especializado IterativeAnalyzerService.
        """
        if not algoritmo.arbol_sintactico:
            raise ValueError("El algoritmo no tiene un AST. Ejecute el parser primero.")

        # Análisis de eficiencia (visitor)
        self._ultimo_analisis = self._analizar_eficiencia(algoritmo.arbol_sintactico)
        
        # Análisis estructural del AST
        estructura = self._iterative_service.analizar_estructura_ast(algoritmo.arbol_sintactico)
        self._ultimo_analisis.update(estructura)

        t_n_peor = self._ultimo_analisis.get("funcion_peor_caso")
        t_n_mejor = self._ultimo_analisis.get("funcion_mejor_caso")
        max_profundidad = estructura.get("max_profundidad", 0)
        hay_salida_temprana = estructura.get("hay_salida_temprana", False)

        # Determinar complejidades usando el servicio (ahora incluye caso promedio)
        complejidades = self._iterative_service.determinar_complejidades(max_profundidad, hay_salida_temprana)
        notacion_o = complejidades["notacion_o"]
        notacion_omega = complejidades["notacion_omega"]
        notacion_theta = complejidades["notacion_theta"]
        notacion_promedio = complejidades["notacion_promedio"]
        orden_peor_str = complejidades["orden_peor_str"]
        orden_mejor_str = complejidades["orden_mejor_str"]
        orden_promedio_str = complejidades["orden_promedio_str"]

        # Generar pasos de resolución matemática (peor, mejor Y promedio)
        pasos_peor_caso = self._iterative_service.generar_pasos_peor_caso(max_profundidad)
        pasos_mejor_caso = self._iterative_service.generar_pasos_mejor_caso(max_profundidad, hay_salida_temprana)
        pasos_caso_promedio = self._iterative_service.generar_pasos_caso_promedio(max_profundidad, hay_salida_temprana)

        # Procesar desglose de costos para LaTeX
        raw_desglose = self._ultimo_analisis.get('desglose_costos', [])
        line_costs = self._iterative_service.procesar_desglose_costos(raw_desglose)

        # Generar LaTeX para las funciones T(n)
        worst_case_func_str = self._iterative_service.formatear_funcion_latex(t_n_peor)
        best_case_func_str = self._iterative_service.formatear_funcion_latex(t_n_mejor)

        # Generar justificación basada en la estructura (ahora incluye caso promedio)
        justificacion = self._iterative_service.generar_justificacion(
            max_profundidad, notacion_o, notacion_omega, notacion_promedio
        )

        justification_data = {
            'worst_case_function': worst_case_func_str,
            'best_case_function': best_case_func_str,
            'line_costs': line_costs,
            'resolution_steps': {
                'worst_case': pasos_peor_caso,
                'best_case': pasos_mejor_caso,
                'average_case': pasos_caso_promedio  # NUEVO: pasos del caso promedio
            },
            'conclusion': {
                'worst_case': {'dominant_term': orden_peor_str, 'complexity': notacion_o},
                'best_case': {'dominant_term': orden_mejor_str, 'complexity': notacion_omega},
                'average_case': {
                    'complexity': notacion_promedio,
                    'dominant_term': orden_promedio_str,
                    'description': (
                        f"Usando análisis probabilístico (Cormen Cap. 5): "
                        f"Asumiendo distribución uniforme de entradas, "
                        f"el tiempo esperado es {notacion_promedio}."
                    )
                }
            }
        }

        complejidad = Complejidad(
            self._id,
            notacion_o,
            notacion_omega,
            notacion_theta,
            justificacion,
            justification_data
        )

        complejidad.analizador = self
        self._complejidad = complejidad
        return complejidad

    def analizar_recursivo(self, algoritmo: Algoritmo) -> Complejidad:
        """
        Analiza algoritmos RECURSIVOS usando LLM para resolver ecuaciones de recurrencia.
        Delega la lógica al servicio especializado RecursiveAnalyzerService.
        Incluye análisis de caso promedio basado en Cormen Cap. 5 y 7.
        """
        if not algoritmo.arbol_sintactico:
            raise ValueError("El algoritmo no tiene un AST. Ejecute el parser primero.")
            
        if not self._recursive_service.detectar_recursividad(algoritmo.arbol_sintactico):
            raise ValueError("El algoritmo no parece ser recursivo. Use 'analizar' para iterativos.")

        # 1. Generar ecuación de recurrencia
        analisis_recurrencia = self._recursive_service.generar_ecuacion_recurrencia(algoritmo.arbol_sintactico)
        
        # 2. Usar LLM para resolver la ecuación (ahora incluye caso promedio)
        solucion_llm = self._recursive_service.resolver_recurrencia_con_llm(
            analisis_recurrencia["ecuacion"],
            analisis_recurrencia["patron"],
            algoritmo.codigo_fuente
        )
        
        # 3. Generar pasos del caso promedio para algoritmos recursivos
        pasos_caso_promedio = self._recursive_service.generar_pasos_caso_promedio_recursivo(
            analisis_recurrencia["patron"]
        )
        
        # 4. Generar justificación combinada (incluye caso promedio)
        justificacion = self._recursive_service.generar_justificacion_combinada(analisis_recurrencia, solucion_llm)
        
        # 5. Extraer información de caso promedio
        caso_promedio = solucion_llm.get('caso_promedio', {})
        
        # 6. Construir justification_data con caso promedio
        justification_data = {
            'recurrence_equation': analisis_recurrencia['ecuacion'],
            'recursion_type': analisis_recurrencia['patron']['tipo'],
            'resolution_steps': {
                'worst_case': [],  # Los pasos se incluyen en la justificación textual
                'best_case': [],
                'average_case': pasos_caso_promedio
            },
            'conclusion': {
                'worst_case': {
                    'dominant_term': solucion_llm.get('notacion_o', 'O(n)').replace('O(', '').replace(')', ''),
                    'complexity': solucion_llm.get('notacion_o', 'O(n)')
                },
                'best_case': {
                    'dominant_term': solucion_llm.get('notacion_omega', 'Ω(1)').replace('Ω(', '').replace(')', ''),
                    'complexity': solucion_llm.get('notacion_omega', 'Ω(1)')
                },
                'average_case': {
                    'complexity': caso_promedio.get('notacion', solucion_llm.get('notacion_theta', 'Θ(n)')),
                    'dominant_term': caso_promedio.get('notacion', 'n').replace('E[T(n)] = Θ(', '').replace(')', ''),
                    'description': (
                        f"Distribución asumida: {caso_promedio.get('distribucion_asumida', 'N/A')}. "
                        f"Factor constante: {caso_promedio.get('constante_factor', 'N/A')}"
                    )
                }
            },
            'method_used': solucion_llm.get('metodo_utilizado', 'Análisis de Recurrencias'),
            'references': solucion_llm.get('referencias', 'Cormen et al.')
        }
        
        # 7. Crear objeto Complejidad con justification_data
        complejidad = Complejidad(
            id=algoritmo.id,
            notacion_o=solucion_llm.get('notacion_o', 'O(n)'),
            notacion_omega=solucion_llm.get('notacion_omega', 'Ω(1)'),
            notacion_theta=solucion_llm.get('notacion_theta', 'Θ(n)'),
            justificacion=justificacion,
            justification_data=justification_data
        )

        complejidad.analizador = self
        self._complejidad = complejidad
        return complejidad

    def es_recursivo(self, algoritmo: Algoritmo) -> bool:
        """
        Detecta si un algoritmo es recursivo.
        """
        if not algoritmo.arbol_sintactico:
            return False
        return self._recursive_service.detectar_recursividad(algoritmo.arbol_sintactico)

    def analizar_auto(self, algoritmo: Algoritmo) -> Complejidad:
        """
        Detecta automáticamente el tipo de algoritmo y aplica el análisis correspondiente.
        """
        if self.es_recursivo(algoritmo):
            return self.analizar_recursivo(algoritmo)
        else:
            return self.analizar(algoritmo)
