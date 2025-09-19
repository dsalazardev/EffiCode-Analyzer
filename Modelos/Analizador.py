from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .Algoritmo import Algoritmo
    from .Reporte import Reporte
    from .Complejidad import Complejidad
    from .Parser import Parser
    from Servicios.LLMService import LLMService
    from .Usuario import Usuario
    from Servicios.Ast import AST


class Analizador:
    """
    Clase central que orquesta el análisis de complejidad.
    Mapea la clase 'Analizador' del diagrama UML.
    """
    def __init__(self, parser: Parser, llm_service: LLMService):
        self._algoritmos: List[Algoritmo] = []
        self._reporte: Reporte | None = None
        self._complejidad: Complejidad | None = None
        self._parser = parser
        self._llm_service = llm_service
        self._usuario: Usuario | None = None

    @property
    def algoritmos(self) -> List[Algoritmo]:
        return self._algoritmos

    @property
    def reporte(self) -> Reporte | None:
        return self._reporte

    @reporte.setter
    def reporte(self, value: Reporte | None):
        self._reporte = value

    @property
    def complejidad(self) -> Complejidad | None:
        return self._complejidad

    @complejidad.setter
    def complejidad(self, value: Complejidad | None):
        self._complejidad = value

    @property
    def parser(self) -> Parser:
        return self._parser

    @parser.setter
    def parser(self, value: Parser):
        self._parser = value

    @property
    def llm_service(self) -> LLMService:
        return self._llm_service

    @llm_service.setter
    def llm_service(self, value: LLMService):
        self._llm_service = value

    @property
    def usuario(self) -> Usuario | None:
        return self._usuario

    @usuario.setter
    def usuario(self, value: Usuario | None):
        self._usuario = value

    def calcular_o(self, ast: AST) -> str:
        """Calcula la cota superior asintótica (Peor Caso)."""
        pass

    def calcular_omega(self, ast: AST) -> str:
        """Calcula la cota inferior asintótica (Mejor Caso)."""
        pass

    def calcular_theta(self, ast: AST) -> str:
        """Calcula la cota ajustada asintótica (Caso Promedio)."""
        pass

    def generar_justificacion(self, ast: AST) -> str:
        """Genera la justificación matemática del análisis."""
        pass

    def analizar(self, algoritmo: Algoritmo) -> Complejidad:
        """Realiza el análisis completo de un algoritmo."""
        pass