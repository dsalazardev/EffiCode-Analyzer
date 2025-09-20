from __future__ import annotations
from typing import TYPE_CHECKING

from Servicios.Grammar import Grammar
from Servicios.LLMService import LLMService
from Servicios.Ast import AST

# Importaciones de tipos para evitar dependencias circulares
if TYPE_CHECKING:
    from .Analizador import Analizador

class Parser:

    def __init__(self, id: int, gramatica: Grammar, llm_service: LLMService):
        self._id = id
        self._gramatica = gramatica
        self._analizador: Analizador | None = None
        self._llm_service = llm_service

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



    def validar_sintaxis(self, pseudocodigo: str) -> bool:
        """
        Verifica si el código cumple con la gramática definida.
        Delega la validación al servicio de Gramática.
        """
        return self._gramatica.validar_sentencia(pseudocodigo)

    def parsear(self, pseudocodigo: str) -> AST:
        """
        Convierte el pseudocódigo en un Árbol de Sintaxis Abstracta (AST) de Python.
        El proceso implica validar la sintaxis del pseudocódigo, traducirlo a
        Python usando un LLM y finalmente, parsear ese código Python a un AST.

        Args:
            pseudocodigo (str): El código fuente en pseudocódigo estilo Cormen.

        Returns:
            AST: Una instancia del servicio AST que contiene el árbol del código Python.

        Raises:
            SyntaxError: Si la sintaxis del pseudocódigo es inválida o si el
                         código Python generado por el LLM es inválido.
            ConnectionError: Si hay un problema con el servicio de traducción del LLM.
        """
        # 1. Validar la sintaxis usando el servicio de Gramática
        if not self.validar_sintaxis(pseudocodigo):
            raise SyntaxError("Error de sintaxis: El pseudocódigo no es válido según la gramática.")

        # 2. Traducir a Python usando el servicio LLM
        codigo_python = self._llm_service.traducir_pseudocodigo_a_python(pseudocodigo)
        if not codigo_python or "# Error" in codigo_python:
            raise ConnectionError(f"Error de traducción: El servicio LLM falló. Detalles: {codigo_python}")

        # 3. Parsear el código Python y devolver el objeto AST
        try:
            ast_obj = AST(codigo_python)
            return ast_obj
        except SyntaxError as e:
            # Este error ocurre si el LLM devuelve código Python que no es sintácticamente correcto
            raise SyntaxError(
                f"El código generado por el LLM no es válido. Error: {e}\nCódigo recibido:\n{codigo_python}")

# --- Ejemplo de Uso ---
if __name__ == '__main__':
    # Este bloque demuestra cómo se instancia y usa la clase Parser
    from dotenv import load_dotenv
    load_dotenv()


    # 1. Inicializar los servicios de los que depende el Parser
    try:
        grammar_service = Grammar()
        llm_service = LLMService()
    except (ValueError, RuntimeError) as e:
        print(f"Error al inicializar servicios base: {e}")
        exit()

    # 2. Instanciar el Parser, inyectando sus dependencias
    parser = Parser(id=1, gramatica=grammar_service, llm_service=llm_service)

    # 3. Definir un pseudocódigo para la prueba
    pseudocodigo_valido = """
    INSERTION-SORT(A)
        for j ← 2 to A.length do
            key ← A[j]
            i ← j - 1
            while i > 0 and A[i] > key do
                A[i+1] ← A[i]
                i ← i - 1
            A[i+1] ← key
    """

    # 4. Ejecutar el método `parsear`
    print("Iniciando proceso de parsing...")
    try:
        ast_final = parser.parsear(pseudocodigo_valido)
        print("\n--- Traducción a Python ---")
        print(ast_final._codigo)  # Accedemos al código guardado en el AST
        print("\n--- Análisis del AST ---")
        print(f"Nodos en el AST: {ast_final.contar_nodos()}")
        print(f"Bucles encontrados: {ast_final.extraer_bucles()}")
        print("\nParsing completado con éxito.")

    except (SyntaxError, ConnectionError) as e:
        print(f"\nERROR durante el parsing: {e}")