# 🚗 Asistencia Carretera - Analítica de Incidencias  

## 📌 Introducción  

Este proyecto está inspirado en mi experiencia profesional en **asistencia en carretera**, donde gestiono incidencias de vehículos, tiempos de respuesta, costes y medios de retorno al domicilio de los clientes.  

Con el objetivo de aplicar un flujo completo de análisis de datos (**ETL → EDA → Estadística → Dashboarding**), he creado un **dataset sintético** basado en patrones reales de mi trabajo, asegurando confidencialidad y anonimato.  

De esta forma, el proyecto combina:  
- **Contexto realista de negocio** (tiempos de respuesta, SLA 45 min, costes, satisfacción, resolución de incidencias).  
- **Buenas prácticas analíticas** (limpieza, transformación y exploración de datos).  
- **Visualización profesional** mediante dashboards en Power BI.  

El resultado muestra cómo datos operativos del día a día pueden convertirse en **información estratégica** para mejorar la toma de decisiones en la empresa.  

---

## 🎯 Objetivos  

- Aplicar un proceso **ETL** sobre un conjunto de datos realista.  
- Realizar un **análisis exploratorio (EDA)**.  
- Generar **estadísticas descriptivas e inferenciales**.  
- Crear **dashboards interactivos** en Power BI.  
- Mantener un repositorio organizado y reproducible.  

---

## 📂 Estructura del Proyecto  
```
asistencia-carretera-analitica/
├── data/
│ ├── raw/ # Dataset original (sintético)
│ └── processed/ # Dataset transformado / limpio
├── notebooks/ # Jupyter notebooks (EDA, pruebas, gráficas)
├── dashboards/ # Power BI (.pbix) o exportaciones
├── src/ # Scripts Python
│ ├── etl.py # Extracción y transformación de datos
│ ├── eda.py # Análisis exploratorio
│ └── stats.py # Estadística descriptiva e inferencial
├── requirements.txt # Dependencias
├── README.md # Documentación principal   
└── .gitignore
```

---

## 🔎 Preguntas de Investigación  

1. ¿Qué factores impactan en el cumplimiento del **SLA de 45 minutos**?  
2. ¿Cuál es el **costo promedio por tipo de incidencia** y medio de retorno?  
3. ¿Qué ciudades concentran el mayor número de incidencias?  
4. ¿Existen patrones temporales (mensuales, diarios) en la ocurrencia de incidencias?  
5. ¿Qué variables están más asociadas con la **satisfacción del cliente**?  

---

## ⚙️ Metodología  

1. **ETL (Extracción, Transformación y Carga)**  
   - Normalización de fechas y coordenadas.  
   - Limpieza de valores nulos e inconsistencias.  
   - Generación de dataset procesado.  

2. **EDA (Exploratory Data Analysis)**  
   - Distribución de tiempos de respuesta y costes.  
   - Detección de outliers.  
   - Segmentación por ciudad, tipo de incidencia y medio de retorno.  

3. **Estadística**  
   - Medias, medianas, desviaciones estándar.  
   - Correlaciones entre variables (ej: tiempo de respuesta ↔ satisfacción).  
   - Comparaciones por grupos.  

4. **Dashboard en Power BI**  
   - KPIs:  
     - Tiempo medio de respuesta.  
     - % SLA 45 min incumplido.  
     - Coste medio (€).  
     - Satisfacción media (1-5).  
     - % incidencias resueltas.  
   - Visualizaciones:  
     - **Mapa** por ciudad (conteo de incidencias).  
     - **Barras**: coste medio por tipo de incidencia y medio de retorno.  
     - **Línea temporal**: incidencias por mes.  
     - **Boxplot**: tiempo de respuesta por ciudad.  

---

## 📊 Resultados Esperados  

- Un **dataset limpio y documentado** (CSV).  
- Notebooks con análisis y visualizaciones.  
- Dashboard interactivo en Power BI.  
- README completo para guiar la reproducción del proyecto.  

---

## 🚀 Reproducibilidad  

Clonar el repositorio:  

```bash
git clone https://github.com/Marco2113/asistencia-carretera-analitica.git
cd asistencia-carretera-analitica

Instalar dependencias:

pip install -r requirements.txt

Ejecutar scripts:

python src/etl.py
python src/eda.py
python src/stats.py

Abrir el dashboard en Power BI desde /dashboards/

👤 Autor

Marco Adrian

GitHub

LinkedIn

Coste Medio = AVERAGE('incidencias'[Costo_EUR])
