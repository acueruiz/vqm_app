from flask import Blueprint, request, jsonify, session, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from .models import db, Usuario, CorreoUsuario, PermisoUsuario, VqmTemperatura, TratamientoNCVqm, DatosMdms, VqmMdm, VqmTemperaturaMI10

bcrypt = Bcrypt()

# creamos la Blueprint llamada "vqm" que agrupará todas las rutas de la API (__init__.py) para integrarse con la aplicación Flask
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

# iniciar sesión con usuario previamente creado
@api_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    print(f"Intentando login con: {email} - {password}")

    user = Usuario.query.filter_by(email=email).first()

    if user:
        print(f"Usuario encontrado: {user.email}")
    else:
        print("Usuario no encontrado")

    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        print("Inicio de sesión exitoso")

        # Obtener los permisos relacionados
        permisos = [permiso.departamento for permiso in user.permisos]

        return jsonify({
            "message": "Inicio de sesión exitoso",
            "email": user.email,
            "nombre": user.nombre,
            "id": user.id,
            "admin": user.admin,
            "permisos": permisos
        }), 200

    print("Credenciales incorrectas")
    return jsonify({"error": "Credenciales incorrectas"}), 401

@api_blueprint.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"message": "Sesión cerrada exitosamente"}), 200

@api_blueprint.route('/protected', methods=['GET'])
@login_required
def protected():
    return jsonify({"message": f"Bienvenido, {current_user.nombre}"}), 200

# crear un usuario
@api_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    nombre = data.get('nombre')
    password = data.get('password')

    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error": "El usuario ya existe"}), 400
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    nuevo_usuario = Usuario(
        email=email,
        nombre=nombre,
        password=hashed_password
    )
    
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"message": "Usuario registrado exitosamente"}), 201

# modificar un usuario
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

# borrar un usuario
@api_blueprint.route('/vqm/usuarios/<int:id>', methods=['DELETE'])
def delete_user(id):
    # buscar el usuario en la base de datos
    usuario = Usuario.query.get(id)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # eliminar el usuario de la base de datos
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

# actualizar vqm temperatura (usando "máquina")
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

# actualizar datos mdm (usa "másico")
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
@api_blueprint.route('/vqm/<string:modelo>/<int:id>', methods=['DELETE']) # por implementar!!!! <--------------------------------------
def delete_record(modelo, id):
    if modelo in MODELOS:
        registro = MODELOS[modelo].query.get(id)
        if not registro:
            return jsonify({"error": "Registro no encontrado"}), 404
        
        db.session.delete(registro)
        db.session.commit()
        return jsonify({"message": f"Registro {id} eliminado de {modelo}"}), 200
    return jsonify({"error": "Modelo no encontrado"}), 404

# rutas para gestión de correos por departamento

@api_blueprint.route('/correos/departamento/<string:departamento>', methods=['GET'])
def get_correos_por_departamento(departamento):
    correos = CorreoUsuario.query.filter_by(departamento=departamento).all()
    return jsonify([c.to_dict() for c in correos]), 200

@api_blueprint.route('/correos', methods=['POST'])
def add_correo():
    data = request.json
    nuevo = CorreoUsuario(
        email=data["email"],
        nombre=data.get("nombre", ""),
        departamento=data["departamento"],
        tipo_notificacion=data.get("tipo_notificacion", "vqm_nc"),
        activo=data.get("activo", True)
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"message": "Correo añadido"}), 201

@api_blueprint.route('/correos/<int:id>', methods=['DELETE'])
def delete_correo(id):
    correo = CorreoUsuario.query.get(id)
    if not correo:
        return jsonify({"error": "Correo no encontrado"}), 404
    db.session.delete(correo)
    db.session.commit()
    return jsonify({"message": "Correo eliminado"}), 200