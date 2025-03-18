from flask import Blueprint, request, jsonify
from .models import db, Usuario, CorreoUsuario, PermisoUsuario, VqmTemperatura, TratamientoNCVqm, DatosMdms, VqmMdm, VqmTemperaturaMI10

# creamos la Blueprint llamada "vqm" que agrupará todas las rutas de la API (__init__.py)
# para integrarse con la aplicación Flask
api_blueprint = Blueprint('vqm', __name__)

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

# obtener todos los registros de cualquier tabla
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

# actualizar un registro existente en la base de datos
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

# actualizar un registro existente en la base de datos
@api_blueprint.route('/vqm/<string:modelo>/<string:masico>', methods=['PUT'])
def update_record_by_masico(modelo, masico):
    if modelo in MODELOS:
        registro = MODELOS[modelo].query.filter_by(masico=masico).first()  # CAMBIO AQUÍ
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
