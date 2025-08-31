Asistencia en Carretera – Análisis y Optimización de Costes
Proyecto de analítica aplicado a operaciones de asistencia en carretera. Incluye dataset sintético, notebook/EDA (pendiente), dashboard (Power BI) y app en Streamlit.

Objetivos
Visualizar incidencias por ciudad/tipo y tiempos de respuesta
Medir cumplimiento de SLA 45 min
Analizar costes por medio de retorno (Taxi/Grúa/Retorno Domicilio)
Identificar oportunidades de ahorro
Datasets
incidencias_asistencia_carretera.csv – 900 filas, 2024-08-31 a 2025-08-30
diccionario_datos_incidencias.csv – glosario de campos
KPIs sugeridos
Tiempo medio de respuesta
% SLA 45 min incumplido
Coste medio por incidente
% Resueltos
Satisfacción media (1-5)
Visualizaciones Power BI
Mapa por ciudad (conteo de incidencias)
Barras: coste medio por Tipo_Incidencia y por Medio_Retorno
Línea temporal: incidencias por mes
Boxplot (Power BI Visuals) de Tiempo_Respuesta por ciudad
DAX (ejemplos)
Incidencias = COUNTROWS('incidencias')

SLA Incumplido % = 
DIVIDE(CALCULATE(COUNTROWS('incidencias'), 'incidencias'[SLA_45min_Incumplido] = "Sí"), [Incidencias])

Tiempo Medio Respuesta = AVERAGE('incidencias'[Tiempo_Respuesta_min])

Coste Medio = AVERAGE('incidencias'[Costo_EUR])
