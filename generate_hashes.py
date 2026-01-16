from werkzeug.security import generate_password_hash

# Generar hashes para cada usuario
users = {
    'admin': 'admin123',
    'recepcion': 'recepcion123',
    'piso1': 'piso1123',
    'piso2': 'piso2123',
    'piso3': 'piso3123'
}

print("-- Hashes generados correctamente:\n")
for username, password in users.items():
    hash_password = generate_password_hash(password)
    print(f"-- Usuario: {username} / Password: {password}")
    print(f"'{hash_password}'")
    print()
