from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .Analizador import Analizador
    from .Reporte import Reporte
    from Servicios.Ast import AST
    from .tipo_algoritmo import TipoAlgoritmo

class Algoritmo:
    """
    Representa un algoritmo a ser analizado.
    Mapea la clase 'Algoritmo' del diagrama UML.
    """
    def __init__(self, id: int, codigo_fuente: str, tipo_algoritmo: TipoAlgoritmo):
        self._id = id
        self._codigo_fuente = codigo_fuente
        self._tipo_algoritmo = tipo_algoritmo
        self._arbol_sintactico: Optional[AST] = None
        self._reporte: Optional[Reporte] = None
        self._analizador: Optional[Analizador] = None

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int):
        self._id = value

    @property
    def codigo_fuente(self) -> str:
        return self._codigo_fuente

    @codigo_fuente.setter
    def codigo_fuente(self, value: str):
        self._codigo_fuente = value

    @property
    def tipo_algoritmo(self) -> TipoAlgoritmo:
        return self._tipo_algoritmo

    @tipo_algoritmo.setter
    def tipo_algoritmo(self, value: TipoAlgoritmo):
        self._tipo_algoritmo = value

    @property
    def arbol_sintactico(self) -> Optional[AST]:
        return self._arbol_sintactico

    @arbol_sintactico.setter
    def arbol_sintactico(self, value: Optional[AST]):
        self._arbol_sintactico = value

    @property
    def reporte(self) -> Optional[Reporte]:
        return self._reporte

    @reporte.setter
    def reporte(self, value: Optional[Reporte]):
        self._reporte = value

    @property
    def analizador(self) -> Optional[Analizador]:
        return self._analizador

    @analizador.setter
    def analizador(self, value: Optional[Analizador]):
        self._analizador = value