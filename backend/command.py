import click
from flask.cli import with_appcontext
from utils.actualizar_resumen_temp import actualizar_resumen_temperatura_desde_mediciones

@click.command("actualizar-resumen-temp")
@with_appcontext
def actualizar_resumen_temp():
    """Genera los resúmenes de VQM Temperatura desde mediciones."""
    actualizar_resumen_temperatura_desde_mediciones()