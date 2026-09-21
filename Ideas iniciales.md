**Propuesta — Plataforma de Transparencia de Calidad para Clientes**



**Objetivo**

Dar a los clientes acceso digital y oportuno a la calidad de los productos que compran, para fortalecer la confianza y retención, reemplazando el proceso manual actual de envío de reportes PDF.



**Problema actual**



Reportes de granulometría generados y enviados manualmente por producto

Disponibles hasta fin de mes, con atrasos frecuentes

El cliente recibe el dato cuando ya no le sirve para decidir



**Propuesta de solución**

Plataforma web de acceso individual (por credenciales o enlace temporal) donde cada cliente visualiza la calidad de los productos que ha comprado.



**Alcance funcional (v1)**



Reporte de granulometría por producto comprado

Actualización periódica alineada a ciclos de laboratorio (no diaria)

Acceso condicionado a compra vigente en ventana de tiempo definida (misma regla actual, ahora digitalizada)

Gráficas de tendencia histórica / control de variabilidad por producto

Certificado de cumplimiento normativo descargable

Canal de contacto directo con laboratorio



**Fuera de alcance (v1)**



Trazabilidad por entrega/camión — se evalúa en fase futura



**Valor esperado**



Reduce fricción y tiempo de espera del cliente

Refuerza el argumento de venta basado en calidad, no precio

Sienta base de datos estructurada para análisis futuro (ML/BI) sobre calidad y comportamiento de compra









**DATOS NECESARIOS (BOCETO)**



**TABLA DE LABORATORIO (calidad del producto)**

1\. id\_muestra – identificador único de cada muestra/ensayo

2\. producto – nombre estandarizado del producto (mismo catálogo que ventas)

3\. fecha\_muestreo – fecha en que se tomó la muestra

4\. tamiz – tamaño de malla evaluado

5\. porcentaje\_pasa – resultado real del ensayo en ese tamiz

6\. limite\_inferior\_norma – límite inferior aceptable según norma, por tamiz

7\. limite\_superior\_norma – límite superior aceptable según norma, por tamiz

8\. norma\_referencia – norma técnica utilizada (ej. ASTM, NMX, u otra local)



**TABLA COMERCIAL (ventas)**

9\. id\_cliente – identificador único del cliente

10\. producto – mismo nombre estandarizado que en laboratorio (debe coincidir exactamente)

11\. fecha\_compra – fecha en que se realizó la compra



**PIEZA ESTRUCTURAL NECESARIA**

12\. Catálogo único de productos – lista maestra con un solo nombre/código por producto,

&#x20;   usado de forma idéntica tanto en laboratorio como en ventas.

&#x20;   Sin esto no es posible cruzar la información de calidad con la de compras.



**PREGUNTAS CLAVE A CONFIRMAR**

\- ¿El laboratorio guarda sus resultados en algún archivo editable (Excel/CSV), o todo termina directo en PDF sin quedar un respaldo digital editable?

\- ¿Existe ya una lista de productos con nombre consistente,

&#x20; o cada área (laboratorio/ventas) le llama distinto al mismo producto?

\- ¿Dónde vive hoy el dato de qué compró cada cliente y en qué fecha

&#x20; (sistema de facturación, ERP, Excel de ventas, otro)?





**FLUJO DE DATOS PROPUESTO (VISIÓN GENERAL)**



**1. Origen del dato**

&#x20;  El laboratorio registra los resultados de calidad de cada producto

&#x20;  (granulometría) en un formato digital estandarizado, en lugar de

&#x20;  generarlos directamente como PDF individuales.



**2. Ordenamiento y validación**

&#x20;  Esa información se organiza automáticamente mediante un proceso

&#x20;  que limpia, valida y compara cada resultado contra la norma

&#x20;  correspondiente, determinando si el producto cumple o no.



**3. Almacenamiento central**

&#x20;  Los resultados, ya ordenados, se guardan en una base de datos

&#x20;  central que sirve como fuente única de información — evitando

&#x20;  reportes sueltos y dispersos como ocurre hoy.



**4. Cruce con información comercial** 

&#x20;  Esa misma base se conecta con los datos de ventas (qué compró

&#x20;  cada cliente y cuándo), para saber automáticamente a qué

&#x20;  información tiene acceso cada uno.



**5. Plataforma para el cliente**

&#x20;  La plataforma web consulta esa base de datos y le muestra a

&#x20;  cada cliente, de forma automática y actualizada, la calidad de

&#x20;  los productos que ha comprado — sin intervención manual.



**6. Actualización periódica**

&#x20;  Cada vez que el laboratorio genera nuevos resultados, estos se

&#x20;  reflejan en la plataforma en el siguiente ciclo de actualización,

&#x20;  sin necesidad de reenviar nada manualmente.



**Resumen**

**En lugar de un proceso manual (laboratorio → PDF → envío por correo),**

**se propone un flujo automático (laboratorio → base de datos →**

**plataforma → cliente), más rápido, más confiable y sin depender de**

**que una persona lo gestione reporte por reporte.**

