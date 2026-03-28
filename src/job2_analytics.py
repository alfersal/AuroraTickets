import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, when, window

def main():
    # 1. Inicializar sesión de Spark
    spark = SparkSession.builder \
        .appName("Job2_Analytics_AuroraTickets") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")

    # Definir rutas y credenciales
    S3_CURATED_PATH = "s3://tu-bucket-aurora/curated/clickstream/"
    S3_ANALYTICS_PATH = "s3://tu-bucket-aurora/analytics/"
    
    # Credenciales RDS (¡Ajusta estos datos con tu base de datos!)
    RDS_URL = "jdbc:mysql://aurora-db.crq8ce88m17t.us-east-1.rds.amazonaws.com:3306/auroraanalytics"
    RDS_USER = "admin"
    RDS_PASSWORD = "TU_PASSWORD_AQUI"

    print("--- Iniciando Job 2: Productos Analíticos ---")

    # 2. Leer datos curados
    df_curated = spark.read.parquet(S3_CURATED_PATH)

    # ---------------------------------------------------------
    # PRODUCTO A: FUNNEL DIARIO
    # ---------------------------------------------------------
    # Agrupamos por fecha y sesión, contando qué acciones ha hecho el usuario
    df_funnel = df_curated.groupBy("dt", "session_id").agg(
        count("*").alias("total_events"),
        _sum(when(col("event_type") == "view", 1).otherwise(0)).alias("detail_views"),
        _sum(when(col("event_type") == "begin_checkout", 1).otherwise(0)).alias("checkouts"),
        _sum(when(col("event_type") == "purchase", 1).otherwise(0)).alias("purchases")
    )

    # Escribir en la base de datos MySQL (RDS) para validar coherencia
    print("--- Escribiendo Funnel en MySQL (RDS) ---")
    df_funnel.write \
        .format("jdbc") \
        .option("url", RDS_URL) \
        .option("dbtable", "metrics_funnel_daily") \
        .option("user", RDS_USER) \
        .option("password", RDS_PASSWORD) \
        .option("driver", "com.mysql.cj.jdbc.Driver") \
        .mode("overwrite") \
        .save()

    # ---------------------------------------------------------
    # PRODUCTO B: RANKING DE EVENTOS (ROI)
    # ---------------------------------------------------------
    # Cruzamos las visitas al detalle con las compras efectivas
    df_ranking = df_curated.filter(col("event_id").isNotNull()).groupBy("event_id", "name").agg(
        count("*").alias("total_interactions"),
        _sum(when(col("event_type") == "purchase", 1).otherwise(0)).alias("total_purchases")
    ).orderBy(col("total_purchases").desc())

    # Escribir en S3 Analytics
    df_ranking.write.mode("overwrite").parquet(f"{S3_ANALYTICS_PATH}event_rank/")

    # ---------------------------------------------------------
    # PRODUCTO C: ANOMALÍAS Y BOTS
    # ---------------------------------------------------------
    # Agrupamos por IP en ventanas de 1 minuto para buscar ráfagas de peticiones
    df_anomalies = df_curated.groupBy("ip", window("timestamp", "1 minute")).agg(
        count("*").alias("request_count")
    ).filter(col("request_count") > 50) # Umbral de bot estático

    # Escribir en S3 Analytics
    df_anomalies.write.mode("overwrite").parquet(f"{S3_ANALYTICS_PATH}anomalies/")

    print("--- Job 2 Completado con Éxito ---")
    spark.stop()

if __name__ == "__main__":
    main()