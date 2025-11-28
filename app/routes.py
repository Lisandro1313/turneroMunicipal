from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from calendar import monthrange
from app import db, limiter
from app.models import User, Organization, Schedule
from app.utils import log_action, editor_required, admin_required, generate_schedule_dates

main = Blueprint("main", __name__)

# Página de inicio
@main.route("/")
def index():
    """Página principal pública"""
    return render_template("base.html")

# Login
@main.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    """Login de usuarios con rate limiting"""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    
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
            log_action(user.id, 'login', details=f"Login exitoso de {username}")
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for("main.dashboard"))

        flash("Usuario o contraseña incorrecta", "error")
        log_action(None, 'login_failed', details=f"Intento fallido para usuario: {username}")
    
    return render_template("login.html")

# Logout
@main.route("/logout")
@login_required
def logout():
    """Cerrar sesión"""
    log_action(current_user.id, 'logout', details=f"Logout de {current_user.username}")
    logout_user()
    flash("Sesión cerrada exitosamente", "success")
    return redirect(url_for("main.index"))

# Dashboard
@main.route("/dashboard")
@login_required
def dashboard():
    """Dashboard principal - requiere login"""
    # Próximas entregas (próximos 7 días)
    today = datetime.now().date()
    week_later = today + timedelta(days=7)
    
    upcoming = Schedule.query.filter(
        Schedule.date >= today,
        Schedule.date <= week_later,
        Schedule.delivered == False
    ).order_by(Schedule.date).limit(10).all()
    
    # Estadísticas rápidas
    total_orgs = Organization.query.filter_by(is_active=True).count()
    pending_today = Schedule.query.filter(
        Schedule.date == today,
        Schedule.delivered == False
    ).count()
    
    return render_template("dashboard.html", 
                         upcoming=upcoming,
                         total_orgs=total_orgs,
                         pending_today=pending_today)

