"""
Router para el módulo de análisis de complejidad algorítmica.
Contiene todos los endpoints relacionados con el análisis de pseudocódigo.
"""
import base64
import json
import pydot
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response, JSONResponse

from Modelos.Algoritmo import Algoritmo
from Modelos.Reporte import Reporte
from Enumerations.tipoAlgoritmo import TipoAlgoritmo
from Servicios.ReportService import ReportService

from ..deps import get_services, ServiceContainer
from ..schemas.analysis import (
    AnalysisRequest, AnalysisResponse, ReportRequest, 
    ValidationRequest, ValidationResponse,
    NaturalLanguageRequest, NaturalLanguageResponse
)


router = APIRouter(
    tags=["Analysis"],
    responses={
        500: {"description": "Internal server error"},
        422: {"description": "Validation error"}
    }
)


def generate_ast_image_base64(ast_obj) -> str:
    """
    Genera una imagen PNG del AST codificada en Base64.
    
    Args:
        ast_obj: Objeto AST a visualizar
        
    Returns:
        String con la imagen en formato data:image/png;base64,...
    """
    try:
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
                    label=str(nodo)[:50],  # Limitar longitud
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
    
    except Exception as e:
        print(f"Error generating AST image: {e}")
        return ""


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analizar pseudocódigo",
    description="Analiza pseudocódigo estilo Cormen y devuelve la complejidad algorítmica (sin esperar validación IA)"
)
async def analyze_pseudocode(
    request: AnalysisRequest,
    services: ServiceContainer = Depends(get_services)
) -> AnalysisResponse:
    """
    Analiza el pseudocódigo proporcionado y calcula su complejidad algorítmica.
    
    NOTA: La validación de IA se hace en un endpoint separado (/validate)
    para evitar bloquear la respuesta principal.
    
    El proceso incluye:
    1. Parsing del pseudocódigo a Python
    2. Generación del AST
    3. Análisis de complejidad (Big O, Omega, Theta)
    4. Generación de imagen del AST
    
    Args:
        request: Objeto con el pseudocódigo a analizar
        services: Contenedor de servicios (inyectado automáticamente)
        
    Returns:
        AnalysisResponse con todos los resultados del análisis (validation=None)
        
    Raises:
        HTTPException: Si hay error en el parsing o análisis
    """
    try:
        pseudocode = request.pseudocode
        print(f"Analyzing pseudocode:\n{pseudocode}")

        # Step 1: Parse pseudocode to AST
        ast_obj = services.parser.parsear(pseudocode)
        
        # Step 2: Create Algorithm object
        algoritmo = Algoritmo(
            id=1, 
            codigo_fuente=pseudocode, 
            tipo_algoritmo=TipoAlgoritmo.ITERATIVO
        )
        algoritmo.addAST(ast_obj)
        
        # Step 3: ANÁLISIS HÍBRIDO (Neural + Simbólico combinados)
        resultado_complejidad = services.analizador.analizar_hibrido(algoritmo)
        
        # Step 4: Generate AST Image
        ast_image_base64 = generate_ast_image_base64(ast_obj)

        print(f"Hybrid analysis complete: {resultado_complejidad.notacion_o}")
        
        # Retornamos con información híbrida incluida
        return AnalysisResponse(
            complexity_o=resultado_complejidad.notacion_o,
            complexity_omega=resultado_complejidad.notacion_omega,
            complexity_theta=resultado_complejidad.notacion_theta,
            justification=resultado_complejidad.justificacion_matematica,
            justification_data=resultado_complejidad.justification_data,
            validation=None,  # Se obtendrá en /validate
            ast_image=ast_image_base64
        )

    except SyntaxError as e:
        print(f"Syntax error: {e}")
        raise HTTPException(status_code=400, detail=f"Error de sintaxis: {str(e)}")
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post(
    "/validate",
    response_model=ValidationResponse,
    summary="Validar análisis con IA",
    description="Valida el análisis de complejidad usando IA (Gemini). Endpoint separado para carga asíncrona."
)
async def validate_with_ai(
    request: ValidationRequest,
    services: ServiceContainer = Depends(get_services)
) -> ValidationResponse:
    """
    Valida el análisis de complejidad usando IA (Gemini).
    
    Este endpoint está separado del análisis principal para permitir
    que el frontend muestre los resultados inmediatamente mientras
    la validación de IA se carga de forma asíncrona.
    
    Args:
        request: Datos del análisis a validar
        services: Contenedor de servicios
        
    Returns:
        ValidationResponse con el texto de validación
    """
    try:
        print(f"Starting AI validation for: {request.complexity_o}")
        
        # Crear objeto de complejidad simplificado para el LLM
        class SimpleComplexity:
            def __init__(self, o, omega, theta, justificacion):
                self.notacion_o = o
                self.notacion_omega = omega
                self.notacion_theta = theta
                self.justificacion_matematica = justificacion
        
        resultado_complejidad = SimpleComplexity(
            request.complexity_o,
            request.complexity_omega,
            request.complexity_theta,
            request.justification
        )
        
        validacion_ia = services.llm_service.validar_analisis(
            resultado_complejidad,
            request.pseudocode
        )
        
        print(f"AI validation complete")
        
        return ValidationResponse(
            validation=validacion_ia,
            status="completed"
        )
        
    except Exception as e:
        print(f"AI validation failed: {e}")
        return ValidationResponse(
            validation=f"Validación IA no disponible: {str(e)}",
            status="error"
        )


