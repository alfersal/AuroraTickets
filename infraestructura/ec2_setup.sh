#!/bin/bash
# ==============================================================================
# Script de automatización (User Data) para Nodos EC2 - Aurora Tickets
# Sistema Operativo: Ubuntu Server 22.04 LTS
# Propósito: Instalación desatendida de dependencias, Java y Apache Spark
# ==============================================================================

echo "--- Iniciando configuración del nodo EC2 ---"

# 1. Actualizar repositorios del sistema
sudo apt-get update -y
sudo apt-get upgrade -y

# 2. Instalar herramientas básicas y Python 3
sudo apt-get install -y wget tar unzip curl python3 python3-pip

# 3. Instalar Java (Requisito fundamental para Apache Spark)
echo "--- Instalando OpenJDK 8 ---"
sudo apt-get install -y openjdk-8-jdk

# 4. Descargar e instalar Apache Spark (Versión 3.2.1 - Pre-construida para Hadoop)
echo "--- Descargando Apache Spark ---"
cd /tmp
wget https://archive.apache.org/dist/spark/spark-3.2.1/spark-3.2.1-bin-hadoop3.2.tgz

echo "--- Descomprimiendo y moviendo a /opt/spark ---"
tar -xzf spark-3.2.1-bin-hadoop3.2.tgz
sudo mv spark-3.2.1-bin-hadoop3.2 /opt/spark

# 5. Configurar Variables de Entorno para todos los usuarios
echo "--- Configurando variables de entorno (SPARK_HOME y JAVA_HOME) ---"
echo "export SPARK_HOME=/opt/spark" | sudo tee -a /etc/profile.d/spark.sh
echo "export PATH=\$PATH:/opt/spark/bin:/opt/spark/sbin" | sudo tee -a /etc/profile.d/spark.sh
echo "export PYSPARK_PYTHON=/usr/bin/python3" | sudo tee -a /etc/profile.d/spark.sh

# Recargar variables
source /etc/profile.d/spark.sh

# 6. Crear carpetas de trabajo para los Jobs de Aurora Tickets
mkdir -p /home/ubuntu/jobs
mkdir -p /home/ubuntu/data
chown -R ubuntu:ubuntu /home/ubuntu/jobs
chown -R ubuntu:ubuntu /home/ubuntu/data

echo "--- Instalación completada con éxito. El nodo está listo. ---"
spark-submit --version