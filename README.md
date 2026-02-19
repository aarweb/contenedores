# Investigacion de contadores
Un contador puede tener:
## Identificación del contador
* Numero de serie de fabrica
* Localicacion (latitud, longitud, direccion de instalacion)
* CUPS
* Tipo de contador: (agual, gas, electricidad...)
## Hardware
* Marca (brand)
* Modelo
* Version de firmware
## Metrología
* Constante de energia (K) en la que trabaja el contador.
    > Se usa para saber la sensibilidad del contador, ya que puede 1000 pulsos
    > Ejemplo: 
    >> Si K = 1000, 1000 pulsos son 1kWh
    >> 1 pulso = 1 Wh
* Unidad en la que devuelve un pulso
* Factor multiplicador
* Sentido del flujo (Importación, Exportación)

# Definicion de los campos de los contadores
## Campos globales
* Numero de serie de fábrica
* ID del punto de suministro (CUPS en electricidad o numero de póliza)
* Marca, Modelo y version de firmware
* Latitud, longitud, direccion física
* Tipo de suministro(Agua, Electricidad, Gas)
* Estado del dispositivo (Activo, Averiado, Saboteado)

### Campos unicos de Contadores de Electricidad
* Constante de Energia (K)
* Unidades de Medida (Wh, kWh)
* Sentido del flujo. Energia Importada (consumo) o Exportada (generación solar)
* Factor Multiplicador (Ratio para medidas indirectas)
* Tipo de Red (monofásico, trifásico)

### Campos unicos para contadores de Agua / Gas
* Factor de escala del pulso (Cuanto volumen representa un pulso)
* Unidad de medida (m³)
* Calibre del contador (diametro de la tuberia (15mm, 20mm))
* Caudal Nominal (Qn, es el flujo máximo de trabajo del modelo)


## Campos de los modelos que tendran las lecturas
### Smart meter luz
**energia_activa_kwh**: Energía total consumida desde el inicio, es el valor que aparece en la factura.
* Si en enero la lectura tenia de energia_activa_kwh: 1000 kWh y
* En febrefro tenia 1160 kWh, cobraran 160 kWh.


**energia_reactiva_kvarh**: Energia que no se convierte en trabajo útil (motores, transformadores), se contra en industria.
* Este campo solo hay que que tenerlo en cuenta en fabricas con maquinaria pesada.

**potencaia_activa_kw**: Lo que se esta consumiendo en ese momento.
* Lo que se consume en el momento de la lectura.

**potencia_reactiva_kvar**: potencia reactiva instantánea, puede ser negativa.
* Importante en industrias como fabricas
* Es la energia que necesitamos, para mantener un campo magnetico como para un motor, y devuelves esa misma energia (Teniendo en cuenta las perdidas)

**voltaje_v**: tensión de la red
* Es la presión con la cual nos llega la electricidad (definida por REE con la distribuidora)

**corriente_a**: Amperios en que se están circulando en ese momento
*  Nos inidica, cuanta cantidad de electricidad está circulando por los cambles del lugar en ese momento

**frecuencia_hz**: frecuencia de la red eléctrica
* Es la frecuencia con la que va y viene la electricidad en nuestro hogar (Este valor lo define REE)

### Smart meter agua
**volumen_acumulado_m3**: metros cúbicos totales consumidos desde el inicio, valor que aparece en la factura.
* Si en enero la lectura tenia de volumen_acumulado_m3: 100 m³ y
* En febrefro tenia 108 m³, cobraran 8 m³.

**caudal_m3h**: litros por hora que están pasando en este momento
* Lo que se consume en ese momento de la lectura

**presion_bar**: presión de la red.
* la fuerza con lo que llega el agua al hogar.

**temperatura_c**: temperatura del agua, útil para detectar fugas
* esta es la temperatura del agua que está pasando por el contador en ese momento
  

### Smart meter gas
**volumen_acumulado_m3**: metros cúbicos consumidos acumulados
* Si en enero la lectura tenia de volumen_acumulado_m3: 500 m³ y
* En febrefro tenia 560 m³, cobraran 60 m³ (calculandolo tambien con el poder_calorifico_kwh_m3).
* 60 m³ × 11 kWh/m³ = 660 kWh → esto aparece en la factura

**caudal_m3h**: flujo instantáneo de gas
* Nos indica la cantidad de gas que esta pasando en el momento de la lectura


**presion_mbar**: presión del gas en milibares, crítica por seguridad
* la fuerza con la que llega el gas

**temperatura_c**: temperatura del gas
* La temperatura del gas que esta pasando en el momento de la lectura

**poder_calorifico_kwh_m3**: cuánta energía produce cada m³ de gas, varía según la composición del gas suministrado y lo usa la distribuidora para calcular la factura en kWh

## Campos clave de los smart meters

### Campos de facturación
Son los que generan el cobro:

| Suministro | Campo | Descripción |
|---|---|---|
| Luz | `energia_activa_kwh` | Energía total consumida desde el inicio |
| Agua | `volumen_acumulado_m3` | Metros cúbicos totales consumidos |
| Gas | `volumen_acumulado_m3` + `poder_calorifico_kwh_m3` | Volumen × poder calorífico = kWh facturados |

### Campos de diagnóstico
Son los que detectan problemas:

**Luz:**
* `voltaje_v` → detecta fallos en la red eléctrica
* `frecuencia_hz` → detecta sobrecarga de la red
* `corriente_a` → detecta cortocircuitos o sobrecargas en tu instalación
* `potencia_activa_kw` → detecta consumos anómalos

**Agua:**
* `caudal_m3h` → detecta fugas (flujo de madrugada cuando no debería haber)
* `presion_bar` → detecta roturas en la red
* `temperatura_c` → detecta fugas cerca de tuberías calientes

**Gas:**
* `caudal_m3h` → detecta fugas (el más crítico, riesgo de explosión)
* `presion_mbar` → detecta roturas o fugas en la red
* `temperatura_c` → corrige el volumen para que la factura sea justa

### Campos instantáneos
Fotografía del momento actual:

* `potencia_activa_kw` → lo que consumes ahora mismo (luz)
* `caudal_m3h` → lo que pasa por la tubería ahora mismo (agua y gas)

### Conclusion de uso
* Campos **acumulados** sirven para facturar
* Campos de **flujo y presión** sirven para detectar problemas
* Métricas de calidad de la red