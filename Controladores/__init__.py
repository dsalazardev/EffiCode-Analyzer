"""
Módulo de Controladores.

Los controladores actúan como intermediarios entre la capa de presentación
(API REST, CLI, GUI) y la capa de servicios. Orquestan el flujo de la
aplicación sin conocer detalles de la interfaz de usuario.

Patrón arquitectónico: MVC (Model-View-Controller)
"""

from .AnalisisController import AnalisisController, ResultadoAnalisis, crear_controlador_analisis

__all__ = [
    'AnalisisController',
    'ResultadoAnalisis', 
    'crear_controlador_analisis'
]