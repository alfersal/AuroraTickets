-- ==============================================================================
-- Script de inicialización de Base de Datos - Aurora Tickets
-- Motor: MySQL (Amazon RDS)
-- Propósito: Creación del esquema analítico para visualización de KPIs
-- ==============================================================================

-- 1. Crear la base de datos analítica si no existe
CREATE DATABASE IF NOT EXISTS auroraanalytics;
USE auroraanalytics;

-- 2. Crear la tabla del Producto A (Funnel Diario)
-- Esta tabla recibirá los datos procesados por el Job 2 de Apache Spark
CREATE TABLE IF NOT EXISTS metrics_funnel_daily (
    dt DATE COMMENT 'Fecha de la partición de los eventos',
    session_id VARCHAR(255) COMMENT 'ID único de la sesión de navegación',
    total_events INT COMMENT 'Total de acciones realizadas en la sesión',
    detail_views INT COMMENT 'Veces que el usuario vio los detalles de un evento',
    checkouts INT COMMENT 'Veces que el usuario inició el proceso de pago',
    purchases INT COMMENT 'Compras finales completadas'
);

-- (Opcional) Índices para acelerar las consultas del Dashboard
CREATE INDEX idx_dt ON metrics_funnel_daily(dt);
CREATE INDEX idx_session ON metrics_funnel_daily(session_id);