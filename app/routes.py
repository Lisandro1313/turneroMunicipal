from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from app import db, limiter
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
        elif current_user.role == 'pisos':
            return redirect(url_for('turns.piso_llamado', numero=1))
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
            elif user.role == 'pisos':
                return redirect(url_for('turns.piso_llamado', numero=1))
            else:  # admin
                return redirect(url_for('turns.recepcion'))

        flash("Usuario o contraseña incorrecta", "error")
    
    return render_template("login.html")

# Logout
@main.route("/logout")
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash("Sesión cerrada exitosamente", "success")
    return redirect(url_for("main.index"))
