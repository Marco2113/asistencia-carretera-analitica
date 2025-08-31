📊 Asistencia en Carretera – Análisis y Optimización de Costes








🚗 Descripción

Proyecto de analítica de datos aplicada a operaciones de asistencia en carretera, usando un dataset sintético que simula incidencias reales (averías, accidentes, retornos en taxi o grúa).

El objetivo es mostrar habilidades prácticas en Data Analytics:

Creación de datasets simulados y limpios.

Exploratory Data Analysis (Python, Pandas, Matplotlib).

Dashboards interactivos en Power BI.

App desplegada en Streamlit Cloud para visualización dinámica.

Este proyecto forma parte de mi portfolio como Data Analyst Junior.

📂 Estructura del Proyecto
asistencia-carretera-analitica/
│
├── incidencias_asistencia_carretera.csv   # Dataset sintético (900 registros)
├── diccionario_datos_incidencias.csv      # Glosario de campos
├── EDA_incidencias.ipynb                  # Exploratory Data Analysis en Python
├── app_streamlit_incidencias.py           # Aplicación Streamlit
├── requirements.txt                       # Dependencias mínimas para Streamlit
├── README.md                              # Este documento

📑 Dataset Sintético

Filas: 900 (1 año de datos, ago-2024 → ago-2025)

Columnas clave:

Fecha, Ciudad, Tipo_Incidencia, Tiempo_Respuesta_min, Costo_EUR, Medio_Retorno

SLA de 45 min, coste asociado, satisfacción cliente (1–5).

Ejemplo:

Fecha	Ciudad	Tipo_Incidencia	Tiempo_Respuesta_min	Costo_EUR	Medio_Retorno	SLA_45min_Incumplido
2025-08-25	Madrid	Batería	42.5	60.2	Taxi	No
2025-08-25	Oviedo	Motor	88.1	150.7	Grúa	Sí
📊 KPIs Principales

Tiempo medio de respuesta: 38.5 min

SLA 45 min incumplido: 30 %

Coste medio por incidencia: 82 €

Satisfacción cliente: 4.2 / 5

Top incidencias: Neumático (26 %), Batería (23 %)

📈 Dashboard Power BI

Incluye:

Página 1 – KPI Ejecutivo: métricas clave (tiempo, coste, SLA).

Página 2 – Geografía: mapa por ciudad con incidencias.

Página 3 – Operaciones: costes por medio de retorno y tipo de incidencia.

Página 4 – Tendencias: evolución mensual.

(📌 Captura pendiente de añadir cuando lo tengas montado en Power BI.)

🌐 Demo Interactiva – Streamlit

👉 Abrir App en Streamlit Cloud
 (pondrás el link cuando la despliegues)

La app permite:

Filtrar por ciudad, tipo de incidencia, medio de retorno.

Visualizar KPIs dinámicos.

Explorar tablas y costes medios.

🛠️ Tecnologías

Lenguaje: Python (Pandas, Matplotlib, Numpy)

Visualización: Power BI, Streamlit

Infraestructura: Streamlit Cloud, GitHub

Otros: EDA con Jupyter Notebook

🚀 Cómo ejecutar localmente
# Clonar repo
git clone https://github.com/Marco2113/asistencia-carretera-analitica.git
cd asistencia-carretera-analitica

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar app Streamlit
streamlit run app_streamlit_incidencias.py

📌 Autor

👤 Marco Adrian

GitHub

LinkedIn

Coste Medio = AVERAGE('incidencias'[Costo_EUR])
