"""
Controlador de Análisis de Complejidad Algorítmica.

Este controlador actúa como intermediario entre la capa de presentación (API/CLI/GUI)
y la capa de servicios. Su responsabilidad es orquestar el flujo de análisis
sin conocer detalles de HTTP o interfaz de usuario.

Patrón: Controller (MVC) / Application Service (DDD)

Ventajas:
- Desacopla la lógica de orquestación de la API
- Facilita testing unitario
- Permite reutilizar la lógica en CLI, GUI, tests
- Centraliza el manejo de errores de negocio
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import base64
import pydot

from Modelos.Algoritmo import Algoritmo
from Modelos.Complejidad import Complejidad
from Modelos.Reporte import Reporte
from Modelos.Parser import Parser
from Modelos.Analizador import Analizador
from Enumerations.tipoAlgoritmo import TipoAlgoritmo
from Servicios.LLMService import LLMService
from Servicios.ReportService import ReportService


@dataclass
class ResultadoAnalisis:
    """DTO para el resultado del análisis."""
    complejidad_o: str
    complejidad_omega: str
    complejidad_theta: str
    justificacion: str
    justification_data: Dict[str, Any]
    ast_imagen: Optional[str] = None
    validacion_ia: Optional[str] = None
    es_recursivo: bool = False
    errores: list = None
    
    def __post_init__(self):
        if self.errores is None:
            self.errores = []


class AnalisisController:
    """
    Controlador para el análisis de complejidad algorítmica.
    
    Orquesta el flujo completo de análisis:
    1. Parsing del pseudocódigo
    2. Detección del tipo de algoritmo
    3. Análisis de complejidad
    4. Generación de visualizaciones
    5. Validación con IA (opcional)
    
    Attributes:
        parser: Servicio de parsing
        analizador: Servicio de análisis de complejidad
        llm_service: Servicio de IA para validación
        report_service: Servicio de generación de reportes
    """
    
    def __init__(
        self, 
        parser: Parser, 
        analizador: Analizador, 
        llm_service: Optional[LLMService] = None
    ):
        """
        Inicializa el controlador con las dependencias necesarias.
        
        Args:
            parser: Instancia del parser de pseudocódigo
            analizador: Instancia del analizador de complejidad
            llm_service: Instancia del servicio LLM (opcional)
        """
        self._parser = parser
        self._analizador = analizador
        self._llm_service = llm_service
        self._report_service = ReportService()
    
    def analizar(
        self, 
        pseudocodigo: str, 
        generar_imagen_ast: bool = True,
        incluir_validacion_ia: bool = False
    ) -> ResultadoAnalisis:
        """
        Ejecuta el análisis completo de un pseudocódigo.
        
        Este es el método principal que orquesta todo el flujo de análisis.
        
        Args:
            pseudocodigo: Código en pseudocódigo estilo Cormen
            generar_imagen_ast: Si debe generar imagen del AST
            incluir_validacion_ia: Si debe incluir validación con IA
            
        Returns:
            ResultadoAnalisis con todos los resultados
            
        Raises:
            ValueError: Si el pseudocódigo está vacío
            SyntaxError: Si hay errores de sintaxis en el pseudocódigo
        """
        # Validación de entrada
        if not pseudocodigo or not pseudocodigo.strip():
            raise ValueError("El pseudocódigo no puede estar vacío")
        
        errores = []
        
        # 1. Parsing del pseudocódigo
        try:
            ast_obj = self._parser.parsear(pseudocodigo)
        except Exception as e:
            raise SyntaxError(f"Error de sintaxis en el pseudocódigo: {str(e)}")
        
        # 2. Crear objeto Algoritmo
        algoritmo = Algoritmo(
            id=1,
            codigo_fuente=pseudocodigo,
            tipo_algoritmo=TipoAlgoritmo.DESCONOCIDO
        )
        algoritmo.addAST(ast_obj)
        
        # 3. Detectar tipo y analizar
        es_recursivo = self._analizador.es_recursivo(algoritmo)
        
        try:
            if es_recursivo:
                algoritmo.tipo_algoritmo = TipoAlgoritmo.RECURSIVO
                complejidad = self._analizador.analizar_recursivo(algoritmo)
            else:
                algoritmo.tipo_algoritmo = TipoAlgoritmo.ITERATIVO
                complejidad = self._analizador.analizar(algoritmo)
        except Exception as e:
            # Fallback al análisis híbrido si falla
            errores.append(f"Advertencia: {str(e)}. Usando análisis híbrido.")
            complejidad = self._analizador.analizar_hibrido(algoritmo)
        
        # 4. Generar imagen del AST (opcional)
        ast_imagen = None
        if generar_imagen_ast:
            try:
                ast_imagen = self._generar_imagen_ast(ast_obj)
            except Exception as e:
                errores.append(f"No se pudo generar imagen del AST: {str(e)}")
        
        # 5. Validación con IA (opcional)
        validacion_ia = None
        if incluir_validacion_ia and self._llm_service:
            try:
                validacion_ia = self._llm_service.validar_analisis(
                    complejidad, 
                    pseudocodigo
                )
            except Exception as e:
                errores.append(f"No se pudo obtener validación IA: {str(e)}")
        
        # 6. Construir resultado
        return ResultadoAnalisis(
            complejidad_o=complejidad.notacion_o,
            complejidad_omega=complejidad.notacion_omega,
            complejidad_theta=complejidad.notacion_theta,
            justificacion=complejidad.justificacion,
            justification_data=complejidad.justification_data or {},
            ast_imagen=ast_imagen,
            validacion_ia=validacion_ia,
            es_recursivo=es_recursivo,
            errores=errores
        )
    
    def validar_con_ia(self, pseudocodigo: str, complejidad_calculada: str) -> str:
        """
        Solicita validación de la IA para un análisis previo.
        
        Args:
            pseudocodigo: El código analizado
            complejidad_calculada: La complejidad que se calculó
            
        Returns:
            String con la validación de la IA
            
        Raises:
            RuntimeError: Si el servicio LLM no está disponible
        """
        if not self._llm_service:
            raise RuntimeError("Servicio LLM no disponible")
        
        # Crear un objeto Complejidad mínimo para la validación
        complejidad = Complejidad(
            id=1,
            notacion_o=complejidad_calculada,
            notacion_omega=complejidad_calculada.replace("O", "Ω"),
            notacion_theta=complejidad_calculada.replace("O", "Θ"),
            justificacion="Análisis previo"
        )
        
        return self._llm_service.validar_analisis(complejidad, pseudocodigo)
    
    def generar_reporte_pdf(
        self, 
        pseudocodigo: str, 
        resultado: ResultadoAnalisis
    ) -> bytes:
        """
        Genera un reporte PDF del análisis.
        
        Args:
            pseudocodigo: El código analizado
            resultado: El resultado del análisis
            
        Returns:
            Bytes del PDF generado
        """
        # Crear objetos necesarios para el reporte
        algoritmo = Algoritmo(
            id=1,
            codigo_fuente=pseudocodigo,
            tipo_algoritmo=TipoAlgoritmo.RECURSIVO if resultado.es_recursivo else TipoAlgoritmo.ITERATIVO
        )
        
        complejidad = Complejidad(
            id=1,
            notacion_o=resultado.complejidad_o,
            notacion_omega=resultado.complejidad_omega,
            notacion_theta=resultado.complejidad_theta,
            justificacion=resultado.justificacion,
            justification_data=resultado.justification_data
        )
        
        reporte = Reporte(
            id=1,
            algoritmo_analizado=algoritmo,
            resultado_complejidad=complejidad
        )
        reporte.validacion_llm = resultado.validacion_ia
        
        return self._report_service.generar_pdf(reporte)
    
    def _generar_imagen_ast(self, ast_obj) -> str:
        """
        Genera una imagen PNG del AST codificada en Base64.
        
        Args:
            ast_obj: Objeto AST a visualizar
            
        Returns:
            String con la imagen en formato data:image/png;base64,...
        """
        graph = pydot.Dot("AST", graph_type="digraph", rankdir="TB")
        graph.set_node_defaults(fontname="Arial", fontsize="10")
        graph.set_edge_defaults(color="#666666")

        def agregar_nodo(nodo, padre=None):
            if isinstance(nodo, dict):
                label = nodo.get("_type", str(type(nodo)))
                current_node = pydot.Node(
                    id(nodo), 
                    label=label, 
                    shape="box", 
                    style="rounded,filled", 
                    fillcolor="#E3F2FD",
                    fontcolor="#1565C0"
                )
                graph.add_node(current_node)

                if padre:
                    graph.add_edge(pydot.Edge(id(padre), id(nodo)))

                for k, v in nodo.items():
                    if isinstance(v, (dict, list)):
                        agregar_nodo(v, nodo)

            elif isinstance(nodo, list):
                for elemento in nodo:
                    agregar_nodo(elemento, padre)
            else:
                leaf_node = pydot.Node(
                    id(nodo), 
                    label=str(nodo)[:50],
                    shape="ellipse", 
                    fillcolor="#FFF9C4", 
                    style="filled",
                    fontcolor="#F57F17"
                )
                graph.add_node(leaf_node)
                if padre:
                    graph.add_edge(pydot.Edge(id(padre), id(nodo)))

        ast_dict = ast_obj.to_dict() if hasattr(ast_obj, "to_dict") else ast_obj
        agregar_nodo(ast_dict)
        
        png_data = graph.create_png()
        base64_encoded = base64.b64encode(png_data).decode("utf-8")
        return f"data:image/png;base64,{base64_encoded}"


# =========================================================================
# FACTORY FUNCTION
# =========================================================================

def crear_controlador_analisis(
    parser: Parser, 
    analizador: Analizador, 
    llm_service: Optional[LLMService] = None
) -> AnalisisController:
    """
    Factory function para crear un AnalisisController.
    
    Args:
        parser: Instancia del parser
        analizador: Instancia del analizador
        llm_service: Instancia del servicio LLM (opcional)
        
    Returns:
        Instancia configurada de AnalisisController
    """
    return AnalisisController(parser, analizador, llm_service)
