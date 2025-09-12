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
│   ├── raw/                      # Dataset original (sintético)
│   └── processed/                # Dataset transformado / limpio
├── notebooks/                    # Jupyter notebooks (EDA, limpieza, pruebas)
│   ├── eda.ipynb                 # EDA (gráficos, exploración)
│   ├── etl.ipynb                 # ETL (versión notebook)
│   └── stats.ipynb               # Estadística (versión notebook)
├── dashboards/                   # Power BI (.pbix) o exportaciones
│   ├── dashboard_asistencia.pbix
│   ├── dashboard_asistencia.pdf                
├── src/                          # Scripts Python
│   ├── __init__.py               # Hace que src sea un paquete importable
│   ├── etl.py                    # Extracción y transformación de datos
│   ├── eda.py                    # EDA reproducible (figuras y mapas)
│   └── stats.py                  # Estadística descriptiva e inferencial
├── reports/
│   ├── figs/                     # Figuras generadas (PNG)
│   ├── mapas/                    # Mapas (HTML, folium)
│   └── stats/                    # Resultados estadísticos (CSV)
├── requirements.txt              # Dependencias (versionadas)
├── README.md                     # Documentación principal
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
   - Segmentación por ciudad, proveedor y tipo de incidencia.  
   - Series temporales y mapas.

3. **Estadística**  
   - ANOVA/Kruskal para costes por tipo.
   - χ² de independencia (Tipo_Incidencia × SLA).
   - Regresión logística sin fuga para incumplimiento del SLA. 

4. **📊 Dashboard en Power BI**  

El análisis culmina con un **dashboard interactivo en Power BI**, diseñado para responder de forma visual y rápida a las preguntas de negocio:  

### KPIs principales
- ⚡ **Incidencias Totales**  
- ⏱️ **% Incumplimiento SLA (45 min)**  
- 🕑 **Tiempo Medio de Respuesta** y **Percentil 95**  
- 💰 **Costo Medio (€)** y **Costo Total (€)**  
- ⭐ **Satisfacción Media (1–5)**  
- (Opcional) 🔮 **Probabilidad Media de Incumplir (modelo logístico)**  

### Visualizaciones clave
- **Mapa interactivo** con distribución de incidencias por ciudad.  
- **Gráfico de barras**: coste medio por tipo de incidencia y proveedor.  
- **Serie temporal**: evolución de incidencias por mes.  
- **Boxplot**: tiempo de respuesta por ciudad.  
- **Gráfico circular**: % SLA cumplido vs incumplido.  
 

---
´´´
📦 Datos y Supuestos (Data Dictionary)

Campos principales (entrada cruda):

| Campo                  | Tipo     | Descripción / Unidad                |
| ---------------------- | -------- | ----------------------------------- |
| `Id_Incidente`         | int      | Identificador del incidente         |
| `Fecha`                | date str | Fecha (`YYYY-MM-DD`)                |
| `Hora`                 | time str | Hora (`HH:MM` o `HH:MM:SS`)         |
| `Ciudad`               | str      | Ciudad                              |
| `Latitud`, `Longitud`  | float    | Coordenadas geográficas             |
| `Tipo_Incidencia`      | str      | Categoría del incidente             |
| `Tipo_Vehiculo`        | str      | Categoría del vehículo              |
| `Proveedor`            | str      | Proveedor que atiende               |
| `Distancia_km`         | float    | Distancia recorrida (km)            |
| `Tiempo_Respuesta_min` | float    | Tiempo de respuesta (minutos)       |
| `Medio_Retorno`        | str      | Medio de retorno                    |
| `Costo_EUR`            | float    | Coste del servicio (€)              |
| `Resuelto`             | str      | “Sí”/“No”                           |
| `SLA_45min_Incumplido` | str      | “Sí”/“No” si está presente en crudo |
| `Satisfaccion_1a5`     | float    | Satisfacción del cliente (1–5)      |
| `Notas`                | str/NaN  | Eliminada en ETL                    |

Campos derivados (ETL):

| Campo                 | Tipo     | Descripción                                                                                                                                                                                         |
| --------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Fecha_Hora`          | datetime | Ensamblado de `Fecha` + `Hora` cuando aplica                                                                                                                                                        |
| `SLA_Incumplido`      | Int64    | **Objetivo binario**: 1=incumple, 0=cumple. Si `SLA_45min_Incumplido` existe, se mapea “Sí/No”→1/0 (normalizando tildes y espacios). Si **no** existe, se calcula como `Tiempo_Respuesta_min > 45`. |
| `Anio`, `MesN`, `Mes` | int/str  | Año, número de mes y nombre de mes (español)                                                                                                                                                        |


Supuestos clave:
- SLA incumplido si Tiempo_Respuesta_min > 45.
- Normalización textual para evitar duplicados (p. ej., “Sí” ≡ “si”).
- Notas se descarta del dataset analítico.


## 📊 Resultados Esperados  

- Un **dataset limpio y documentado** (CSV).  
- Notebooks con análisis y visualizaciones.  
- Dashboard interactivo en Power BI.  
- README completo para guiar la reproducción del proyecto.  

### Ejemplo de dashboard
![Dashboard Power BI](reports/figs/dashboard_example.png)  

📂 El archivo completo está en la carpeta [`/dashboards`](dashboards/dashboard_asistencia)


El dashboard completo está disponible en formato PDF:  

[📄 Ver Dashboard (PDF)](dashboards/dashboard_asistencia.pdf)  


---

## 🚀 Reproducibilidad  

Clonar el repositorio:  

```bash
git clone https://github.com/Marco2113/asistencia-carretera-analitica.git
cd asistencia-carretera-analitica
```

Instalar dependencias:

````
pip install -r requirements.txt
````

Ejecutar scripts:
 
 ````
python src/etl.py
python src/eda.py
python src/stats.py
````

Abrir el dashboard en Power BI desde /dashboards/

👤 Autor  

**Marco Adrian**  

- [GitHub](https://github.com/Marco2113)  
- [LinkedIn](https://www.linkedin.com/in/marco-adrian-5b1bb4279/)  

