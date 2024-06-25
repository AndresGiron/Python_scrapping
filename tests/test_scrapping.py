import pytest
from scrapping import scrapping  # Importa tu función scrapping desde el archivo scrapping.py

import logging

# Configura el logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

actor_ofendido = 'input[aria-label="Cédula/RUC/Pasaporte del actor"]'
demandado_procesado = 'input[aria-label="Cédula/RUC/Pasaporte del demandado"]'
# Definición de la función de prueba para ejecutar múltiples consultas en paralelo

@pytest.mark.parametrize("sujeto,codigo_cedula", [
    (actor_ofendido, "0992339411001"),
    (demandado_procesado, "1791251237001"),
    (actor_ofendido, "0968599020001"),
    (demandado_procesado, "0968599020001"),#
    (actor_ofendido, "0968599020001"),
    (demandado_procesado, "1791251237001"),
    (actor_ofendido, "0968599020001"),
    (demandado_procesado, "0968599020001"),#
    (actor_ofendido, "0968599020001"),
    (demandado_procesado, "1791251237001"),
    (actor_ofendido, "0968599020001"),
    (demandado_procesado, "0968599020001"),#
    (actor_ofendido, "0992339411001"),
    (demandado_procesado, "1791251237001"),
    (actor_ofendido, "0968599020001"),
])
def test_scrapping(sujeto, codigo_cedula):
    try:
        scrapping(sujeto, codigo_cedula)
    except Exception as e:
        pytest.fail(f"Scrapping failed for {sujeto} with {codigo_cedula}: {e}")




