-- ============================================
-- Script para ACTUALIZAR passwords de usuarios existentes
-- Ejecutar este en Neon SQL Editor
-- ============================================

-- Actualizar password de admin a admin123
UPDATE "user" 
SET password_hash = 'scrypt:32768:8:1$Iq5jLvmzbTIcKPNa$dbb5eac8ffb451e35c5122fab54798b7dc3daad5c607f362d6e3af46ea888f4006e78416fe2224df56858cb66d2465b71d996b4817c2d8e954ede1c80f54bdec'
WHERE username = 'admin';

-- Actualizar password de recepcion a recepcion123
UPDATE "user" 
SET password_hash = 'scrypt:32768:8:1$1YjClFumQ2cQrpEC$8e5c38e07235f098f3f09e60f8dde08a33dc20ad17e0cd13969e1f6a20adea9d8556def9df3fba459e6b0be2b12571bb823a6f15ff887e9b83af4a56ba204807'
WHERE username = 'recepcion';

-- Actualizar password de piso1 a piso1123
UPDATE "user" 
SET password_hash = 'scrypt:32768:8:1$NOvHYqbiO8KLxk3a$d7bd9bba2263a5613ea8853c625851e1e05a13af4d4655c5e78f5051a771618511673dcd3c1b98a46a03262ba637077d84c813118961c0bb1195154e38b452c2'
WHERE username = 'piso1';

-- Actualizar password de piso2 a piso2123
UPDATE "user" 
SET password_hash = 'scrypt:32768:8:1$UucLvf3LXyXIFN3J$77e405df80fd0cb2008de6e9fda9ab58fcd99bc46fddc73c4bb7400aebe93f72ce6eb6c3ea41e284c30fe6c60ed71f6e9b2581c9db805bdaf26e326cb596e326'
WHERE username = 'piso2';

-- Actualizar password de piso3 a piso3123
UPDATE "user" 
SET password_hash = 'scrypt:32768:8:1$SFk2b4DlWhWMZm0p$cab3b085cf01bca4502674999e21a4ef55105fe5eab0d9f355fde9f381d059ff83f9e32de356f77480f1125191d4c0685ea7c097df89e4011b8f5bd048e28f6c'
WHERE username = 'piso3';

-- Verificar los usuarios actualizados
SELECT username, role, piso, is_active 
FROM "user" 
ORDER BY id;
