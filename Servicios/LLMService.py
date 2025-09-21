from __future__ import annotations
import os
import json
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional
from pathlib import Path


# Dependencias (asegúrate de tenerlas instaladas)
# pip install python-dotenv google-generativeai
# pip install python-dotenv
# Usar en el main
# from dotenv import load_dotenv
# load_dotenv()

# pip install google-generativeai
# Se importa la librería de Google para interactuar con Gemini

try:
    import google.generativeai as genai
    from google.api_core import exceptions
except ImportError:
    print("Dependencia no encontrada. Instale 'google-generativeai'.")
    genai = None
    File = None

if TYPE_CHECKING:
    from Modelos.Analizador import Analizador
    from Modelos.Complejidad import Complejidad
    from Modelos.Algoritmo import Algoritmo


class LLMService:
    """
    Servicio principal de IA que opera con el contexto permanente del libro
    "Introduction to Algorithms" de Cormen, usando una estrategia de caché
    para optimizar el tiempo de inicio.
    """
    # La ruta al libro es ahora una constante interna de la clase.
    _ROOT = Path(__file__).resolve().parent.parent
    _RUTA_LIBRO = _ROOT / "Documentos" / "Introduction_to_Algorithms_by_Thomas_H_Coremen.pdf"
    _CACHE_FILE = _ROOT / "cache_file.json"

    def __init__(self, modelo: str = "gemini-2.5-pro"):
        """
        Inicializa el servicio LLM, configura la API y gestiona la carga
        del libro de contexto usando un sistema de caché.
        """
        self._api_key = os.getenv("GOOGLE_API_KEY")
        if not self._api_key:
            raise ValueError("API Key no encontrada. Configure la variable de entorno 'GOOGLE_API_KEY'.")
        if not genai:
            raise RuntimeError("La librería 'google-generativeai' no está instalada.")

        genai.configure(api_key=self._api_key)
        self._modelo_genai = genai.GenerativeModel(modelo)
        self._modelo = modelo
        self._analizador: Optional[Analizador] = None

        # --- Gestión del Contexto Permanente con Caché ---
        self._libro_contexto_file = self._gestionar_cache_libro()
        # -----------------------------------------------

    def _gestionar_cache_libro(self) -> File:
        """
        Verifica si existe una referencia válida del libro en caché.
        Si no, sube el libro y guarda la nueva referencia en caché.
        """
        cache_data = self._cargar_cache()
        if cache_data:
            nombre_archivo = cache_data.get("file_name")
            tiempo_carga_str = cache_data.get("upload_time")
            if nombre_archivo and tiempo_carga_str:
                tiempo_carga = datetime.fromisoformat(tiempo_carga_str)
                # Google almacena los archivos por 48 horas.
                if datetime.now() - tiempo_carga < timedelta(hours=48):
                    try:
                        print(f"--- [LLMService] Intentando reutilizar archivo en caché: {nombre_archivo} ---")
                        file_obj = genai.get_file(name=nombre_archivo)
                        print(f"Éxito. Usando el libro '{file_obj.display_name}' desde la caché.")
                        return file_obj
                    except exceptions.NotFound:
                        print("--- [LLMService] El archivo en caché ya no existe en Google. Se subirá de nuevo. ---")

        # Si no hay caché válido, se sube el archivo
        return self._subir_y_guardar_libro_en_cache()

    def _cargar_cache(self) -> Optional[dict]:
        """Carga los datos del archivo de caché si existe."""
        if self._CACHE_FILE.exists():
            with self._CACHE_FILE.open('r') as f:
                return json.load(f)
        return None

    def _subir_y_guardar_libro_en_cache(self) -> File:
        """Sube el libro a la API de Google y guarda su referencia en el archivo de caché."""
        print("--- [LLMService] Subiendo el libro de contexto a la API de Archivos de Google... ---")
        if not self._RUTA_LIBRO.exists():
            raise FileNotFoundError(f"No se encontró el libro en la ruta interna: {self._RUTA_LIBRO}")

        file_obj = genai.upload_file(path=self._RUTA_LIBRO)
        print(f"Libro '{file_obj.display_name}' subido con éxito.")

        cache_data = {
            "file_name": file_obj.name,
            "upload_time": datetime.now().isoformat()
        }
        with open(self._CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
        print(f"--- [LLMService] Referencia guardada en '{self._CACHE_FILE}'. ---")
        return file_obj

    # --- Propiedades y Setters (sin cambios) ---
    @property
    def modelo(self) -> str:
        return self._modelo

    # ... (resto de propiedades) ...

    # --- Métodos de Lógica de Negocio ---
    def _ejecutar_prompt_con_contexto(self, prompt: str) -> str:
        """Función auxiliar que siempre incluye el libro como contexto."""
        try:
            respuesta = self._modelo_genai.generate_content([self._libro_contexto_file, prompt])
            return respuesta.text.strip()
        except Exception as e:
            return f"Error al contactar la API de Gemini: {e}"

    def traducir_pseudocodigo_a_python(self, pseudocodigo: str) -> str:
        """Usa el LLM para convertir pseudocódigo a Python, basándose en el libro."""
        prompt = f"""
                    Actúa como un programador experto en algoritmos científico de la computación, especializado en traducir pseudocódigo del libro 'Introduction to Algorithms' de Cormen a Python idiomático.
                            
                    **Contexto Académico:** Tu única fuente de verdad es el libro 'Introduction to Algorithms' proporcionado. 

                    **Tarea:** Basado en las convenciones del libro, traduce el siguiente pseudocódigo a una función de Python.

                    **Reglas Estrictas:**
                    1.  **Salida Exclusiva de Código:** Responde **únicamente con el código Python**.
                    2.  **Fidelidad al Libro:** Traduce `←` se convierte en `=`, `A.length` a `len(A)`, `≤, ≥, ≠` en `<=, >=, !=` y adapta los bucles de 1-indexado a 0-indexado.
                    3.  **Manejo de índices:** Adapta los bucles y accesos de 1-indexado (Cormen) a 0-indexado (Python).

                    **Pseudocódigo a Traducir:**
                    ---
                    {pseudocodigo}
                    ---
                    """
        codigo_generado = self._ejecutar_prompt_con_contexto(prompt)
        return codigo_generado.replace("```python", "").replace("```", "").strip()

    def traducir_natural_a_pseudocodigo(self, texto: str) -> str:
        """Usa el LLM para convertir lenguaje natural a pseudocódigo estilo Cormen."""
        prompt = f"""
                    Actúa como un experto en el libro 'Introduction to Algorithms' de Cormen.
                    
                    **Contexto Académico:** Tu única fuente de verdad es el libro 'Introduction to Algorithms' proporcionado. 

                    **Tarea:** Convierte la siguiente descripción a pseudocódigo, siguiendo estrictamente el estilo del libro. Convierte la siguiente descripción en lenguaje natural a pseudocódigo, siguiendo estrictamente el estilo de Cormen.

                    **Reglas de Estilo del Libro:**
                    - Usa `←` para asignaciones.
                    - Usa `A.length` para la longitud de arreglos.
                    - Usa bucles `for`, `while` con la sintaxis del libro.
                    - Usa comentarios con `//`.

                    **Descripción a Convertir que viene en lenguaje Natural:**
                    "{texto}"
                    """
        return self._ejecutar_prompt_con_contexto(prompt)

    def validar_analisis(self, complejidad: Complejidad, pseudocodigo: str) -> str:
        """Pide al LLM que valide un análisis de complejidad, usando el libro como referencia."""
        prompt = f"""
                Actúa como un experto en análisis de algoritmos, al nivel de un profesor de ciencias de la computación.
                
                **Contexto Académico:** Tu única fuente de verdad es el libro 'Introduction to Algorithms' proporcionado.

                **Tarea:** Como un profesor de algoritmos, revisa y valida el siguiente análisis de complejidad basándote en la teoría del libro.

                **Pseudocódigo:**
                {pseudocodigo}


                **Análisis Propuesto:**
                - O(n): {complejidad.notacion_o}
                - Ω(n): {complejidad.notacion_omega}
                - Justificación: {complejidad.justificacion_matematica}

                **Tu Respuesta:** Proporciona una segunda opinión experta y concisa. Confirma si es correcto o explica claramente cualquier error o matiz, citando conceptos del libro si es relevante.
                """
        return self._ejecutar_prompt_con_contexto(prompt)

    def clasificar_patron(self, algoritmo: Algoritmo) -> str:
        """Usa el LLM para identificar el patrón de diseño del algoritmo, según las definiciones del libro."""
        prompt = f"""
                Actúa como un científico de la computación experto en paradigmas de diseño de algoritmos.
        
                **Contexto Académico:** Tu única fuente de verdad es el libro 'Introduction to Algorithms' proporcionado.

                **Tarea:** Identifica el principal paradigma de diseño algorítmico del pseudocódigo, usando la terminología del libro.

                **Pseudocódigo:**
                {algoritmo.codigo_fuente}


                **Instrucciones:** Responde únicamente con el nombre del patrón (ej: 'Divide and conquer', 'Dynamic programming', 'Greedy algorithm').
                 Responde únicamente con el nombre del patrón. Sé específico.
                 Ejemplos: 'Divide y Vencerás', 'Programación Dinámica', 'Algoritmo Voraz', 'Búsqueda por Fuerza Bruta', 'Backtracking'.
                 Si no identificas un patrón claro, responde 'No se identifica un patrón estándar'.
                """
        return self._ejecutar_prompt_con_contexto(prompt)
