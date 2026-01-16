from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app import db, limiter, csrf
from app.models import User

main = Blueprint("main", __name__)

# Página de inicio - redirige según rol
@main.route("/")
def index():
    """Página principal - redirige según rol del usuario"""
    if current_user.is_authenticated:
        # Redirigir según el rol del usuario
        if current_user.role == 'recepcion':
            return redirect(url_for('turns.recepcion'))
        elif current_user.role in ['piso1', 'piso2', 'piso3']:
            # Extraer número de piso del role
            piso_num = current_user.role.replace('piso', '')
            return redirect(url_for('turns.piso_llamado', numero=int(piso_num)))
        else:  # admin puede ver recepción por defecto
            return redirect(url_for('turns.recepcion'))
    return render_template("base.html")

# Login
@main.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    """Login de usuarios con rate limiting"""
    if current_user.is_authenticated:
        return redirect(url_for('turns.recepcion'))
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Por favor completa todos los campos", "error")
            return render_template("login.html")

        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash("Tu cuenta está desactivada. Contacta al administrador.", "error")
                return render_template("login.html")
            
            login_user(user, remember=True)
            user.update_last_login()
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Redirigir según rol
            if user.role == 'recepcion':
                return redirect(url_for('turns.recepcion'))
            elif user.role in ['piso1', 'piso2', 'piso3']:
                # Extraer número de piso del role
                piso_num = user.role.replace('piso', '')
                return redirect(url_for('turns.piso_llamado', numero=int(piso_num)))
            else:  # admin
                return redirect(url_for('turns.recepcion'))

        flash("Usuario o contraseña incorrecta", "error")
    
    return render_template("login.html")

# API Login para mobile
@main.route("/api/login", methods=["POST"])
@csrf.exempt
@limiter.limit("10 per minute")
def api_login():
    """Login API para app mobile"""
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username or not password:
            return jsonify({"success": False, "error": "Usuario y contraseña requeridos"}), 400

        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                return jsonify({"success": False, "error": "Cuenta desactivada"}), 403
            
            login_user(user, remember=True)
            user.update_last_login()
            
            return jsonify({
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "piso": user.piso
                }
            }), 200
        
        return jsonify({"success": False, "error": "Credenciales inválidas"}), 401
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Logout
@main.route("/logout")
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash("Sesión cerrada exitosamente", "success")
    return redirect(url_for("main.index"))
