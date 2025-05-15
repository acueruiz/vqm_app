from backend.database import db
from backend.models import VqmTemperaturaMI10, VqmTemperaturaResumen
from sqlalchemy import func
from datetime import date

def actualizar_resumen_temperatura_desde_mediciones():
    print("Generando resúmenes a partir de las 15 mediciones...")

    # agrupar por maquina y fecha
    agrupados = db.session.query(
        VqmTemperaturaMI10.titulo,
        VqmTemperaturaMI10.fecha,
        func.count().label("num_registros"),
        func.bool_or(VqmTemperaturaMI10.vqm_conforme == False).label("hay_no_conforme")
    ).group_by(
        VqmTemperaturaMI10.titulo,
        VqmTemperaturaMI10.fecha
    ).having(func.count() == 15).all()

    for titulo_raw, fecha_grupo, num_registros, hay_nc in agrupados:
        # normalizar nombre de máquina
        maquina = titulo_raw.strip().upper()

        # verificar si ya hay resumen creado
        resumen_existente = db.session.query(VqmTemperaturaResumen).filter_by(
            maquina=maquina,
            grupo_fecha=fecha_grupo,
            origen="medicion"
        ).first()

        estado = "NO CONFORME" if hay_nc else "CONFORME"

        if resumen_existente:
            resumen_existente.estado = estado
            resumen_existente.fecha_evento = date.today()
        else:
            nuevo_resumen = VqmTemperaturaResumen(
                maquina=maquina,
                grupo_fecha=fecha_grupo,
                estado=estado,
                origen="medicion",
                fecha_evento=date.today()
            )
            db.session.add(nuevo_resumen)

    db.session.commit()
    print("Resúmenes actualizados correctamente.")