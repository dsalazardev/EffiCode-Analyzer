from dotenv import load_dotenv

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
        print("✅ Servicios inicializados correctamente.")
    except Exception as e:
        print(f"❌ Error fatal al inicializar los servicios: {e}")
        return

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
    print("\n--- [PASO 1] Analizando el siguiente Pseudocódigo ---")
    print(pseudocodigo)

    try:
        print("\n--- [PASO 2] Ejecutando el Parser (Validación y Traducción a AST)... ---")
        ast_obj = parser.parsear(pseudocodigo)
        print("✅ AST generado con éxito.")

        # 4. Crear el objeto Algoritmo y asignarle el AST
        algoritmo = Algoritmo(id=1, codigo_fuente=pseudocodigo, tipo_algoritmo=TipoAlgoritmo.ITERATIVO)
        algoritmo.addAST(ast_obj)

        # 5. ¡Ejecutar el análisis de eficiencia!
        print("\n--- [PASO 3] Ejecutando análisis de eficiencia matemática... ---")
        resultado_complejidad = analizador.analizar(algoritmo)
        print("✅ Análisis completado.")

        reporte = Reporte(id=1, algoritmo_analizado=algoritmo, resultado_complejidad=resultado_complejidad)

        print("\n--- [PASO 4] Solicitando validación del análisis a la IA... ---")
        validacion_ia = llm_service.validar_analisis(resultado_complejidad, pseudocodigo)
        reporte.validacion_llm = validacion_ia
        imprimir_reporte(reporte)

    except (SyntaxError, ConnectionError, ValueError, RuntimeError) as e:
        print(f"❌ ERROR en el proceso de análisis: {e}")


def imprimir_reporte(reporte: Reporte):
    """Función auxiliar para mostrar el reporte de forma clara."""
    print("\n" + "="*70)
    print("📊 REPORTE FINAL DE ANÁLISIS DE COMPLEJIDAD ALGORÍTMICA")
    print("="*70)
    print(f"\n📄 ALGORITMO ANALIZADO:\n{reporte.algoritmo_analizado.codigo_fuente}")
    print("\n" + "-"*70)
    print("🧠 ANÁLISIS MATEMÁTICO DE EFICIENCIA (Línea por Línea)")
    print("-" * 70)
    print(reporte.resultado_complejidad.justificacion_matematica)
    print("\n" + "-"*70)
    print("📈 CONCLUSIÓN DE COMPLEJIDAD ASINTÓTICA")
    print("-" * 70)
    print(f"  - Peor Caso (Cota Superior): {reporte.resultado_complejidad.notacion_o}")
    print(f"  - Mejor Caso (Cota Inferior): {reporte.resultado_complejidad.notacion_omega}")
    print(f"  - Caso Promedio (Cota Ajustada): {reporte.resultado_complejidad.notacion_theta}")
    print("-" * 70)
    print("\n🤖 VALIDACIÓN POR IA (Segunda Opinión Experta)")
    print("-" * 70)
    print(reporte.validacion_llm)
    print("="*70)


if __name__ == "__main__":
    ejecutar_analisis_completo()