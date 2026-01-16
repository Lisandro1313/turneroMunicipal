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

-- Password: admin123
INSERT INTO "user" (username, email, password_hash, role, piso, is_active) 
VALUES ('admin', 'admin@municipio.gov.ar', 'scrypt:32768:8:1$Iq5jLvmzbTIcKPNa$dbb5eac8ffb451e35c5122fab54798b7dc3daad5c607f362d6e3af46ea888f4006e78416fe2224df56858cb66d2465b71d996b4817c2d8e954ede1c80f54bdec', 'admin', NULL, TRUE)
ON CONFLICT (username) DO NOTHING;

-- Password: recepcion123
INSERT INTO "user" (username, email, password_hash, role, piso, is_active) 
VALUES ('recepcion', 'recepcion@municipio.gov.ar', 'scrypt:32768:8:1$1YjClFumQ2cQrpEC$8e5c38e07235f098f3f09e60f8dde08a33dc20ad17e0cd13969e1f6a20adea9d8556def9df3fba459e6b0be2b12571bb823a6f15ff887e9b83af4a56ba204807', 'recepcion', NULL, TRUE)
ON CONFLICT (username) DO NOTHING;

-- Password: piso1123
INSERT INTO "user" (username, email, password_hash, role, piso, is_active) 
VALUES ('piso1', 'piso1@municipio.gov.ar', 'scrypt:32768:8:1$NOvHYqbiO8KLxk3a$d7bd9bba2263a5613ea8853c625851e1e05a13af4d4655c5e78f5051a771618511673dcd3c1b98a46a03262ba637077d84c813118961c0bb1195154e38b452c2', 'piso1', '1', TRUE)
ON CONFLICT (username) DO NOTHING;

-- Password: piso2123
INSERT INTO "user" (username, email, password_hash, role, piso, is_active) 
VALUES ('piso2', 'piso2@municipio.gov.ar', 'scrypt:32768:8:1$UucLvf3LXyXIFN3J$77e405df80fd0cb2008de6e9fda9ab58fcd99bc46fddc73c4bb7400aebe93f72ce6eb6c3ea41e284c30fe6c60ed71f6e9b2581c9db805bdaf26e326cb596e326', 'piso2', '2', TRUE)
ON CONFLICT (username) DO NOTHING;

-- Password: piso3123
INSERT INTO "user" (username, email, password_hash, role, piso, is_active) 
VALUES ('piso3', 'piso3@municipio.gov.ar', 'scrypt:32768:8:1$SFk2b4DlWhWMZm0p$cab3b085cf01bca4502674999e21a4ef55105fe5eab0d9f355fde9f381d059ff83f9e32de356f77480f1125191d4c0685ea7c097df89e4011b8f5bd048e28f6c', 'piso3', '3', TRUE)
ON CONFLICT (username) DO NOTHING;

-- ============================================
-- Verificar que se crearon correctamente
-- ============================================

SELECT 'Tablas creadas correctamente:' AS mensaje;
SELECT COUNT(*) AS total_users FROM "user";
SELECT username, role, piso FROM "user";
