from werkzeug.security import generate_password_hash
from app import db
from app.models import User

# Reemplaza estos valores por los del usuario administrador que necesitas.
username = "lisandro"
password = "lisandro"

# Crear un nuevo usuario con la contraseña encriptada
hashed_password = generate_password_hash('lisandro', method='sha256')
user = User(username=username, password=hashed_password)

db.session.add(user)
db.session.commit()

print("Usuario creado con éxito")