# Listado de organizaciones
@main.route("/organizations")
@login_required
def organizations():
    """Lista todas las organizaciones activas"""
    page = request.args.get('page', 1, type=int)
    direccion_filter = request.args.get('direccion')
    search = request.args.get('search', '')
    
    query = Organization.query.filter_by(is_active=True)
    
    if direccion_filter:
        query = query.filter_by(direccion_municipal=direccion_filter)
    
    if search:
        query = query.filter(
            (Organization.name.contains(search)) |
            (Organization.representative.contains(search))
        )
    
    organizations = query.order_by(Organization.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template("organizations.html", organizations=organizations)

# Agregar una organización
@main.route("/add_organization", methods=["GET", "POST"])
@login_required
@editor_required
def add_organization():
    """Agregar nueva organización - requiere rol editor o admin"""
    if request.method == "POST":
        try:
            org = Organization(
                name=request.form.get("name"),
                representative=request.form.get("representative"),
                address=request.form.get("address"),
                phone=request.form.get("phone"),
                email=request.form.get("email"),
                direccion_municipal=request.form.get("direccion_municipal"),
                tipo_organizacion=request.form.get("tipo_organizacion"),
                kilos=request.form.get("kilos", type=int),
                frequency=request.form.get("frequency", "mensual"),
                day_of_week=request.form.get("day_of_week", type=int),
                day_of_month=request.form.get("day_of_month", type=int),
                notes=request.form.get("notes")
            )
            
            db.session.add(org)
            db.session.commit()
            
            log_action(current_user.id, 'create', 'organization', org.id, 
                      f"Creada organización: {org.name}")
            
            flash("Organización agregada exitosamente", "success")
            return redirect(url_for("main.organizations"))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Error al agregar organización: {str(e)}", "error")

    return render_template("add_organization.html")

# Editar una organización
@main.route("/edit_organization/<int:id>", methods=["GET", "POST"])
@login_required
@editor_required
def edit_organization(id):
    """Editar organización existente"""
    org = Organization.query.get_or_404(id)

    if request.method == "POST":
        try:
            org.name = request.form.get("name")
            org.representative = request.form.get("representative")
            org.address = request.form.get("address")
            org.phone = request.form.get("phone")
            org.email = request.form.get("email")
            org.direccion_municipal = request.form.get("direccion_municipal")
            org.tipo_organizacion = request.form.get("tipo_organizacion")
            org.kilos = request.form.get("kilos", type=int)
            org.frequency = request.form.get("frequency")
            org.day_of_week = request.form.get("day_of_week", type=int)
            org.day_of_month = request.form.get("day_of_month", type=int)
            org.notes = request.form.get("notes")

            db.session.commit()
            
            log_action(current_user.id, 'update', 'organization', org.id, 
                      f"Actualizada organización: {org.name}")
            
            flash("Organización actualizada correctamente", "success")
            return redirect(url_for("main.organizations"))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar organización: {str(e)}", "error")

    return render_template("edit_organization.html", organization=org)

# Eliminar una organización
@main.route("/delete_organization/<int:id>")
@login_required
@admin_required
def delete_organization(id):
    """Desactivar organización - solo admin"""
    org = Organization.query.get_or_404(id)
    
    try:
        org.is_active = False
        db.session.commit()
        
        log_action(current_user.id, 'delete', 'organization', org.id, 
                  f"Desactivada organización: {org.name}")
        
        flash("Organización eliminada correctamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar organización: {str(e)}", "error")
    
    return redirect(url_for("main.organizations"))

# Generar cronograma
@main.route("/generate_schedule", methods=["GET", "POST"])
@login_required
@editor_required
def generate_schedule():
    """Generar cronograma automático basado en las organizaciones"""
    if request.method == "POST":
        try:
            start_date_str = request.form.get("start_date")
            end_date_str = request.form.get("end_date")
            clear_existing = request.form.get("clear_existing") == "on"
            
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            if start_date > end_date:
                flash("La fecha de inicio debe ser anterior a la fecha de fin", "error")
                return render_template("generate_schedule.html")
            
            # Limpiar cronograma existente si se solicita
            if clear_existing:
                Schedule.query.delete()
            
            organizations = Organization.query.filter_by(is_active=True).all()
            schedules_created = 0
            
            for org in organizations:
                # Generar fechas según frecuencia
                dates = generate_schedule_dates(
                    org.frequency,
                    start_date,
                    end_date,
                    org.day_of_week,
                    org.day_of_month
                )
                
                for date in dates:
                    # Verificar si ya existe
                    existing = Schedule.query.filter_by(
                        organization_id=org.id,
                        date=date
                    ).first()
                    
                    if not existing:
                        schedule = Schedule(
                            organization_id=org.id,
                            date=date,
                            kilos=org.kilos,
                            delivered=False
                        )
                        db.session.add(schedule)
                        schedules_created += 1
            
            db.session.commit()
            
            log_action(current_user.id, 'generate_schedule', details=
                      f"Generadas {schedules_created} entregas desde {start_date} hasta {end_date}")
            
            flash(f"Cronograma generado con éxito. {schedules_created} entregas programadas.", "success")
            return redirect(url_for("main.schedule_list"))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Error al generar cronograma: {str(e)}", "error")
    
    return render_template("generate_schedule.html")

# Listar cronograma
@main.route("/schedule_list")
@login_required
def schedule_list():
    """Lista de todas las entregas programadas"""
    page = request.args.get('page', 1, type=int)
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    org_id = request.args.get('organization', type=int)
    status = request.args.get('status')
    
    query = Schedule.query
    
    # Filtros
    if month and year:
        first_day = datetime(year, month, 1).date()
        last_day = datetime(year, month, monthrange(year, month)[1]).date()
        query = query.filter(Schedule.date >= first_day, Schedule.date <= last_day)
    
    if org_id:
        query = query.filter_by(organization_id=org_id)
    
    if status == 'delivered':
        query = query.filter_by(delivered=True)
    elif status == 'pending':
        query = query.filter_by(delivered=False)
    
    schedules = query.order_by(Schedule.date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Para los filtros
    organizations = Organization.query.filter_by(is_active=True).order_by(Organization.name).all()
    
    return render_template("schedule_list.html", 
                         schedules=schedules,
                         organizations=organizations)

# Cronograma por mes y año
@main.route("/schedule/<int:year>/<int:month>")
@login_required
def schedule_month(year, month):
    """Ver cronograma de un mes específico"""
    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, monthrange(year, month)[1]).date()

    schedules = Schedule.query.filter(
        Schedule.date >= first_day,
        Schedule.date <= last_day
    ).order_by(Schedule.date).all()

    return render_template("schedule_month.html", 
                         schedules=schedules, 
                         year=year, 
                         month=month)
