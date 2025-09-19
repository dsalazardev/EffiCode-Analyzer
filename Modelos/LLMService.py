from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Analizador import Analizador
    from .Complejidad import Complejidad
    from .Algoritmo import Algoritmo

class LLMService:
    """
    Servicio para interactuar con un modelo de lenguaje grande (LLM).
    Mapea la clase 'LLMService' del diagrama UML.
    """
    def __init__(self, id: int, api_key: str, modelo: str):
        self._id = id
        self._api_key = api_key
        self._modelo = modelo
        self._analizador: Analizador | None = None

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int):
        self._id = value

    @property
    def api_key(self) -> str:
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        self._api_key = value

    @property
    def modelo(self) -> str:
        return self._modelo

    @modelo.setter
    def modelo(self, value: str):
        self._modelo = value

    @property
    def analizador(self) -> Analizador | None:
        return self._analizador

    @analizador.setter
    def analizador(self, value: Analizador | None):
        self._analizador = value

    def traducir_natural_a_pseudocodigo(self, texto: str) -> str:
        """Usa el LLM para convertir lenguaje natural a pseudocódigo."""
        pass

    def validar_analisis(self, complejidad: Complejidad) -> str:
        """Pide al LLM que valide o dé una segunda opinión sobre un análisis."""
        pass

    def clasificar_patron(self, algoritmo: Algoritmo) -> str:
        """Usa el LLM para identificar el patrón de diseño del algoritmo (e.g., divide y vencerás)."""
        pass