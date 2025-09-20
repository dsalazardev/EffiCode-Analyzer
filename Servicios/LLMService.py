from __future__ import annotations
import os
from typing import TYPE_CHECKING, Optional

#pip install python-dotenv
# Usar en el main
# from dotenv import load_dotenv
# load_dotenv()

# pip install google-generativeai
# Se importa la librería de Google para interactuar con Gemini
try:
    import google.generativeai as genai
except ImportError:
    print("Dependencia no encontrada. Por favor, instale 'google-generativeai' usando: pip install google-generativeai")
    genai = None

# Type hints para evitar importaciones circulares y mantener el código limpio
if TYPE_CHECKING:
    from Modelos.Analizador import Analizador
    from Modelos.Complejidad import Complejidad
    from Modelos.Algoritmo import Algoritmo


class LLMService:
    """
    Servicio principal de IA para interactuar con un modelo de lenguaje grande (LLM).
    Contiene toda la lógica para conectarse a la API de Gemini y realizar tareas
    de análisis y traducción de algoritmos.
    """

    def __init__(self,modelo: str = "gemini-1.5-flash-latest"):
        """
        Inicializa el servicio LLM, configurando el cliente de la API.

        Args:
            id (int): Un identificador para esta instancia del servicio.
            modelo (str): El nombre del modelo de Gemini a utilizar.

        Raises:
            ValueError: Si la API key de Google no está configurada en las
                        variables de entorno.
            RuntimeError: Si la librería 'google-generativeai' no está instalada.
        """
        self._api_key = os.getenv("GOOGLE_API_KEY")
        if not self._api_key:
            raise ValueError("API Key no encontrada. Por favor, configure la variable de entorno 'GOOGLE_API_KEY'.")

        if not genai:
            raise RuntimeError("La librería 'google-generativeai' no está instalada.")

        genai.configure(api_key=self._api_key)
        self._modelo_genai = genai.GenerativeModel(modelo)
        self._modelo = modelo
        self._analizador: Optional[Analizador] = None

    # --- Propiedades y Setters ---

    @property
    def api_key(self) -> str:
        # Por seguridad, no devolvemos la clave completa, sino un indicador de que existe.
        return f"Key loaded: {'Yes' if self._api_key else 'No'}"

    @property
    def modelo(self) -> str:
        return self._modelo

    @modelo.setter
    def modelo(self, value: str):
        self._modelo = value
        # Si se cambia el modelo, se actualiza la instancia del modelo de genai
        self._modelo_genai = genai.GenerativeModel(value)

    @property
    def analizador(self) -> Optional[Analizador]:
        return self._analizador

    @analizador.setter
    def analizador(self, value: Optional[Analizador]):
        self._analizador = value

    # --- Métodos de Lógica de Negocio ---

    def _ejecutar_prompt(self, prompt: str) -> str:
        """
        Función auxiliar centralizada para enviar un prompt al modelo y devolver
        la respuesta limpia. Maneja errores de la API.
        """
        try:
            respuesta = self._modelo_genai.generate_content(prompt)
            return respuesta.text.strip()
        except Exception as e:
            error_msg = f"Error al contactar la API de Gemini: {e}"
            print(error_msg)
            return f"Error: {error_msg}"

    def traducir_pseudocodigo_a_python(self, pseudocodigo: str) -> str:
        """
        Usa el LLM para convertir pseudocódigo estilo Cormen a Python funcional.
        Este es el método clave para conectar la gramática con el AST de Python.
        """
        prompt = f"""
            Actúa como un programador experto en algoritmos, especializado en traducir pseudocódigo del libro 'Introduction to Algorithms' de Cormen a Python idiomático.
            
            **Tarea:** Traduce el siguiente pseudocódigo a una única función de Python.
            
            **Reglas Estrictas:**
            1.  **SALIDA EXCLUSIVA DE CÓDIGO:** Tu respuesta debe ser **únicamente el código Python**. No incluyas explicaciones, ```, ni texto que no sea código ejecutable.
            2.  **TRADUCCIÓN PRECISA:** `←` se convierte en `=`, `A.length` en `len(A)`, `≤, ≥, ≠` en `<=, >=, !=`.
            3.  **MANEJO DE ÍNDICES:** Adapta los bucles y accesos de 1-indexado (Cormen) a 0-indexado (Python).
            
            **Pseudocódigo a Traducir:**
            ---
            {pseudocodigo}
            ---
            """
        codigo_generado = self._ejecutar_prompt(prompt)
        return codigo_generado.replace("```python", "").replace("```", "").strip()

    def traducir_natural_a_pseudocodigo(self, texto: str) -> str:
        """Usa el LLM para convertir lenguaje natural a pseudocódigo estilo Cormen."""
        prompt = f"""
                Actúa como un experto en el libro 'Introduction to Algorithms' de Cormen.
                
                **Tarea:** Convierte la siguiente descripción en lenguaje natural a pseudocódigo, siguiendo estrictamente el estilo de Cormen.
                
                **Reglas de Estilo:**
                - Usa `←` para asignaciones.
                - Usa `A.length` para la longitud de arreglos.
                - Usa bucles `for`, `while` con la sintaxis del libro.
                - Usa comentarios con `//`.
                
                **Descripción en Lenguaje Natural:**
                "{texto}"
                """
        return self._ejecutar_prompt(prompt)

    def validar_analisis(self, complejidad: Complejidad, pseudocodigo: str) -> str:
        """Pide al LLM que valide o dé una segunda opinión sobre un análisis de complejidad."""
        prompt = f"""
                Actúa como un experto en análisis de algoritmos, al nivel de un profesor de ciencias de la computación.
                
                **Tarea:** Revisa y valida el siguiente análisis de complejidad para el pseudocódigo proporcionado.
                
                **Pseudocódigo:**
        
                {pseudocodigo}

                **Análisis Propuesto:**
                - **Peor Caso (Big O):** {complejidad.notacion_o}
                - **Mejor Caso (Big Omega):** {complejidad.notacion_omega}
                - **Justificación:** {complejidad.justificacion_matematica}
                
                **Tu Respuesta:**
                Proporciona una segunda opinión concisa y experta. Si el análisis es correcto, confírmalo y, si es posible, añade un matiz interesante. Si hay un error, explícalo de forma clara y sugiere la corrección.
                """
        return self._ejecutar_prompt(prompt)


    def clasificar_patron(self, algoritmo: Algoritmo) -> str:
        """Usa el LLM para identificar el patrón de diseño del algoritmo."""
        prompt = f"""
            Actúa como un científico de la computación experto en paradigmas de diseño de algoritmos.
            
            **Tarea:** Identifica el principal paradigma o patrón de diseño algorítmico utilizado en el siguiente pseudocódigo.
            
            **Pseudocódigo:**
            {algoritmo.codigo_fuente}
            
            
            **Instrucciones:**
            Responde únicamente con el nombre del patrón. Sé específico.
            Ejemplos: 'Divide y Vencerás', 'Programación Dinámica', 'Algoritmo Voraz', 'Búsqueda por Fuerza Bruta', 'Backtracking'.
            Si no identificas un patrón claro, responde 'No se identifica un patrón estándar'.
            """
        return self._ejecutar_prompt(prompt)

