from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import db  # Importar la base de datos
from flask_login import UserMixin  # Asegura compatibilidad con Flask-Login

# clase Base para evitar repetir `id`
class BaseModel(db.Model):
    __abstract__ = True  # No se crea tabla para esta clase
    id = Column(Integer, primary_key=True, autoincrement=True)

    def to_dict(self):
        """Convierte cualquier modelo a diccionario automáticamente."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class Usuario(UserMixin, db.Model):  # Hereda de UserMixin
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    nombre = Column(String, nullable=False)
    password = Column(String, nullable=False)
    admin = Column(Boolean, default=False)

    correos = relationship("CorreoUsuario", back_populates="usuario", cascade="all, delete")
    permisos = relationship("PermisoUsuario", back_populates="usuario", cascade="all, delete")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "nombre": self.nombre,
            "admin": self.admin,
            # "password": self.password --> se puede omitir la contraseña por seguridad
        }

# modelo de correos de usuarios
class CorreoUsuario(BaseModel):
    __tablename__ = "correos_usuarios"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True)
    email = Column(String, nullable=False)
    nombre = Column(String, nullable=True)
    departamento = Column(String, nullable=False)
    tipo_notificacion = Column(String, nullable=False)  # ej: "VQM_Bascula", "VQM_MDM"
    activo = Column(Boolean, default=True)

    usuario = relationship("Usuario", back_populates="correos", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "email": self.email,
            "nombre": self.nombre,
            "departamento": self.departamento,
            "tipo_notificacion": self.tipo_notificacion,
            "activo": self.activo
        }

# modelo de Permisos de Usuarios
class PermisoUsuario(BaseModel):
    __tablename__ = "permisos_usuarios"

    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"))
    grupo = Column(String, nullable=False)
    permiso_edicion = Column(Boolean, default=False)
    permiso_desbloqueo = Column(Boolean, default=False)

    usuario = relationship("Usuario", back_populates="permisos")

# moodelo de VQM Temperatura
class VqmTemperatura(BaseModel):
    __tablename__ = "vqm_temperatura"

    maquina = Column(String, nullable=False)
    apelacion = Column(String)
    receta = Column(String)
    temperatura_caida = Column(Float)
    media_calificacion = Column(Float)
    fecha_calificacion = Column(Date)
    operario = Column(String)

    def to_dict(self):
        data = super().to_dict()
        data["fecha_calificacion"] = self.fecha_calificacion.strftime('%Y-%m-%d') if self.fecha_calificacion else None
        return data

# modelo de Tratamiento NC (No Conformidad) en VQM
class TratamientoNCVqm(BaseModel):
    __tablename__ = "tratamiento_nc_vqm"

    titulo = Column(String)
    fecha = Column(Date)
    trimestre_anio = Column(String)
    instrumento_medida = Column(String)
    maquina = Column(String)
    operario = Column(String)
    vqm_conforme = Column(Boolean)
    descripcion_intervencion = Column(String)
    resultado_intervencion = Column(String)
    efectos_proceso = Column(String)
    efectos_producto = Column(String)
    acciones_nc = Column(String)
    nc_validada = Column(Boolean)
    fecha_acciones = Column(Date)

    def to_dict(self):
        data = super().to_dict()
        data["fecha"] = self.fecha.strftime('%Y-%m-%d') if self.fecha else None
        data["fecha_acciones"] = self.fecha_acciones.strftime('%Y-%m-%d') if self.fecha_acciones else None
        return data

# modelo de Datos MDMS
class DatosMdms(BaseModel):
    __tablename__ = "datos_mdms"

    masico = Column(String)
    kw = Column(Float)
    id_dosificador = Column(String)
    valor_test1 = Column(Float)
    tolerancia1 = Column(Float)
    valor_test2 = Column(Float)
    tolerancia2 = Column(Float)
    circuito = Column(String)
    bascula = Column(String)
    id_bascula = Column(String)
    id_masas_patron = Column(String)
    vr_masas_patron = Column(Float)
    tolerancia_vr = Column(Float)
    tolerancia_cero = Column(Float)

# modelo de VQM MDM
class VqmMdm(BaseModel):
    __tablename__ = "vqm_mdm"

    titulo = Column(String)
    fecha = Column(Date)
    operador = Column(String)
    valor_bascula = Column(Float)
    valor_cero_bascula = Column(Float)
    vqm_bascula_conforme = Column(Boolean)
    error_cantidad1 = Column(Float)
    error_cantidad2 = Column(Float)
    vqm_masico_conforme = Column(Boolean)
    cant1_verif1_valor_masico = Column(Float)
    cant1_verif1_valor_bascula = Column(Float)
    cant1_verif2_valor_masico = Column(Float)
    cant1_verif2_valor_bascula = Column(Float)
    cant2_verif1_valor_masico = Column(Float)
    cant2_verif1_valor_bascula = Column(Float)
    cant2_verif2_valor_masico = Column(Float)
    cant2_verif2_valor_bascula = Column(Float)

    def to_dict(self):
        data = super().to_dict()
        data["fecha"] = self.fecha.strftime('%Y-%m-%d') if self.fecha else None
        return data

# modelo de VQM Temperatura MI10
class VqmTemperaturaMI10(BaseModel):
    __tablename__ = "vqm_temperatura_mi10"

    titulo = Column(String)
    fecha = Column(Date)
    num_ml_dia = Column(Integer)
    temperatura_mi = Column(Float)
    temperatura_pistola = Column(Float)
    diferencia_temperaturas = Column(Float)
    trimestre_anio = Column(String)
    desviacion_tmi = Column(Float)
    desviacion_tmi_tr = Column(Float)
    media_tmi_tr = Column(Float)
    lsx = Column(Float)
    lix = Column(Float)
    vqm_conforme = Column(Boolean)
    operario = Column(String)

    def to_dict(self):
        data = super().to_dict()
        data["fecha"] = self.fecha.strftime('%Y-%m-%d') if self.fecha else None
        return data
