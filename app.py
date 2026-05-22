from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta-para-desarrollo'
# Usamos SQLite por simplicidad. En Docker puedes cambiarlo a la URL de tu DB.
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://reservasuser:reservas123@10.10.0.12/reservas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODELOS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    reservas = db.relationship('Reserva', backref='autor', lazy=True)

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    dia = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- RUTAS DE AUTENTICACIÓN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('index'))
        flash('Credenciales inválidas')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe')
            return redirect(url_for('registro'))
            
        nuevo_usuario = User(username=username, password=generate_password_hash(password))
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- RUTAS DE RESERVAS ---
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        nueva_reserva = Reserva(
            nombre=request.form.get('nombre'),
            telefono=request.form.get('telefono'),
            correo=request.form.get('correo'),
            dia=datetime.strptime(request.form.get('dia'), '%Y-%m-%d').date(),
            hora=datetime.strptime(request.form.get('hora'), '%H:%M').time(),
            user_id=current_user.id
        )
        db.session.add(nueva_reserva)
        db.session.commit()
        flash('Reserva guardada con éxito')
        return redirect(url_for('index'))
        
    mis_reservas = Reserva.query.filter_by(user_id=current_user.id).all()
    return render_template('reservas.html', reservas=mis_reservas)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Crea la base de datos si no existe
    app.run(debug=True, host='0.0.0.0') # host='0.0.0.0' es clave para Docker
