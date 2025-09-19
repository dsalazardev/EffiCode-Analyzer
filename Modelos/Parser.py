# models/parser.py

from __future__ import annotations
from typing import TYPE_CHECKING

# Importaciones de tipos para evitar dependencias circulares
if TYPE_CHECKING:
    from .Analizador import Analizador
    from .Grammar import Grammar
    from .Ast import AST


class Parser:

    def __init__(self, id: int, gramatica: Grammar):
        self._id = id
        self._gramatica = gramatica
        self._analizador: Analizador | None = None

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int):
        self._id = value

    @property
    def gramatica(self) -> Grammar:
        return self._gramatica

    @gramatica.setter
    def gramatica(self, value: Grammar):
        self._gramatica = value

    @property
    def analizador(self) -> Analizador | None:
        return self._analizador

    @analizador.setter
    def analizador(self, value: Analizador | None):
        self._analizador = value

    def parsear(self, codigo: str) -> AST:
        """Convierte el código en un Árbol de Sintaxis Abstracta (AST)."""
        # Lógica de parsing
        pass

    def validar_sintaxis(self, codigo: str) -> bool:
        """Verifica si el código cumple con la gramática definida."""
        # Lógica de validación de sintaxis
        pass