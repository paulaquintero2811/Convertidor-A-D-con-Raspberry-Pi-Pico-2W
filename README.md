# Conversión A/D con Raspberry Pi Pico 2 W

## Descripción

En este laboratorio se estudió experimentalmente el proceso de **conversión analógico-digital (A/D)** utilizando una **Raspberry Pi Pico 2 W**, basada en el microcontrolador **RP2350**.

La práctica se dividió en dos partes principales:

* **Proceso de muestreo:** se analizó una señal senoidal conectada a una entrada ADC y se observaron mediante un osciloscopio los pulsos correspondientes a los instantes de muestreo.
* **Análisis estadístico del ADC:** se aplicaron diferentes niveles de tensión DC y se realizaron 10.000 mediciones por cada prueba para analizar la variabilidad, la desviación estándar, los histogramas y la exactitud de las mediciones.

El laboratorio permitió relacionar conceptos como **muestreo, frecuencia de muestreo, cuantización, resolución, repetibilidad y exactitud** con mediciones realizadas sobre un sistema real.

## Objetivo

Comprender los fundamentos de la conversión analógico-digital mediante su observación experimental y analizar su aplicación en la adquisición y procesamiento de señales dentro de un sistema de comunicación digital.

## Hardware utilizado

* Raspberry Pi Pico 2 W
* Microcontrolador RP2350
* Generador de señales
* Osciloscopio
* Fuente de voltaje DC
* Multímetro
* Computador

## Software utilizado

* MicroPython
* Thonny
* MATLAB

## Características del ADC

El RP2350 incorpora un ADC con una resolución nominal de **12 bits**, permitiendo representar **4096 niveles digitales**, desde 0 hasta 4095.

Para la práctica se utilizó una referencia de **3.3 V** y la entrada analógica principal fue:

* **GP26 / ADC0 — Pin 31**
* GP27 / ADC1
* GP28 / ADC2

Además, se utilizó **GP15 — Pin 20** como señal de referencia para indicar los instantes de muestreo.

## Parte 1 — Proceso de muestreo

Para el proceso de muestreo se utilizó una señal senoidal configurada inicialmente con:

* Frecuencia: **100 Hz**
* Voltaje pico a pico: **2 Vpp**
* Offset: **1.65 V**
* Frecuencia de muestreo programada: **1000 Hz**
* Período de muestreo: **1000 µs**
* Número de muestras: **10.000**

La señal se conectó simultáneamente al **GP26/ADC0** de la Raspberry Pi Pico 2 W y al canal 1 del osciloscopio. El **GP15** se conectó al canal 2 para observar los pulsos de muestreo.

### Archivo generado

Durante la adquisición se generó el archivo:

```text
datos.csv
```

Este archivo contiene:

* Número de muestra
* Tiempo de adquisición
* Lectura digital del ADC
* Voltaje estimado

## Resultados del muestreo

La frecuencia de muestreo obtenida experimentalmente con el osciloscopio fue:

**Fs = 1000 Hz**

La frecuencia calculada por el software fue:

**Fs = 1000.02 Hz**

La medición experimental presentó un error de **0 %** respecto al valor nominal.

La frecuencia de la señal senoidal medida mediante el osciloscopio fue aproximadamente:

**Fin = 99.70 Hz**

Con estos valores se obtuvieron aproximadamente:

**10 muestras por período**.

### Cambio de frecuencia de entrada

Manteniendo la frecuencia de muestreo en aproximadamente 1000 Hz, se probaron diferentes frecuencias de entrada:

| Frecuencia configurada | Frecuencia medida | Muestras por período |
| ---------------------: | ----------------: | -------------------: |
|                 100 Hz |          99.70 Hz |                10.03 |
|                 200 Hz |          199.8 Hz |                    5 |
|                 250 Hz |            250 Hz |                    4 |
|                 400 Hz |          401.6 Hz |                 2.49 |

Se observó que, al aumentar la frecuencia de la señal mientras se mantiene constante la frecuencia de muestreo, disminuye la cantidad de muestras disponibles para representar cada período.

## Parte 2 — Análisis estadístico del ADC

Para esta parte se utilizaron cinco niveles diferentes de tensión DC, realizando **10.000 mediciones por cada prueba**.

Los resultados obtenidos fueron:

| Test |    VDMM | VADC promedio | Desviación estándar |
| ---- | ------: | ------------: | ------------------: |
| 1    | 0.605 V |    0.606066 V |            7.215 mV |
| 2    | 1.611 V |    1.603018 V |            7.266 mV |
| 3    | 2.088 V |    2.076866 V |            7.626 mV |
| 4    | 2.605 V |    2.596864 V |            7.602 mV |
| 5    | 3.172 V |    3.150838 V |            7.899 mV |

Para cada prueba se generaron archivos con las muestras y los histogramas correspondientes.

### Archivos generados

```text
samples_test_1.csv
samples_test_2.csv
samples_test_3.csv
samples_test_4.csv
samples_test_5.csv

histogram_test_1.csv
histogram_test_2.csv
histogram_test_3.csv
histogram_test_4.csv
histogram_test_5.csv
```

Posteriormente, los datos fueron procesados mediante MATLAB para calcular nuevamente la media y la desviación estándar y comparar los resultados con los obtenidos directamente durante la adquisición.

## Análisis de resultados

Los resultados mostraron que las mediciones del ADC presentan cierta dispersión incluso cuando se aplica una tensión DC aproximadamente constante.

La desviación estándar obtenida estuvo entre:

**7.215 mV y 7.899 mV**

Además, se encontraron entre **110 y 135 códigos ADC diferentes** en las cinco pruebas. Esto demuestra que una tensión constante no necesariamente produce exactamente el mismo código digital en todas las mediciones.

Al comparar las mediciones promedio del ADC con el multímetro, los errores relativos fueron inferiores al **1 %** en todos los casos. El mayor error fue de aproximadamente **0.667 %**, correspondiente al Test 5.

Para un ADC ideal de 12 bits con una referencia de 3.3 V, el informe obtuvo un tamaño de LSB de aproximadamente:

**LSB = 0.806 mV**

La desviación estándar experimental correspondió aproximadamente a **9 LSB**, por lo que las variaciones observadas no pueden explicarse únicamente por la cuantización ideal.

## Conclusiones

La práctica permitió comprobar experimentalmente el funcionamiento de un convertidor analógico-digital utilizando la Raspberry Pi Pico 2 W.

Se comprobó que la frecuencia de muestreo programada de **1000 Hz** coincidió prácticamente con la frecuencia medida mediante el osciloscopio y que, al aumentar la frecuencia de la señal de entrada, disminuye el número de muestras disponibles por período.

En el análisis estadístico se observó que las mediciones del ADC presentan pequeñas variaciones incluso para una tensión DC constante. Sin embargo, los valores promedio mostraron una buena aproximación respecto al multímetro, con errores inferiores al 1 %.

Finalmente, se pudo diferenciar entre **repetibilidad y exactitud**: las mediciones presentaron una dispersión relativamente estable, indicando buena repetibilidad, pero los valores promedio no coincidieron exactamente con la referencia del multímetro.

```

## Autores

**Paula Quintero**
**Ediem Valero**

Universidad Militar Nueva Granada
Ingeniería de Telecomunicaciones
Comunicación Digital
Bogotá, Colombia — 2026