@router.get(
    "/health",
    summary="Health check",
    description="Verifica que el servicio de análisis esté funcionando"
)
async def health_check(
    services: ServiceContainer = Depends(get_services)
) -> dict:
    """Endpoint de health check para el módulo de análisis."""
    return {
        "status": "healthy",
        "services": {
            "grammar": services.grammar is not None,
            "parser": services.parser is not None,
            "analizador": services.analizador is not None,
            "llm_service": services.llm_service is not None
        }
    }


# === ENDPOINTS DE REPORTES ===

# Instancia del servicio de reportes
_report_service = ReportService()


@router.post(
    "/report/pdf",
    summary="Generar reporte PDF",
    description="Genera un reporte PDF completo del análisis de complejidad"
)
async def generate_pdf_report(request: ReportRequest):
    """
    Genera un reporte PDF descargable con el análisis completo.
    
    Incluye:
    - Código fuente analizado
    - Tabla de complejidades (O, Ω, Θ, E[T(n)])
    - Pasos de resolución matemática
    - Costos por línea de código
    
    Returns:
        Response con el archivo PDF
    """
    try:
        pdf_bytes = _report_service.generar_pdf(
            analysis_data=request.analysis_data,
            pseudocode=request.pseudocode
        )
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=reporte_complejidad.pdf"
            }
        )
    
    except ImportError as e:
        raise HTTPException(
            status_code=501, 
            detail="Generación de PDF no disponible. Instale reportlab: pip install reportlab"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")


@router.post(
    "/report/json",
    summary="Generar reporte JSON",
    description="Genera un reporte JSON estructurado del análisis de complejidad"
)
async def generate_json_report(request: ReportRequest):
    """
    Genera un reporte JSON estructurado con el análisis completo.
    
    El JSON incluye:
    - Metadatos del reporte
    - Código fuente
    - Todas las complejidades
    - Pasos de resolución detallados
    - Costos por línea
    
    Returns:
        JSONResponse con el reporte estructurado
    """
    try:
        report_data = _report_service.generar_json(
            analysis_data=request.analysis_data,
            pseudocode=request.pseudocode
        )
        
        # Convertir a JSON con formato bonito
        json_str = json.dumps(report_data, ensure_ascii=False, indent=2)
        
        return Response(
            content=json_str,
            media_type="application/json",
            headers={
                "Content-Disposition": "attachment; filename=reporte_complejidad.json"
            }
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generando JSON: {str(e)}")


@router.post(
    "/translate/natural-to-pseudocode",
    response_model=NaturalLanguageResponse,
    summary="Traducir lenguaje natural a pseudocódigo",
    description="Usa IA para convertir una descripción en lenguaje natural a pseudocódigo estilo Cormen"
)
async def translate_natural_to_pseudocode(
    request: NaturalLanguageRequest,
    services: ServiceContainer = Depends(get_services)
):
    """
    Traduce una descripción en lenguaje natural a pseudocódigo estilo Cormen.
    
    Esta funcionalidad utiliza un modelo de lenguaje (LLM) para interpretar
    la descripción del usuario y generar pseudocódigo siguiendo las convenciones
    del libro "Introduction to Algorithms" de Cormen.
    
    ⚠️ ADVERTENCIA: Esta funcionalidad depende de IA externa (Google Gemini).
    Si el servicio no está disponible, la operación fallará.
    
    Args:
        request: Objeto con el texto en lenguaje natural
        
    Returns:
        NaturalLanguageResponse con el pseudocódigo generado
        
    Raises:
        HTTPException 503: Si el servicio de IA no está disponible
        HTTPException 500: Si ocurre un error durante la traducción
    """
    try:
        # Verificar que el servicio LLM esté disponible
        if services.llm_service is None:
            raise HTTPException(
                status_code=503,
                detail="El servicio de IA no está disponible. Configure la variable GOOGLE_API_KEY."
            )
        
        # Realizar la traducción
        pseudocode = services.llm_service.traducir_natural_a_pseudocodigo(request.text)
        
        # Verificar si hubo error en la respuesta
        if pseudocode.startswith("# Error:"):
            raise HTTPException(
                status_code=503,
                detail="Error al contactar el servicio de IA. Intente nuevamente."
            )
        
        # Limpiar el pseudocódigo (remover marcadores de código si existen)
        pseudocode = pseudocode.replace("```pseudocode", "").replace("```", "").strip()
        
        return NaturalLanguageResponse(
            pseudocode=pseudocode,
            status="completed",
            warning="⚠️ Este resultado fue generado por IA. Verifique la sintaxis antes de analizar."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error durante la traducción: {str(e)}"
        )
