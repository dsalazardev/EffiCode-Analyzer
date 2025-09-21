# main.py

import os
from dotenv import load_dotenv

# --- Importaciones de Servicios ---
from Servicios.Grammar import Grammar
from Servicios.LLMService import LLMService
from Servicios.Ast import AST
# from Servicios.AnalysisService import AnalysisService # <-- ¡Este es el siguiente a crear!

# --- Importaciones de Modelos ---
from Modelos.Algoritmo import Algoritmo
from Enumerations.tipo_algoritmo import TipoAlgoritmo
from Modelos.Reporte import Reporte
from Modelos.Complejidad import Complejidad
from Modelos.Usuario import Usuario
from Modelos.Parser import Parser


# --- SIMULACIÓN DEL AnalysisService (El cerebro que falta por construir) ---
class MockAnalysisService:
    def analizar(self, ast: AST) -> Complejidad:
        print("\n[PASO 3] Analizando el AST con la teoría de Cormen...")
        bucles = ast.extraer_bucles()

        # Lógica de ejemplo basada en la estructura del AST
        if 'For' in bucles and 'While' in bucles:
            print("-> Se detectó un bucle 'for' con un 'while' anidado.")
            return Complejidad(id=1, notacion_o="O(n^2)", notacion_omega="Ω(n)", notacion_theta="Θ(n^2)",
                               justificacion="El algoritmo presenta un bucle externo que depende de la entrada (n) y un bucle interno cuya ejecución, en el peor de los casos, también depende de n, resultando en una complejidad cuadrática.")
        elif bucles:
            print("-> Se detectó un único nivel de bucles.")
            return Complejidad(id=1, notacion_o="O(n)", notacion_omega="Ω(n)", notacion_theta="Θ(n)",
                               justificacion="El algoritmo contiene un bucle principal que itera sobre el tamaño de la entrada, lo que resulta en una complejidad lineal.")
        else:
            return Complejidad(id=1, notacion_o="O(1)", notacion_omega="Ω(1)", notacion_theta="Θ(1)",
                               justificacion="El algoritmo no contiene bucles ni llamadas recursivas, por lo que su tiempo de ejecución es constante.")


# --- INICIO DEL FLUJO DE LA APLICACIÓN ---

def ejecutar_analisis_completo():
    # 1. Cargar configuración e inicializar servicios
    load_dotenv()
    try:
        grammar = Grammar()
        llm_service = LLMService()  # Ya no necesita el path del libro
        parser = Parser(id=1, gramatica=grammar, llm_service=llm_service)
        analysis_service = MockAnalysisService()  # Usamos nuestro mock por ahora
    except Exception as e:
        print(f"❌ Error fatal al inicializar los servicios: {e}")
        return

    # 2. Simular entrada de un usuario
    pseudocodigo = """
    INSERTION-SORT(A)
        // Ordena un arreglo A de n números
        for j ← 2 to A.length do
            key ← A[j]
            i ← j - 1
            while i > 0 and A[i] > key do
                A[i+1] ← A[i]
                i ← i - 1
            A[i+1] ← key
    """
    print("--- [PASO 0] Analizando el siguiente Pseudocódigo ---")
    print(pseudocodigo)

    # 3. Usar el Parser para obtener el AST (valida y traduce internamente)
    try:
        print("\n--- [PASO 1 & 2] Ejecutando el Parser (Validación y Traducción)... ---")
        ast = parser.parsear(pseudocodigo)
    except (SyntaxError, ConnectionError) as e:
        print(f"❌ ERROR en el proceso de parsing: {e}")
        return

    # 4. Usar el AnalysisService para calcular la complejidad
    resultado_complejidad = analysis_service.analizar(ast)

    # 5. Crear los modelos de datos para el reporte final
    usuario = Usuario(id=1, nombre="dsalazardev")
    algoritmo = Algoritmo(id=1, codigo_fuente=pseudocodigo, tipo_algoritmo=TipoAlgoritmo.ITERATIVO)

    usuario.addAlgoritmo(algoritmo)
    algoritmo.addUsuario(usuario)

    algoritmo.addAST(ast)

    reporte = Reporte(id=1, algoritmo_analizado=algoritmo, resultado_complejidad=resultado_complejidad)

    # 6. (Opcional) Usar el LLMService para una segunda opinión
    print("\n[PASO 4] Solicitando validación del análisis a la IA...")
    validacion_ia = llm_service.validar_analisis(resultado_complejidad, pseudocodigo)
    reporte.validacion_llm = validacion_ia

    # 7. Imprimir el reporte final
    print("\n" + "=" * 50)
    print("📊 REPORTE FINAL DE EFFI-CODE ANALYZER")
    print("=" * 50)
    print(f"\n👤 Usuario: {usuario.nombre}")
    print(f"\n📄 Algoritmo Analizado:\n{reporte.algoritmo_analizado.codigo_fuente}")
    print("\n--- 🧠 Complejidad Calculada ---")
    print(f"  - Peor Caso (O): {reporte.resultado_complejidad.notacion_o}")
    print(f"  - Mejor Caso (Ω): {reporte.resultado_complejidad.notacion_omega}")
    print(f"  - Caso Promedio (Θ): {reporte.resultado_complejidad.notacion_theta}")
    print(f"\nJustificación Técnica:\n{reporte.resultado_complejidad.justificacion_matematica}")
    print("\n--- 🤖 Validación por IA (Segunda Opinión) ---")
    print(reporte.validacion_llm)
    print("=" * 50)


    # Traer el algoritmo que el usuario
    for alg in usuario.algoritmos:
        print(f"Algoritmo ID: {alg.id}, Tipo: {alg.tipo_algoritmo}, Código:\n{alg.codigo_fuente}")

    print("=" * 50)

    usuario = algoritmo.usuario
    ast = algoritmo.arbol_sintactico

    print(f"El algoritmo pertenece al usuario: {usuario.nombre}")
    print(f"AST: {ast.to_dict()}")



if __name__ == "__main__":
    ejecutar_analisis_completo()