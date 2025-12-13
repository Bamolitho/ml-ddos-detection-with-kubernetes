-- =========================================================
-- BASE DE DONNÉES DDoS Detection
-- =========================================================

CREATE DATABASE IF NOT EXISTS ddos_detection
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE ddos_detection;

-- =========================================================
-- TABLE USERS (AUTHENTIFICATION)
-- =========================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci;

-- =========================================================
-- TABLE FLOWS (DDoS DETECTION)
-- =========================================================
CREATE TABLE IF NOT EXISTS flows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    src_ip VARCHAR(45),
    dst_ip VARCHAR(45),
    src_port INT,
    dst_port INT,
    prediction INT,
    verdict ENUM('Benign', 'DDoS') NOT NULL,
    probability FLOAT NULL,
    threshold FLOAT NULL,
    action ENUM('Passed', 'Blocked') NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_timestamp (timestamp),
    INDEX idx_verdict (verdict),
    INDEX idx_action (action)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci;

SELECT '[OK] Base ddos_detection initialisée' AS status;
