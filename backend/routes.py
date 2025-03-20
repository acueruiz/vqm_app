from flask import Blueprint, request, jsonify, session, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from .models import db, Usuario, CorreoUsuario, PermisoUsuario, VqmTemperatura, TratamientoNCVqm, DatosMdms, VqmMdm, VqmTemperaturaMI10

bcrypt = Bcrypt()

# creamos la Blueprint llamada "vqm" que agrupará todas las rutas de la API (__init__.py)
# para integrarse con la aplicación Flask
api_blueprint = Blueprint('vqm', __name__)

@api_blueprint.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Bienvenido a la API de VQM"}), 200

# ruta de prueba, para ver si la app está activa
@api_blueprint.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "API funcionando correctamente"}), 200

# rutas genéricas y dinámicas para obtener, insertar, actualizar y eliminar registros
MODELOS = {
    "usuarios": Usuario,
    "correos_usuarios": CorreoUsuario,
    "permisos_usuarios": PermisoUsuario,
    "vqm_temperatura": VqmTemperatura,
    "tratamiento_nc_vqm": TratamientoNCVqm,
    "datos_mdms": DatosMdms,
    "vqm_mdm": VqmMdm,
    "vqm_temperatura_mi10": VqmTemperaturaMI10
}

@api_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    print(f"Intentando login con: {email} - {password}")  # <-- Añade esto para ver qué datos llegan

    user = Usuario.query.filter_by(email=email).first()
    
    if user:
        print(f"Usuario encontrado: {user.email}")  # <-- Para verificar que se encuentra el usuario en la BD
    else:
        print("Usuario no encontrado")  # <-- Si no lo encuentra, hay un problema con la consulta

    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        print("Inicio de sesión exitoso")  # <-- Si llega aquí, la contraseña es correcta
        return jsonify({"message": "Inicio de sesión exitoso"}), 200

    print("Credenciales incorrectas")  # <-- Si no pasa, hay un problema con la comparación de contraseñas
    return jsonify({"error": "Credenciales incorrectas"}), 401

@api_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('vqm.login'))

@api_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    nombre = data.get('nombre')
    password = data.get('password')
    
    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error": "El usuario ya existe"}), 400
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    nuevo_usuario = Usuario(email=email, nombre=nombre, password=hashed_password, admin=False)
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({"message": "Usuario registrado exitosamente"}), 201

@api_blueprint.route('/protected', methods=['GET'])
@login_required
def protected():
    return jsonify({"message": f"Bienvenido, {current_user.nombre}"}), 200

# modificar usuario
@api_blueprint.route('/vqm/usuarios/<string:email>', methods=['PUT'])
def update_user(email):
    user = Usuario.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.json

    if "nombre" in data:
        user.nombre = data["nombre"]
    if "admin" in data:
        user.admin = data["admin"]
    if "password" in data:
        user.password = bcrypt.generate_password_hash(data["password"]).decode('utf-8')

    db.session.commit()
    return jsonify({"message": "Usuario actualizado correctamente"}), 200

# borrar usuario
@api_blueprint.route('/vqm/usuarios/<int:id>', methods=['DELETE'])
def delete_user(id):
    # Buscar el usuario en la base de datos
    usuario = Usuario.query.get(id)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Eliminar el usuario de la base de datos
    db.session.delete(usuario)
    db.session.commit()

    return jsonify({"message": f"Usuario con ID {id} eliminado correctamente"}), 200

@api_blueprint.route('/vqm/<string:modelo>', methods=['GET'])
def get_all(modelo):
    if modelo in MODELOS:
        registros = MODELOS[modelo].query.all()
        return jsonify([r.to_dict() for r in registros]), 200
    return jsonify({"error": "Modelo no encontrado"}), 404

# obtener un registro específico por ID
@api_blueprint.route('/vqm/<string:modelo>/<int:id>', methods=['GET'])
def get_by_id(modelo, id):
    if modelo in MODELOS:
        registro = MODELOS[modelo].query.get(id)
        if registro:
            return jsonify(registro.to_dict()), 200
        return jsonify({"error": "Registro no encontrado"}), 404
    return jsonify({"error": "Modelo no encontrado"}), 404

# insertar uno o varios registros en la base de datos
@api_blueprint.route('/vqm/<string:modelo>', methods=['POST'])
def create_record(modelo):
    if modelo in MODELOS:
        data = request.json
        
        # manejo de múltiples registros
        if isinstance(data, list):  # si recibe una lista de registros
            nuevos_registros = [MODELOS[modelo](**registro) for registro in data]
            db.session.add_all(nuevos_registros)
        else:  # si solo recibe un único registro
            nuevo_registro = MODELOS[modelo](**data)
            db.session.add(nuevo_registro)

        db.session.commit()
        return jsonify({"message": f"Registro(s) agregado(s) en {modelo}"}), 201
    
    return jsonify({"error": "Modelo no encontrado"}), 404

# actualizar vqm temperatura (usa "maquina")
@api_blueprint.route('/vqm/<string:modelo>/<string:maquina>', methods=['PUT'])
def update_record_by_maquina(modelo, maquina):
    if modelo in MODELOS:
        registro = MODELOS[modelo].query.filter_by(maquina=maquina).first()
        if not registro:
            return jsonify({"error": "Registro no encontrado"}), 404
        
        data = request.json
        for key, value in data.items():
            setattr(registro, key, value)
        
        db.session.commit()
        return jsonify({"message": f"Registro {maquina} actualizado en {modelo}"}), 200
    return jsonify({"error": "Modelo no encontrado"}), 404

# actualizar datos mdm (usa "masico")
@api_blueprint.route('/vqm/<string:modelo>/<string:masico>', methods=['PUT'])
def update_record_by_masico(modelo, masico):
    if modelo in MODELOS:
        registro = MODELOS[modelo].query.filter_by(masico=masico).first()
        if not registro:
            return jsonify({"error": "Registro no encontrado"}), 404
        
        data = request.json
        for key, value in data.items():
            setattr(registro, key, value)
        
        db.session.commit()
        return jsonify({"message": f"Registro {masico} actualizado en {modelo}"}), 200
    return jsonify({"error": "Modelo no encontrado"}), 404

# eliminar un registro por ID
@api_blueprint.route('/vqm/<string:modelo>/<int:id>', methods=['DELETE'])
def delete_record(modelo, id):
    if modelo in MODELOS:
        registro = MODELOS[modelo].query.get(id)
        if not registro:
            return jsonify({"error": "Registro no encontrado"}), 404
        
        db.session.delete(registro)
        db.session.commit()
        return jsonify({"message": f"Registro {id} eliminado de {modelo}"}), 200
    return jsonify({"error": "Modelo no encontrado"}), 404
