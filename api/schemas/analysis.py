"""
Schemas para el módulo de análisis de complejidad.
Incluye soporte para caso promedio basado en Cormen Cap. 5.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal


class AnalysisRequest(BaseModel):
    """Request para analizar pseudocódigo."""
    pseudocode: str = Field(
        ..., 
        description="Pseudocódigo estilo Cormen a analizar",
        min_length=1
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "pseudocode": """INSERTION-SORT(A, n)
    for j ← 2 to n do
        key ← A[j]
        i ← j - 1
        while i > 0 and A[i] > key do
            A[i + 1] ← A[i]
            i ← i - 1
        A[i + 1] ← key
    return A"""
            }
        }


class ReportRequest(BaseModel):
    """Request para generar reporte de análisis."""
    pseudocode: str = Field(
        ..., 
        description="Pseudocódigo analizado",
        min_length=1
    )
    analysis_data: Dict[str, Any] = Field(
        ...,
        description="Datos del análisis de complejidad"
    )
    format: Literal["pdf", "json"] = Field(
        default="pdf",
        description="Formato del reporte: 'pdf' o 'json'"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "pseudocode": "INSERTION-SORT(A, n)...",
                "analysis_data": {
                    "complexity": {"bigO": "O(n²)"},
                    "justification": {}
                },
                "format": "pdf"
            }
        }


class AverageCaseInfo(BaseModel):
    """Información del caso promedio basado en análisis probabilístico."""
    complexity: str = Field(..., description="Complejidad esperada E[T(n)]")
    dominant_term: Optional[str] = Field(None, description="Término dominante")
    description: str = Field(..., description="Descripción del análisis probabilístico")
    distribution_assumed: Optional[str] = Field(None, description="Distribución de probabilidad asumida")
    constant_factor: Optional[str] = Field(None, description="Factor constante comparativo")


class AnalysisResponse(BaseModel):
    """Response con el resultado del análisis de complejidad."""
    complexity_o: str = Field(..., description="Notación Big O (peor caso)")
    complexity_omega: str = Field(..., description="Notación Big Omega (mejor caso)")
    complexity_theta: str = Field(..., description="Notación Big Theta (caso ajustado)")
    complexity_average: Optional[str] = Field(None, description="Complejidad caso promedio E[T(n)]")
    justification: str = Field(..., description="Justificación matemática")
    justification_data: Dict[str, Any] = Field(..., description="Datos estructurados de la justificación")
    validation: Optional[str] = Field(None, description="Validación por IA (None = pendiente)")
    ast_image: str = Field(..., description="Imagen del AST en Base64 (PNG)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "complexity_o": "O(n²)",
                "complexity_omega": "Ω(n)",
                "complexity_theta": "No aplicable",
                "complexity_average": "E[T(n)] = Θ(n²)",
                "justification": "El algoritmo contiene bucles anidados...",
                "justification_data": {
                    "resolution_steps": {
                        "worst_case": [],
                        "best_case": [],
                        "average_case": []
                    },
                    "conclusion": {
                        "worst_case": {"complexity": "O(n²)", "dominant_term": "n²"},
                        "best_case": {"complexity": "Ω(n)", "dominant_term": "n"},
                        "average_case": {
                            "complexity": "E[T(n)] = Θ(n²)",
                            "dominant_term": "n²",
                            "description": "Usando análisis probabilístico con distribución uniforme"
                        }
                    }
                },
                "validation": "El análisis es correcto...",
                "ast_image": "data:image/png;base64,..."
            }
        }


class ValidationRequest(BaseModel):
    """Request para validar análisis con IA."""
    pseudocode: str = Field(
        ..., 
        description="Pseudocódigo analizado",
        min_length=1
    )
    complexity_o: str = Field(..., description="Notación Big O calculada")
    complexity_omega: str = Field(..., description="Notación Big Omega calculada")
    complexity_theta: str = Field(..., description="Notación Big Theta calculada")
    justification: str = Field(..., description="Justificación matemática")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pseudocode": "INSERTION-SORT(A, n)...",
                "complexity_o": "O(n²)",
                "complexity_omega": "Ω(n)",
                "complexity_theta": "No aplicable",
                "justification": "Bucles anidados..."
            }
        }


class ValidationResponse(BaseModel):
    """Response con la validación de IA."""
    validation: str = Field(..., description="Texto de validación de la IA")
    status: str = Field(default="completed", description="Estado: 'completed' o 'error'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "validation": "✅ El análisis es correcto. La complejidad O(n²) se justifica por...",
                "status": "completed"
            }
        }
