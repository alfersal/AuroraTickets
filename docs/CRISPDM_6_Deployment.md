# **Deployment** {#deployment}

Para que todo esto funcione de verdad, he montado un clúster entero en AWS separando muy bien los roles de las máquinas para que no haya cuellos de botella.

![][image9]

Esta imagen muestra cómo he diseñado y desplegado la arquitectura de forma estructural, separando los roles de cada nodo y las capas del Data Lake.

**Infraestructura EC2 y Clúster Spark** He desplegado 6 instancias usando Ubuntu. Tengo una máquina dedicada solo para la web y su agente, un Spark Master que orquesta todo, 3 Spark Workers que se comen el trabajo pesado, y un Nodo Submit desde donde lanzo yo las órdenes. Están en la misma red y configurados por SSH.

EC2:

![][image10]

Como se ve en la interfaz web de Spark, los 3 workers están vivos y conectados al master trabajando en paralelo. El pipeline es totalmente reproducible: basta con ejecutar un comando `spark-submit` apuntando a mi script en el nodo submit, y el proceso fluye desde S3 crudo hasta la base de datos MySQL en RDS.

![][image11]

![][image12]

**Reproducibilidad End-to-End** El tribunal pide que este proyecto sea reproducible, es decir, que si otra persona entra a mi clúster, sepa cómo arrancar todo. La ventaja de haber montado un clúster Standalone de Spark es que el lanzamiento de tareas está totalmente centralizado en el Nodo Submit.

El comando exacto que he utilizado por consola para enviar mis scripts de Python al Spark Master y que este reparta el trabajo entre los Workers es el siguiente:

\# Lanzamiento del Job 1: Curación  
spark-submit \\  
  \--master spark://\<IP\_PRIVADA\_DEL\_MASTER\>:7077 \\  
  \--deploy-mode client \\  
  \--executor-memory 1G \\  
  \--total-executor-cores 3 \\  
  /home/ubuntu/jobs/job1\_curation.py

\# Lanzamiento del Job 2: Analítica y volcado a MySQL  
spark-submit \\  
  \--master spark://\<IP\_PRIVADA\_DEL\_MASTER\>:7077 \\  
  \--deploy-mode client \\  
  \--packages mysql:mysql-connector-java:8.0.28 \\  
  /home/ubuntu/jobs/job2\_analytics.py

Como se aprecia en el código, en el Job 2 he tenido que inyectar dinámicamente el paquete `.jar` del conector de MySQL (`--packages mysql...`). Sin esta librería, Spark habría sido incapaz de hablar con mi base de datos RDS para insertar las métricas finales.

Además, a nivel de Seguridad y Red, he configurado los Security Groups (Cortafuegos de AWS) de forma muy restrictiva:

* **Puerto 22 (SSH):** Abierto solo para mi IP personal, para poder administrar el clúster.  
* **Puerto 80 (HTTP):** Abierto a todo el mundo (0.0.0.0/0) únicamente en la máquina del Agente Web.  
* **Puertos 7077 y 8080 (Spark):** Abiertos únicamente para la comunicación interna de la red de AWS (VPC), impidiendo que alguien desde fuera de internet pueda inyectar código malicioso en mis workers.

Como evidencia adicional del procesamiento distribuido de Spark, he verificado la estructura interna de los directorios que se generan al finalizar los *Jobs*. En la siguiente captura se puede observar el interior de una de las carpetas de salida:

![][image13]

**Estimación de Costes (AWS Pricing Calculator)**

**Presupuesto Actual: 189,65 USD / mes** He realizado la estimación de costes final en la calculadora de AWS basándome estrictamente en la infraestructura desplegada, configurando los servicios bajo demanda (On-Demand) en la región `us-east-1`. Este coste mensual cubre las 6 máquinas EC2, la base de datos RDS, y la monitorización en CloudWatch.

**Análisis Comparativo (Cálculo de la IA)** Como parte de mi análisis técnico, he creído conveniente generar una tabla comparativa de lo que yo considero que debería ser el coste mensual optimizado para este proyecto. Esta tabla no es un presupuesto oficial, sino un cálculo generado por la IA sobre cuánto cree que debería costar todo si optimizáramos la base de datos.

| Concepto | Detalle Técnico Optimizado | Costo Mensual Estimado (USD) |
| :---- | :---- | :---- |
| **Computación (6 EC2)** | t4g.nano / Linux | \~$30.40 |
| **Almacenamiento (S3)** | 5 GB (Capa Estándar) | \~$0.15 |
| **Base de Datos (RDS)** | db.t3.micro (MySQL, Single-AZ) | \~$14.71 |
| **Observabilidad** | CloudWatch (Logs \+ Insights) | \~$15.00 |
| **TOTAL OPTIMIZADO (IA)** | **\-** | **\~$60.26** |

Al realizar esta comparativa, he detectado que la diferencia de casi 130$ entre mi presupuesto actual (189,65$) y el coste optimizado (60,26$) se debe exclusivamente a una instancia RDS redundante que se ha colado en el presupuesto (una `db.t3.medium` en `Multi-AZ` que cuesta 144,03$).

Dado que este proyecto es un entorno de pruebas, no necesitamos un despliegue de base de datos de "Alta Disponibilidad" (Multi-AZ), por lo que podríamos ahorrarnos ese sobrecoste. Aún así, presento el presupuesto de 189,65$ como una estimación viable en un entorno corporativo menos optimizado.

![][image14]

![][image15]