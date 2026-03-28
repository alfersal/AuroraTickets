import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, to_date

def main():
    # 1. Inicializar sesión de Spark
    spark = SparkSession.builder \
        .appName("Job1_Curation_AuroraTickets") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")

    # Definir rutas (¡Cambia 'tu-bucket-aurora' por tu bucket real!)
    S3_RAW_PATH = "s3://tu-bucket-aurora/raw/"
    S3_CURATED_PATH = "s3://tu-bucket-aurora/curated/"

    print("--- Iniciando Job 1: Ingesta y Limpieza ---")

    # 2. Lectura de datos Raw
    df_clickstream = spark.read.json(f"{S3_RAW_PATH}clickstream/")
    df_events = spark.read.csv(f"{S3_RAW_PATH}business/events.csv", header=True, inferSchema=True)
    df_transactions = spark.read.csv(f"{S3_RAW_PATH}business/transactions.csv", header=True, inferSchema=True)

    # 3. Limpieza de datos (Lógica exacta de la memoria)
    # Eliminar precios negativos y nulos del catálogo
    df_events_clean = df_events.filter((col("base_price") > 0) & (col("base_price").isNotNull()))

    # Casteo de fechas y limpieza de transacciones
    df_transactions_clean = df_transactions.withColumn(
        "transaction_date", to_timestamp(col("date_string"))
    ).filter(col("revenue") > 0).dropna(subset=["session_id", "event_id"])

    # 4. Cruce (Enriquecimiento del Clickstream)
    df_clickstream_enriched = df_clickstream.join(
        df_events_clean,
        on="event_id",
        how="left"
    )

    # Añadir columna 'dt' para particionado físico por fecha
    df_final = df_clickstream_enriched.withColumn("dt", to_date(col("timestamp")))

    # 5. Escritura en capa Curated (S3) en formato Parquet particionado
    print("--- Escribiendo datos limpios en S3 (Curated) ---")
    df_final.write \
        .mode("overwrite") \
        .partitionBy("dt") \
        .parquet(f"{S3_CURATED_PATH}clickstream/")

    print("--- Job 1 Completado con Éxito ---")
    spark.stop()

if __name__ == "__main__":
    main()