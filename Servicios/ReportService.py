"""
Servicio de generación de reportes en PDF y JSON.
Genera reportes completos del análisis de complejidad algorítmica.
"""
import json
import io
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
        Image, PageBreak, ListFlowable, ListItem
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ reportlab no disponible. Instale con: pip install reportlab")


class ReportService:
    """
    Servicio para generar reportes de análisis de complejidad.
    Soporta exportación a PDF y JSON.
    """
    
    def __init__(self):
        self._styles = None
        if REPORTLAB_AVAILABLE:
            self._init_styles()
    
    def _init_styles(self):
        """Inicializa los estilos para el PDF."""
        self._styles = getSampleStyleSheet()
        
        # Estilo para título principal
        self._styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self._styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a1a2e')
        ))
        
        # Estilo para subtítulos de sección
        self._styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self._styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#16213e')
        ))
        
        # Estilo para subtítulos menores
        self._styles.add(ParagraphStyle(
            name='SubSection',
            parent=self._styles['Heading3'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=8,
            textColor=colors.HexColor('#0f3460')
        ))
        
        # Estilo para texto normal
        self._styles.add(ParagraphStyle(
            name='BodyText',
            parent=self._styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        # Estilo para código
        self._styles.add(ParagraphStyle(
            name='Code',
            parent=self._styles['Normal'],
            fontName='Courier',
            fontSize=9,
            spaceAfter=6,
            backColor=colors.HexColor('#f5f5f5'),
            leftIndent=10,
            rightIndent=10
        ))
        
        # Estilo para fórmulas matemáticas
        self._styles.add(ParagraphStyle(
            name='Formula',
            parent=self._styles['Normal'],
            fontName='Courier',
            fontSize=11,
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=10,
            textColor=colors.HexColor('#1565c0')
        ))
        
        # Estilo para el pie de página
        self._styles.add(ParagraphStyle(
            name='Footer',
            parent=self._styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey
        ))
    
    def generar_json(self, analysis_data: Dict[str, Any], pseudocode: str) -> Dict[str, Any]:
        """
        Genera un reporte completo en formato JSON.
        
        Args:
            analysis_data: Datos del análisis de complejidad
            pseudocode: Código fuente analizado
            
        Returns:
            Diccionario con el reporte completo
        """
        # Extraer datos de complejidad
        complexity = analysis_data.get('complexity', {})
        justification_data = analysis_data.get('justification', {})
        
        report = {
            "metadata": {
                "titulo": "Reporte de Análisis de Complejidad Algorítmica",
                "generado_por": "EffiCode Analyzer",
                "fecha_generacion": datetime.now().isoformat(),
                "version": "1.0.0"
            },
            "algoritmo": {
                "codigo_fuente": pseudocode,
                "tipo": "Iterativo"  # Se puede detectar automáticamente
            },
            "complejidad": {
                "peor_caso": {
                    "notacion": complexity.get('bigO', 'N/A'),
                    "descripcion": "Cota superior asintótica - máximo tiempo de ejecución"
                },
                "mejor_caso": {
                    "notacion": complexity.get('bigOmega', 'N/A'),
                    "descripcion": "Cota inferior asintótica - mínimo tiempo de ejecución"
                },
                "caso_ajustado": {
                    "notacion": complexity.get('bigTheta', 'No aplicable'),
                    "descripcion": "Cota ajustada - cuando peor y mejor caso coinciden"
                },
                "caso_promedio": {
                    "notacion": complexity.get('averageCase', 'N/A'),
                    "descripcion": "Tiempo esperado bajo distribución uniforme de entradas"
                }
            },
            "analisis_matematico": {
                "funcion_peor_caso": justification_data.get('worst_case_function', 'N/A'),
                "funcion_mejor_caso": justification_data.get('best_case_function', 'N/A'),
                "costos_por_linea": justification_data.get('line_costs', []),
                "pasos_resolucion": {
                    "peor_caso": self._formatear_pasos(
                        justification_data.get('resolution_steps', {}).get('worst_case', [])
                    ),
                    "mejor_caso": self._formatear_pasos(
                        justification_data.get('resolution_steps', {}).get('best_case', [])
                    ),
                    "caso_promedio": self._formatear_pasos(
                        justification_data.get('resolution_steps', {}).get('average_case', [])
                    )
                }
            },
            "conclusion": justification_data.get('conclusion', {}),
            "validacion_ia": analysis_data.get('validation', 'No disponible')
        }
        
        return report
    
    def _formatear_pasos(self, pasos: list) -> list:
        """Formatea los pasos de resolución para el JSON."""
        pasos_formateados = []
        for paso in pasos:
            pasos_formateados.append({
                "numero": paso.get('step', 0),
                "titulo": paso.get('title', ''),
                "descripcion": paso.get('description', ''),
                "formula_latex": paso.get('latex', ''),
                "explicacion": paso.get('explanation', '')
            })
        return pasos_formateados
    
    def generar_pdf(self, analysis_data: Dict[str, Any], pseudocode: str) -> bytes:
        """
        Genera un reporte completo en formato PDF.
        
        Args:
            analysis_data: Datos del análisis de complejidad
            pseudocode: Código fuente analizado
            
        Returns:
            Bytes del archivo PDF generado
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab no está instalado. Ejecute: pip install reportlab")
        
        # Buffer para el PDF
        buffer = io.BytesIO()
        
        # Crear documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Contenido del documento
        story = []
        
        # === PORTADA ===
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(
            "📊 Reporte de Análisis de Complejidad",
            self._styles['MainTitle']
        ))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            "EffiCode Analyzer",
            self._styles['SectionTitle']
        ))
        story.append(Spacer(1, 0.5*inch))
        
        # Fecha de generación
        fecha = datetime.now().strftime("%d de %B de %Y, %H:%M")
        story.append(Paragraph(
            f"<b>Fecha de generación:</b> {fecha}",
            self._styles['BodyText']
        ))
        story.append(Spacer(1, 1*inch))
        
        # === SECCIÓN 1: CÓDIGO FUENTE ===
        story.append(Paragraph("1. Código Fuente Analizado", self._styles['SectionTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Mostrar código línea por línea
        for line in pseudocode.split('\n'):
            story.append(Paragraph(line or "&nbsp;", self._styles['Code']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # === SECCIÓN 2: RESUMEN DE COMPLEJIDAD ===
        story.append(Paragraph("2. Resumen de Complejidad", self._styles['SectionTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Extraer complejidades
        complexity = analysis_data.get('complexity', {})
        
        # Tabla de complejidades
        complexity_data = [
            ['Caso', 'Notación', 'Descripción'],
            ['Peor Caso (O)', complexity.get('bigO', 'N/A'), 'Cota superior asintótica'],
            ['Mejor Caso (Ω)', complexity.get('bigOmega', 'N/A'), 'Cota inferior asintótica'],
            ['Caso Ajustado (Θ)', complexity.get('bigTheta', 'No aplicable'), 'Cota ajustada'],
            ['Caso Promedio E[T(n)]', complexity.get('averageCase', 'N/A'), 'Tiempo esperado']
        ]
        
        complexity_table = Table(complexity_data, colWidths=[1.8*inch, 1.5*inch, 2.5*inch])
        complexity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(complexity_table)
        story.append(Spacer(1, 0.3*inch))
        
        # === SECCIÓN 3: ANÁLISIS DEL PEOR CASO ===
        justification_data = analysis_data.get('justification', {})
        worst_case_steps = justification_data.get('resolution_steps', {}).get('worst_case', [])
        
        if worst_case_steps:
            story.append(Paragraph("3. Análisis del Peor Caso", self._styles['SectionTitle']))
            story.append(Spacer(1, 0.2*inch))
            
            for paso in worst_case_steps:
                story.append(Paragraph(
                    f"<b>Paso {paso.get('step', '?')}:</b> {paso.get('title', '')}",
                    self._styles['SubSection']
                ))
                if paso.get('description'):
                    story.append(Paragraph(paso['description'], self._styles['BodyText']))
                if paso.get('latex'):
                    # Convertir LaTeX a texto legible
                    latex_text = self._latex_to_text(paso['latex'])
                    story.append(Paragraph(f"<font color='#1565c0'>{latex_text}</font>", self._styles['Formula']))
                if paso.get('explanation'):
                    story.append(Paragraph(
                        f"<i>{paso['explanation']}</i>",
                        self._styles['BodyText']
                    ))
                story.append(Spacer(1, 0.1*inch))
        
        # === SECCIÓN 4: ANÁLISIS DEL MEJOR CASO ===
        best_case_steps = justification_data.get('resolution_steps', {}).get('best_case', [])
        
        if best_case_steps:
            story.append(Paragraph("4. Análisis del Mejor Caso", self._styles['SectionTitle']))
            story.append(Spacer(1, 0.2*inch))
            
            for paso in best_case_steps:
                story.append(Paragraph(
                    f"<b>Paso {paso.get('step', '?')}:</b> {paso.get('title', '')}",
                    self._styles['SubSection']
                ))
                if paso.get('description'):
                    story.append(Paragraph(paso['description'], self._styles['BodyText']))
                if paso.get('latex'):
                    latex_text = self._latex_to_text(paso['latex'])
                    story.append(Paragraph(f"<font color='#2e7d32'>{latex_text}</font>", self._styles['Formula']))
                if paso.get('explanation'):
                    story.append(Paragraph(
                        f"<i>{paso['explanation']}</i>",
                        self._styles['BodyText']
                    ))
                story.append(Spacer(1, 0.1*inch))
        
        # === SECCIÓN 5: ANÁLISIS DEL CASO PROMEDIO ===
        average_case_steps = justification_data.get('resolution_steps', {}).get('average_case', [])
        
        if average_case_steps:
            story.append(PageBreak())
            story.append(Paragraph("5. Análisis del Caso Promedio (Cormen Cap. 5)", self._styles['SectionTitle']))
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(
                "Análisis probabilístico usando Variables Aleatorias Indicadoras.",
                self._styles['BodyText']
            ))
            story.append(Spacer(1, 0.1*inch))
            
            for paso in average_case_steps:
                story.append(Paragraph(
                    f"<b>{paso.get('title', '')}:</b>",
                    self._styles['SubSection']
                ))
                if paso.get('description'):
                    story.append(Paragraph(paso['description'], self._styles['BodyText']))
                if paso.get('latex'):
                    latex_text = self._latex_to_text(paso['latex'])
                    story.append(Paragraph(f"<font color='#7b1fa2'>{latex_text}</font>", self._styles['Formula']))
                if paso.get('explanation'):
                    story.append(Paragraph(
                        f"<i>{paso['explanation']}</i>",
                        self._styles['BodyText']
                    ))
                story.append(Spacer(1, 0.1*inch))
        
        # === SECCIÓN 6: COSTOS POR LÍNEA ===
        line_costs = justification_data.get('line_costs', [])
        
        if line_costs:
            story.append(Paragraph("6. Costos por Línea de Código", self._styles['SectionTitle']))
            story.append(Spacer(1, 0.2*inch))
            
            costs_data = [['Línea', 'Código', 'Costo', 'Frecuencia']]
            for cost in line_costs[:15]:  # Limitar a 15 líneas
                costs_data.append([
                    str(cost.get('line', '')),
                    str(cost.get('code', ''))[:40],  # Truncar código largo
                    str(cost.get('cost', '')),
                    str(cost.get('frequency', ''))
                ])
            
            costs_table = Table(costs_data, colWidths=[0.6*inch, 2.8*inch, 1*inch, 1.4*inch])
            costs_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Courier'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ced4da')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 1), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ]))
            story.append(costs_table)
        
        # === PIE DE PÁGINA ===
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            "─" * 60,
            self._styles['Footer']
        ))
        story.append(Paragraph(
            "Generado por EffiCode Analyzer © 2025 - Análisis y Diseño de Algoritmos",
            self._styles['Footer']
        ))
        story.append(Paragraph(
            "Basado en 'Introduction to Algorithms' de Cormen, Leiserson, Rivest y Stein",
            self._styles['Footer']
        ))
        
        # Construir PDF
        doc.build(story)
        
        # Obtener bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _latex_to_text(self, latex: str) -> str:
        """
        Convierte notación LaTeX básica a texto legible.
        Para PDFs, usamos una representación simplificada.
        """
        if not latex:
            return ""
        
        text = latex
        
        # Reemplazos comunes de LaTeX
        replacements = {
            '\\sum': 'Σ',
            '\\Sigma': 'Σ',
            '\\prod': 'Π',
            '\\int': '∫',
            '\\infty': '∞',
            '\\leq': '≤',
            '\\geq': '≥',
            '\\neq': '≠',
            '\\times': '×',
            '\\cdot': '·',
            '\\ldots': '...',
            '\\dots': '...',
            '\\theta': 'θ',
            '\\Theta': 'Θ',
            '\\omega': 'ω',
            '\\Omega': 'Ω',
            '\\alpha': 'α',
            '\\beta': 'β',
            '\\gamma': 'γ',
            '\\delta': 'δ',
            '\\epsilon': 'ε',
            '\\lambda': 'λ',
            '\\mu': 'μ',
            '\\pi': 'π',
            '\\sigma': 'σ',
            '\\rightarrow': '→',
            '\\leftarrow': '←',
            '\\Rightarrow': '⇒',
            '\\Leftarrow': '⇐',
            '\\forall': '∀',
            '\\exists': '∃',
            '\\in': '∈',
            '\\notin': '∉',
            '\\subset': '⊂',
            '\\subseteq': '⊆',
            '\\cup': '∪',
            '\\cap': '∩',
            '\\emptyset': '∅',
            '\\quad': '  ',
            '\\qquad': '    ',
            '\\text': '',
            '\\mathcal': '',
            '\\mathrm': '',
            '\\mathbf': '',
            '\\left': '',
            '\\right': '',
            '\\Big': '',
            '\\big': '',
            '\\boxed': '',
            '\\binom': 'C',
        }
        
        for latex_cmd, replacement in replacements.items():
            text = text.replace(latex_cmd, replacement)
        
        # Limpiar llaves y comandos restantes
        import re
        text = re.sub(r'\{([^}]*)\}', r'\1', text)  # Remover llaves manteniendo contenido
        text = re.sub(r'\\[a-zA-Z]+', '', text)  # Remover comandos restantes
        text = re.sub(r'\s+', ' ', text).strip()  # Limpiar espacios
        
        return text
