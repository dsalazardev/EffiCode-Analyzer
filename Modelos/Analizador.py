"""
Orquestador principal de análisis de complejidad.
Delega el análisis a servicios especializados según el tipo de algoritmo.
Incluye clasificador neural como validación adicional.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Any, Optional, Tuple

from .Algoritmo import Algoritmo
from .Complejidad import Complejidad
from Servicios.EfficiencyVisitor import EfficiencyVisitor
from Servicios.IterativeAnalyzerService import IterativeAnalyzerService
from Servicios.RecursiveAnalyzerService import RecursiveAnalyzerService

# Importar clasificador neural (opcional)
try:
    from Servicios.NeuralClassifier import NeuralComplexityClassifier
    NEURAL_AVAILABLE = True
except ImportError:
    NEURAL_AVAILABLE = False
    NeuralComplexityClassifier = None

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
    Incluye clasificador neural para validación y predicción alternativa.
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
        
        # Clasificador neural (carga perezosa)
        self._neural_classifier: Optional[NeuralComplexityClassifier] = None
        self._neural_loaded = False

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
        
        # Análisis estructural del AST (detecta bucles, condiciones, etc.)
        estructura = self._iterative_service.analizar_estructura_ast(algoritmo.arbol_sintactico)
        self._ultimo_analisis.update(estructura)

        t_n_peor = self._ultimo_analisis.get("funcion_peor_caso")
        t_n_mejor = self._ultimo_analisis.get("funcion_mejor_caso")
        max_profundidad = estructura.get("max_profundidad", 0)
        hay_salida_temprana = estructura.get("hay_salida_temprana", False)
        tiene_comparacion_condicional = estructura.get("tiene_comparacion_condicional", True)

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
        # Caso promedio ahora recibe si hay comparaciones condicionales
        pasos_caso_promedio = self._iterative_service.generar_pasos_caso_promedio(
            max_profundidad, 
            hay_salida_temprana,
            tiene_comparacion_condicional
        )

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
        Analiza algoritmos RECURSIVOS usando múltiples métodos:
        
        1. RecurrenceSolver: Resuelve matemáticamente usando 7 métodos de Cormen:
           - Teorema Maestro
           - Akra-Bazzi
           - Sustitución
           - Árbol de recursión
           - Iteración
           - Cambio de variables
           - Funciones generatrices
           
        2. LLM (si disponible): Para análisis de caso promedio y validación
        
        Incluye análisis de caso promedio basado en Cormen Cap. 5 y 7.
        """
        if not algoritmo.arbol_sintactico:
            raise ValueError("El algoritmo no tiene un AST. Ejecute el parser primero.")
            
        if not self._recursive_service.detectar_recursividad(algoritmo.arbol_sintactico):
            raise ValueError("El algoritmo no parece ser recursivo. Use 'analizar' para iterativos.")

        # 1. Generar ecuación de recurrencia
        analisis_recurrencia = self._recursive_service.generar_ecuacion_recurrencia(algoritmo.arbol_sintactico)
        
        # 2. NUEVO: Resolver matemáticamente usando RecurrenceSolver (7 métodos de Cormen)
        solucion_matematica = self._recursive_service.resolver_recurrencia_matematica(algoritmo.arbol_sintactico)
        
        # 3. Usar LLM para análisis adicional (caso promedio detallado, si disponible)
        solucion_llm = self._recursive_service.resolver_recurrencia_con_llm(
            analisis_recurrencia["ecuacion"],
            analisis_recurrencia["patron"],
            algoritmo.codigo_fuente
        )
        
        # 4. Combinar resultados: priorizar solución matemática, enriquecer con LLM
        if solucion_matematica.get('complejidad_final') and solucion_matematica['complejidad_final'] != 'No determinada':
            # Usar la solución matemática como base
            complejidad_final = solucion_matematica['complejidad_final']
            metodo_resolucion = solucion_matematica['metodo_solucion']
            pasos_resolucion = solucion_matematica['pasos_resolucion']
            
            # Actualizar solucion_llm con los valores matemáticos
            solucion_llm['notacion_theta'] = complejidad_final
            solucion_llm['metodo_utilizado'] = f"RecurrenceSolver ({metodo_resolucion})"
            solucion_llm['pasos_resolucion_matematica'] = pasos_resolucion
        
        # 5. Generar pasos del caso promedio para algoritmos recursivos
        pasos_caso_promedio = self._recursive_service.generar_pasos_caso_promedio_recursivo(
            analisis_recurrencia["patron"]
        )
        
        # 6. Generar justificación combinada (incluye caso promedio)
        justificacion = self._recursive_service.generar_justificacion_combinada(analisis_recurrencia, solucion_llm)
        
        # Si hay solución matemática, agregar sus detalles a la justificación
        if solucion_matematica.get('justificacion'):
            justificacion = solucion_matematica['justificacion'] + "\n\n" + justificacion
        
        # 7. Extraer información de caso promedio
        caso_promedio = solucion_llm.get('caso_promedio', {})
        
        # 8. Construir justification_data con caso promedio y solución matemática
        justification_data = {
            'recurrence_equation': analisis_recurrencia['ecuacion'],
            'recursion_type': analisis_recurrencia['patron']['tipo'],
            'mathematical_solution': {
                'complexity': solucion_matematica.get('complejidad_final', 'No determinada'),
                'method': solucion_matematica.get('metodo_solucion', 'N/A'),
                'steps': solucion_matematica.get('pasos_resolucion', [])
            },
            'resolution_steps': {
                'worst_case': solucion_matematica.get('pasos_resolucion', []),
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
        
        # 9. Crear objeto Complejidad con justification_data
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

    # =========================================================================
    # CLASIFICADOR NEURAL - Neural Algorithmix
    # =========================================================================
    
    def _cargar_clasificador_neural(self) -> bool:
        """
        Carga el clasificador neural de forma perezosa.
        
        Returns:
            True si se cargó exitosamente, False en caso contrario
        """
        if self._neural_loaded:
            return self._neural_classifier is not None
        
        self._neural_loaded = True
        
        if not NEURAL_AVAILABLE:
            print("Warning: NeuralClassifier not available (numpy not installed)")
            return False
        
        try:
            self._neural_classifier = NeuralComplexityClassifier()
            if self._neural_classifier.load():
                print("Neural classifier loaded successfully")
                return True
            else:
                print("Warning: No trained neural model available")
                self._neural_classifier = None
                return False
        except Exception as e:
            print(f"Error loading neural classifier: {e}")
            self._neural_classifier = None
            return False
    
    def clasificar_con_neural(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Clasifica la complejidad usando la red neuronal.
        
        Args:
            codigo: Código fuente o pseudocódigo a clasificar
            
        Returns:
            Diccionario con predicción, confianza y probabilidades, o None si falla
        """
        if not self._cargar_clasificador_neural():
            return None
        
        try:
            complejidad, confianza, probabilidades = self._neural_classifier.classify(codigo)
            return {
                'complejidad_predicha': complejidad,
                'confianza': confianza,
                'probabilidades': probabilidades,
                'metodo': 'Neural Algorithmix (MLP + DP + Backtracking)'
            }
        except Exception as e:
            print(f"Error in neural classification: {e}")
            return None
    
    def analizar_con_validacion_neural(self, algoritmo: Algoritmo) -> Tuple[Complejidad, Optional[Dict[str, Any]]]:
        """
        Analiza el algoritmo y valida con la red neuronal.
        
        Útil para comparar el análisis simbólico con la predicción neural.
        
        Args:
            algoritmo: Algoritmo a analizar
            
        Returns:
            Tupla (Complejidad del análisis simbólico, Predicción neural o None)
        """
        # Análisis simbólico normal
        complejidad = self.analizar_auto(algoritmo)
        
        # Validación neural
        prediccion_neural = self.clasificar_con_neural(algoritmo.codigo_fuente)
        
        # Agregar información neural al justification_data
        if prediccion_neural and complejidad.justification_data:
            complejidad.justification_data['neural_validation'] = {
                'predicted_complexity': prediccion_neural['complejidad_predicha'],
                'confidence': prediccion_neural['confianza'],
                'probabilities': prediccion_neural['probabilidades'],
                'matches_symbolic': prediccion_neural['complejidad_predicha'] == complejidad.notacion_o
            }
        
        return complejidad, prediccion_neural
    
    def analizar_solo_neural(self, codigo: str) -> Optional[Complejidad]:
        """
        Analiza usando SOLO la red neuronal (sin análisis simbólico).
        
        Útil cuando el análisis simbólico falla o para algoritmos muy complejos.
        
        Args:
            codigo: Código a analizar
            
        Returns:
            Objeto Complejidad basado en predicción neural, o None si falla
        """
        prediccion = self.clasificar_con_neural(codigo)
        if not prediccion:
            return None
        
        # Construir objeto Complejidad desde predicción neural
        complejidad_predicha = prediccion['complejidad_predicha']
        confianza = prediccion['confianza']
        
        justificacion = (
            f"Análisis realizado por Neural Algorithmix (Red Neuronal MLP).\n"
            f"Confianza de la predicción: {confianza:.1%}\n\n"
            f"Paradigmas utilizados:\n"
            f"- Programación Dinámica: Extracción de features (Levenshtein)\n"
            f"- Backtracking: Optimización de arquitectura\n"
            f"- Algoritmo Voraz: Entrenamiento (Gradient Descent)\n\n"
            f"Distribución de probabilidades:\n"
        )
        
        for comp, prob in sorted(prediccion['probabilidades'].items(), key=lambda x: -x[1]):
            bar = "█" * int(prob * 20)
            justificacion += f"  {comp}: {prob:.1%} {bar}\n"
        
        return Complejidad(
            id=self._id,
            notacion_o=complejidad_predicha,
            notacion_omega=complejidad_predicha,  # Aproximación
            notacion_theta=complejidad_predicha,  # Aproximación
            justificacion=justificacion,
            justification_data={
                'method': 'neural_network',
                'confidence': confianza,
                'probabilities': prediccion['probabilidades'],
                'paradigms_used': [
                    'Programación Dinámica (Feature Extraction)',
                    'Backtracking (Hyperparameter Tuning)',
                    'Algoritmo Voraz (Gradient Descent)'
                ]
            }
        )

    def analizar_hibrido(self, algoritmo: Algoritmo) -> Complejidad:
        """
        Sistema HÍBRIDO: Combina Red Neuronal + Análisis Simbólico.
        
        Estrategia:
        1. Ejecuta AMBOS análisis en paralelo conceptual
        2. Si ambos coinciden -> Alta confianza
        3. Si difieren -> Usa el simbólico pero reporta la discrepancia
        4. Si uno falla -> Usa el que funcione
        
        Args:
            algoritmo: Algoritmo a analizar
            
        Returns:
            Complejidad con información combinada de ambos métodos
        """
        resultado_simbolico = None
        resultado_neural = None
        
        # Paso 1: Análisis Simbólico (siempre intentar)
        try:
            resultado_simbolico = self.analizar_auto(algoritmo)
        except Exception as e:
            print(f"Symbolic analysis failed: {e}")
        
        # Paso 2: Análisis Neural (si está disponible)
        try:
            resultado_neural = self.clasificar_con_neural(algoritmo.codigo_fuente)
        except Exception as e:
            print(f"Neural analysis failed: {e}")
        
        # Paso 3: Combinar resultados
        return self._combinar_resultados(resultado_simbolico, resultado_neural, algoritmo)
    
    def _combinar_resultados(
        self, 
        simbolico: Optional[Complejidad], 
        neural: Optional[Dict[str, Any]],
        algoritmo: Algoritmo
    ) -> Complejidad:
        """
        Combina los resultados del análisis simbólico y neural.
        
        Prioridades:
        1. Ambos disponibles y coinciden -> Mayor confianza
        2. Ambos disponibles pero difieren -> Usa simbólico, reporta discrepancia
        3. Solo simbólico disponible -> Usa simbólico
        4. Solo neural disponible -> Usa neural
        5. Ninguno disponible -> Error
        """
        # Caso: Ninguno funciona
        if simbolico is None and neural is None:
            return Complejidad(
                id=self._id,
                notacion_o="O(?)",
                notacion_omega="Ω(?)",
                notacion_theta="Θ(?)",
                justificacion="Error: No se pudo realizar el análisis con ningún método.",
                justification_data={'error': 'both_methods_failed'}
            )
        
        # Caso: Solo neural disponible
        if simbolico is None and neural is not None:
            return self._crear_complejidad_desde_neural(neural, fallback_reason="symbolic_failed")
        
        # Caso: Solo simbólico disponible
        if simbolico is not None and neural is None:
            if simbolico.justification_data:
                simbolico.justification_data['hybrid_info'] = {
                    'neural_available': False,
                    'method_used': 'symbolic_only',
                    'reason': 'neural_not_available_or_failed'
                }
            return simbolico
        
        # Caso: Ambos disponibles - COMPARAR
        comp_simbolica = simbolico.notacion_o
        comp_neural = neural['complejidad_predicha']
        confianza_neural = neural['confianza']
        
        # Normalizar para comparación
        coinciden = self._normalizar_complejidad(comp_simbolica) == self._normalizar_complejidad(comp_neural)
        
        # Agregar información híbrida al resultado simbólico
        hybrid_info = {
            'neural_available': True,
            'neural_prediction': comp_neural,
            'neural_confidence': confianza_neural,
            'neural_probabilities': neural['probabilidades'],
            'methods_agree': coinciden,
            'method_used': 'hybrid'
        }
        
        if coinciden:
            # Ambos coinciden -> ALTA CONFIANZA
            hybrid_info['consensus'] = 'ALTA'
            hybrid_info['consensus_message'] = (
                f"Ambos métodos coinciden en {comp_simbolica}. "
                f"Confianza neural: {confianza_neural:.1%}"
            )
            justificacion_extra = (
                f"\n\n{'='*50}\n"
                f"VALIDACIÓN HÍBRIDA: CONSENSO\n"
                f"{'='*50}\n"
                f"Red Neuronal: {comp_neural} (confianza {confianza_neural:.1%})\n"
                f"Análisis Simbólico: {comp_simbolica}\n"
                f"Resultado: COINCIDEN - Alta confianza en el resultado\n"
            )
        else:
            # No coinciden -> Reportar discrepancia
            hybrid_info['consensus'] = 'DISCREPANCIA'
            hybrid_info['consensus_message'] = (
                f"Discrepancia detectada. "
                f"Simbólico: {comp_simbolica}, Neural: {comp_neural} ({confianza_neural:.1%}). "
                f"Se usa el análisis simbólico por ser más riguroso."
            )
            justificacion_extra = (
                f"\n\n{'='*50}\n"
                f"VALIDACIÓN HÍBRIDA: DISCREPANCIA\n"
                f"{'='*50}\n"
                f"Red Neuronal: {comp_neural} (confianza {confianza_neural:.1%})\n"
                f"Análisis Simbólico: {comp_simbolica}\n"
                f"Resultado: Se prioriza el análisis simbólico\n"
                f"Nota: La red puede necesitar más entrenamiento para este patrón\n"
            )
        
        # Actualizar el resultado simbólico con info híbrida
        if simbolico.justification_data:
            simbolico.justification_data['hybrid_info'] = hybrid_info
        else:
            simbolico.justification_data = {'hybrid_info': hybrid_info}
        
        simbolico.justificacion_matematica += justificacion_extra
        
        return simbolico
    
    def _normalizar_complejidad(self, complejidad: str) -> str:
        """Normaliza notación de complejidad para comparación."""
        return complejidad.replace('²', '^2').replace('³', '^3').replace(' ', '').upper()
    
    def _crear_complejidad_desde_neural(
        self, 
        neural: Dict[str, Any], 
        fallback_reason: str = ""
    ) -> Complejidad:
        """Crea objeto Complejidad desde predicción neural."""
        comp = neural['complejidad_predicha']
        confianza = neural['confianza']
        
        justificacion = (
            f"Análisis realizado por Neural Algorithmix (Red Neuronal MLP).\n"
            f"Confianza: {confianza:.1%}\n"
        )
        
        if fallback_reason:
            justificacion = f"[Fallback: {fallback_reason}]\n\n" + justificacion
        
        justificacion += "\nDistribución de probabilidades:\n"
        for c, prob in sorted(neural['probabilidades'].items(), key=lambda x: -x[1]):
            bar = "█" * int(prob * 20)
            justificacion += f"  {c}: {prob:.1%} {bar}\n"
        
        return Complejidad(
            id=self._id,
            notacion_o=comp,
            notacion_omega=comp,
            notacion_theta=comp,
            justificacion=justificacion,
            justification_data={
                'method': 'neural_fallback',
                'fallback_reason': fallback_reason,
                'confidence': confianza,
                'probabilities': neural['probabilidades']
            }
        )


