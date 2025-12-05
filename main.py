from dotenv import load_dotenv
import json
import pydot
from graphviz import Source

from Servicios.Grammar import Grammar
from Servicios.LLMService import LLMService

from Modelos.Algoritmo import Algoritmo
from Enumerations.tipoAlgoritmo import TipoAlgoritmo
from Modelos.Reporte import Reporte
from Modelos.Parser import Parser
from Modelos.Analizador import Analizador

def ejecutar_analisis_completo():
    print("--- [PASO 0] Inicializando servicios de EffiCode Analyzer ---")
    load_dotenv()
    try:
        grammar = Grammar()
        llm_service = LLMService()
        parser = Parser(id=1, gramatica=grammar, llm_service=llm_service)
        analizador = Analizador(id=1, parser=parser, llm_service=llm_service)
        print("Servicios inicializados correctamente.")
    except Exception as e:
        print(f"Error fatal al inicializar los servicios: {e}")
        return

    '''pseudocodigo =  """
    MERGE-SORT(A, p, r)
        if p < r then
            q ← (p + r) div 2 
            MERGE-SORT(A, p, q)
            MERGE-SORT(A, q + 1, r)
            MERGE(A, p, q, r)
    """'''

    '''pseudocodigo = """
        BINARY-SEARCH(A, low, high, x)
            if low > high then
                return NIL
            mid ← floor((low + high) / 2)
            if x = A[mid] then
                return mid
            else if x < A[mid] then
                return BINARY-SEARCH(A, low, mid - 1, x)
            else
                return BINARY-SEARCH(A, mid + 1, high, x)
    """'''

    '''pseudocodigo = """
    FACTORIAL(n)
        if n = 0 then
            return 1
        else
            return n * FACTORIAL(n - 1)
    """'''

    '''pseudocodigo = """
    FIBONACCI(n)
        if n ≤ 1 then
            return n
        return FIBONACCI(n-1) + FIBONACCI(n-2)
    """'''

    '''pseudocodigo = """
    HANOI(n, origen, auxiliar, destino)
        if n = 1 then
            mover(origen, destino)           
        else
            HANOI(n-1, origen, destino, auxiliar)
            mover(origen, destino)           
            HANOI(n-1, auxiliar, origen, destino)
    """'''

    '''pseudocodigo = """
    LINEAR-SEARCH(A, x)
        for i ← 1 to A.length do
            if A[i] = x then
                return i
        return NIL
    """'''

    pseudocodigo = """
    INSERTION-SORT(A, n)
        for j ← 2 to n do
            key ← A[j]
            i ← j - 1
            while i > 0 and A[i] > key do
                A[i+1] ← A[i]
                i ← i - 1
            A[i+1] ← key
    """


    pseudocodigo = """
POWER(x, n)
    if n = 0 then
        return 1
    if n mod 2 = 0 then
        y ← POWER(x, n div 2)
        return y * y
    else
        return x * POWER(x, n - 1)
"""
    print("\n--- [PASO 1] Analizando el siguiente Pseudocódigo ---")
    print(pseudocodigo)

    try:
        print("\n--- [PASO 2] Ejecutando el Parser (Validación y Traducción a AST)... ---")
        ast_obj = parser.parsear(pseudocodigo)
        print("AST generado con éxito.\n")

        print("--- Grafo del algoritmo (estructura JSON) ---")
        print(json.dumps(ast_obj.to_dict(), indent=4))

        algoritmo = Algoritmo(id=1, codigo_fuente=pseudocodigo, tipo_algoritmo=TipoAlgoritmo.RECURSIVO)
        algoritmo.addAST(ast_obj)

        print("\n--- [PASO 2.1] Generando grafo visual del AST... ---")
        generar_grafo_ast(ast_obj)
        print("Grafo visual generado y guardado como 'grafo_ast.png'.")

        print("\n--- [PASO 3] Ejecutando análisis de eficiencia matemática... ---")
        resultado_complejidad = analizador.analizar_recursivo(algoritmo)
        print("Análisis completado.")

        reporte = Reporte(id=1, algoritmo_analizado=algoritmo, resultado_complejidad=resultado_complejidad)

        print("\n--- [PASO 4] Solicitando validación del análisis a la IA... ---")
        validacion_ia = llm_service.validar_analisis(resultado_complejidad, pseudocodigo)
        reporte.validacion_llm = validacion_ia

        imprimir_reporte(reporte)

    except (SyntaxError, ConnectionError, ValueError, RuntimeError) as e:
        print(f"ERROR en el proceso de análisis: {e}")

def generar_grafo_ast(ast_obj):
    """Genera una imagen del grafo del AST de Python usando pydot y graphviz."""
    graph = pydot.Dot("AST", graph_type="digraph", rankdir="TB")

    def agregar_nodo(nodo, padre=None):

        if isinstance(nodo, dict):
            label = nodo.get("_type", str(type(nodo)))
            current_node = pydot.Node(id(nodo), label=label, shape="box", style="rounded,filled", fillcolor="#E3F2FD")
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
            leaf_node = pydot.Node(id(nodo), label=str(nodo), shape="ellipse", fillcolor="#FFF9C4", style="filled")
            graph.add_node(leaf_node)
            if padre:
                graph.add_edge(pydot.Edge(id(padre), id(nodo)))

    agregar_nodo(ast_obj.to_dict() if hasattr(ast_obj, "to_dict") else ast_obj)
    graph.write_png("grafo_ast.png")
    print("Grafo visual generado como 'grafo_ast.png'")

def imprimir_reporte(reporte: Reporte):
    """Función auxiliar para mostrar el reporte de forma clara."""
    print("\n" + "="*70)
    print("REPORTE FINAL DE ANÁLISIS DE COMPLEJIDAD ALGORÍTMICA")
    print("="*70)
    print(f"\nALGORITMO ANALIZADO:\n{reporte.algoritmo_analizado.codigo_fuente}")
    print("\n" + "-"*70)
    print("ANÁLISIS MATEMÁTICO DE EFICIENCIA (Línea por Línea)")
    print("-" * 70)
    print(reporte.resultado_complejidad.justificacion_matematica)
    print("\n" + "-"*70)
    print("CONCLUSIÓN DE COMPLEJIDAD ASINTÓTICA")
    print("-" * 70)
    print(f"  - Peor Caso (Cota Superior): {reporte.resultado_complejidad.notacion_o}")
    print(f"  - Mejor Caso (Cota Inferior): {reporte.resultado_complejidad.notacion_omega}")
    print(f"  - Caso Promedio (Cota Ajustada): {reporte.resultado_complejidad.notacion_theta}")
    print("-" * 70)
    print("\nVALIDACIÓN POR IA (Segunda Opinión Experta)")
    print("-" * 70)
    print(reporte.validacion_llm)
    print("="*70)

if __name__ == "__main__":
    ejecutar_analisis_completo()
