-- ============================================
-- SQL para crear tablas en Neon.tech
-- Sistema de Turnos Municipal
-- ============================================

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'piso1',
    piso VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Índices para user
CREATE INDEX IF NOT EXISTS idx_user_username ON "user"(username);

-- Tabla de turnos de visitantes
CREATE TABLE IF NOT EXISTS visitor_turn (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    dni VARCHAR(20),
    area_key VARCHAR(100) NOT NULL,
    area_nombre VARCHAR(200) NOT NULL,
    piso VARCHAR(20),
    motivo_key VARCHAR(100),
    motivo_texto VARCHAR(300),
    estado VARCHAR(30) NOT NULL DEFAULT 'ESPERA',
    hora_llegada TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    hora_autorizado TIMESTAMP WITH TIME ZONE,
    hora_atendido TIMESTAMP WITH TIME ZONE,
    llamado_por VARCHAR(150),
    atendido_por VARCHAR(150),
    notas TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para visitor_turn
CREATE INDEX IF NOT EXISTS idx_visitor_turn_nombre ON visitor_turn(nombre);
CREATE INDEX IF NOT EXISTS idx_visitor_turn_dni ON visitor_turn(dni);
CREATE INDEX IF NOT EXISTS idx_visitor_turn_area_key ON visitor_turn(area_key);
CREATE INDEX IF NOT EXISTS idx_visitor_turn_motivo_key ON visitor_turn(motivo_key);
CREATE INDEX IF NOT EXISTS idx_visitor_turn_hora_llegada ON visitor_turn(hora_llegada);

-- Tabla de mensajes de chat
CREATE TABLE IF NOT EXISTS chat_message (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(150) NOT NULL,
    origen VARCHAR(50) NOT NULL,
    mensaje TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    leido BOOLEAN DEFAULT FALSE
);

-- Índices para chat_message
CREATE INDEX IF NOT EXISTS idx_chat_message_timestamp ON chat_message(timestamp);

-- ============================================
-- Insertar usuarios por defecto
-- ============================================

-- Password: admin
INSERT INTO "user" (username, email, password_hash, role, piso, is_active) 
VALUES ('admin', 'admin@municipio.gov.ar', 'scrypt:32768:8:1$iGVt5Hv32FBKaPHu$2bc35dac6a8a45def44348b5f2e3ac7f1b3d05bb372ef9ec31a1bc34a9a93baea9cd076b06a4a8b23f6c9f52cf3db7fe30b8d28a4f96c0dc7b6dbbd06f4acf79', 'admin', NULL, TRUE)
ON CONFLICT (username) DO NOTHING;

-- Password: recepcion
INSERT INTO "user" (username, email, password_hash, role, piso, is_active) 
VALUES ('recepcion', 'recepcion@municipio.gov.ar', 'scrypt:32768:8:1$iGVt5Hv32FBKaPHu$2bc35dac6a8a45def44348b5f2e3ac7f1b3d05bb372ef9ec31a1bc34a9a93baea9cd076b06a4a8b23f6c9f52cf3db7fe30b8d28a4f96c0dc7b6dbbd06f4acf79', 'recepcion', NULL, TRUE)
ON CONFLICT (username) DO NOTHING;

-- Password: piso1
INSERT INTO "user" (username, email, password_hash, role, piso, is_active) 
VALUES ('piso1', 'piso1@municipio.gov.ar', 'scrypt:32768:8:1$iGVt5Hv32FBKaPHu$2bc35dac6a8a45def44348b5f2e3ac7f1b3d05bb372ef9ec31a1bc34a9a93baea9cd076b06a4a8b23f6c9f52cf3db7fe30b8d28a4f96c0dc7b6dbbd06f4acf79', 'piso1', '1', TRUE)
ON CONFLICT (username) DO NOTHING;

-- Password: piso2
INSERT INTO "user" (username, email, password_hash, role, piso, is_active) 
VALUES ('piso2', 'piso2@municipio.gov.ar', 'scrypt:32768:8:1$iGVt5Hv32FBKaPHu$2bc35dac6a8a45def44348b5f2e3ac7f1b3d05bb372ef9ec31a1bc34a9a93baea9cd076b06a4a8b23f6c9f52cf3db7fe30b8d28a4f96c0dc7b6dbbd06f4acf79', 'piso2', '2', TRUE)
ON CONFLICT (username) DO NOTHING;

-- Password: piso3
INSERT INTO "user" (username, email, password_hash, role, piso, is_active) 
VALUES ('piso3', 'piso3@municipio.gov.ar', 'scrypt:32768:8:1$iGVt5Hv32FBKaPHu$2bc35dac6a8a45def44348b5f2e3ac7f1b3d05bb372ef9ec31a1bc34a9a93baea9cd076b06a4a8b23f6c9f52cf3db7fe30b8d28a4f96c0dc7b6dbbd06f4acf79', 'piso3', '3', TRUE)
ON CONFLICT (username) DO NOTHING;

-- ============================================
-- Verificar que se crearon correctamente
-- ============================================

SELECT 'Tablas creadas correctamente:' AS mensaje;
SELECT COUNT(*) AS total_users FROM "user";
SELECT username, role, piso FROM "user";
