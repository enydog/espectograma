import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
from fitparse import FitFile
from pandas.plotting import autocorrelation_plot
import pandas as pd
import matplotlib.dates as mdates
from datetime import datetime, timedelta

"""
Cómo observar e interpretar el espectrograma

1. **Eje X (Tiempo):** Representa el tiempo durante el cual se registraron los datos 
   de potencia. Está etiquetado en formato hh:mm:ss para facilitar la identificación 
   de eventos específicos en el tiempo.

2. **Eje Y (Frecuencia):** Representa las frecuencias presentes en la señal de potencia. 
   Está escalado logarítmicamente y muestra desde frecuencias muy bajas hasta más altas. 
   Las frecuencias bajas indican cambios lentos en la potencia, mientras que las 
   frecuencias altas indican cambios rápidos.

3. **Colores (Densidad de Potencia):** La intensidad del color en cada punto del espectrograma 
   indica la densidad de potencia en esa frecuencia y tiempo específicos. Colores más brillantes 
   (amarillo) representan mayor densidad de potencia, indicando momentos de alta intensidad en 
   la señal.

4. **Zonas de Esfuerzos Altos:** Las áreas contorneadas en rojo destacan zonas donde la densidad 
   de potencia supera el umbral del percentil 95, indicando esfuerzos significativamente altos.

5. **Curva de Autocorrelación:** Superpuesta al espectrograma en el mismo gráfico, la curva de 
   autocorrelación (en color blanco) muestra la relación entre los valores de potencia a diferentes 
   retardos. Esto puede ayudar a identificar patrones repetitivos y la regularidad de los esfuerzos.

Para una interpretación detallada, busca patrones en las áreas de alta densidad de potencia, 
observa la distribución temporal de los esfuerzos y utiliza la autocorrelación para identificar 
ciclos y repeticiones en los datos de potencia. Esta información puede ser valiosa para optimizar 
entrenamientos y estrategias de carrera.
"""


# Cargar el archivo .FIT y extraer el campo "power"
def extract_power_from_fit(file_path):
    fitfile = FitFile(file_path)
    power_data = []

    for record in fitfile.get_messages('record'):
        for data in record:
            if data.name == 'power' and data.value is not None:
                power_data.append(data.value)
    
    return power_data

# Ruta al archivo .FIT
fit_file_path = 'hit.fit'  # Reemplaza con la ruta correcta al archivo .FIT

# Extraer los datos de potencia
power = extract_power_from_fit(fit_file_path)

# Convertir la lista de datos de potencia a un numpy array
power = np.array(power)

# Generar el espectrograma con una ventana más pequeña para mejorar la resolución
f, t, Sxx = spectrogram(power, fs=1, nperseg=256, noverlap=128)  # Ajustar nperseg y noverlap para mejorar la resolución

# Convertir el tiempo a formato datetime
start_time = datetime(1, 1, 1)
time_in_seconds = t
time_in_hhmmss = [start_time + timedelta(seconds=sec) for sec in time_in_seconds]

plt.figure(figsize=(14, 7))
plt.pcolormesh(time_in_hhmmss, f, Sxx, shading='gouraud')
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time (hh:mm:ss)')
plt.title('Spectrogram of Instantaneous Power with High Efforts Highlighted')
plt.colorbar(label='Power Density')

# Ajustar la escala de color para resaltar detalles
plt.clim(0, np.percentile(Sxx, 95))  # Escala de color hasta el percentil 95 para resaltar más detalles

# Mejorar la escala Y para que sea logarítmica
plt.yscale('log')
plt.ylim([0.1, 0.2])  # Ajustar los límites del eje Y para reducir el área blanca

# Formato del eje X
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
plt.gcf().autofmt_xdate()

# Resaltar las zonas de esfuerzos altos
threshold = np.percentile(Sxx, 95)  # Umbral del percentil 95
high_efforts = Sxx >= threshold
plt.contour(time_in_hhmmss, f, high_efforts, colors='red', linewidths=0.5)

plt.show()

# Agregar el gráfico de autocorrelación
plt.figure(figsize=(10, 6))
autocorrelation_plot(pd.Series(power))
plt.title('Autocorrelation of Instantaneous Power')
plt.show()