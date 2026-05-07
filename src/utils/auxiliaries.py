# helper functions

from utils.database import comida_basedatos
from utils.constants import GruposComida, DIAS_SEMANA, COMIDAS

comida_bd = None


def obtener_comida_bd():
    """Load food data from the database only when needed."""
    global comida_bd
    if comida_bd is None:
        comida_bd = comida_basedatos()
    return comida_bd

def calculo_macronutrientes(proteinas, carbohidratos, grasas):
    """Calculate the percentage of calories coming from each macronutrient."""

    calorias_proteinas = proteinas * 4
    calorias_carbohidratos = carbohidratos * 4
    calorias_grasas = grasas * 9

    total_calorias_macronutrientes = calorias_proteinas + calorias_carbohidratos + calorias_grasas

    if total_calorias_macronutrientes == 0:
        return 0.0, 0.0, 0.0

    porcentaje_proteinas = (calorias_proteinas / total_calorias_macronutrientes) * 100
    porcentaje_carbohidratos = (calorias_carbohidratos / total_calorias_macronutrientes) * 100
    porcentaje_grasas = (calorias_grasas / total_calorias_macronutrientes) * 100

    return porcentaje_proteinas, porcentaje_carbohidratos, porcentaje_grasas


def filtrar_comida(comida_bd=None, tipo=None, edad=None):
    """Filter foods by meal type and user age."""
    if comida_bd is None:
        comida_bd = obtener_comida_bd()
    if tipo is None or edad is None:
        raise ValueError("`tipo` and `edad` are required.")

    if tipo == "almuerzo_cena":
        return [
            i for i, item in enumerate(comida_bd) if not item["grupo"].startswith(
                (
                    GruposComida.Frutas.JUGOS_DE_FRUTAS[0],  # "FC"
                    GruposComida.Frutas.ZUMOS[0],  # "FE"
                    GruposComida.Bebidas.BEBIDAS[0],  # "P"
                    GruposComida.Alcohol.ALCOHOL[0],  # "Q"
                    GruposComida.Lacteos.LecheVaca.LECHE_VACA[0],  # "BA"
                    GruposComida.Lacteos.BEBIDAS_LACTEAS[0],  # "BH"
                    GruposComida.Bebidas.BebidasEnPolvoEsenciasInfusiones.BEBIDAS_EN_POLVO_ESENCIAS_INFUSIONES[0],  # "PA"
                    GruposComida.Azucares.AZUCARES[0],  # "S"
                    GruposComida.Cereales.CEREALES[0],  # "A"
                )
            ) or item["grupo"] in {
                GruposComida.Cereales.ARROZ[0],  # "AC"
                GruposComida.Cereales.PASTA[0],  # "AD"
                GruposComida.Cereales.PIZZAS[0],  # "AE"
                GruposComida.Cereales.PANES[0],  # "AF"
            }
        ]

    if tipo == "bebidas":
        bebidas = [
            i for i, item in enumerate(comida_bd) if item["grupo"].startswith(
                (
                    GruposComida.Bebidas.BEBIDAS[0],  # "P"
                    GruposComida.Frutas.JUGOS_DE_FRUTAS[0],  # "FC"
                    GruposComida.Frutas.ZUMOS[0],  # "FE"
                )
            ) and not item["grupo"].startswith(
                GruposComida.Bebidas.BebidasEnPolvoEsenciasInfusiones.BEBIDAS_EN_POLVO_ESENCIAS_INFUSIONES[0]  # "PA"
            )
        ]
        if edad >= 18:
            bebidas_alcoholicas = [
                i for i, item in enumerate(comida_bd) if item["grupo"].startswith(
                    GruposComida.Alcohol.ALCOHOL[0]  # "Q"
                )
            ]
            bebidas.extend(bebidas_alcoholicas)
        return bebidas

    if tipo == "desayuno":
        return [
            i for i, item in enumerate(comida_bd) if item["grupo"].startswith(
                (
                    GruposComida.Cereales.CEREALES[0],  # "A"
                    GruposComida.Huevos.HUEVOS[0],  # "C"
                    GruposComida.Frutas.FRUTAS_GENERALES[0],  # "FA"
                    GruposComida.Carne.CarneGeneral.BACON[0],  # "MAA"
                )
            ) and item["grupo"] not in {
                GruposComida.Cereales.ARROZ[0],  # "AC"
                GruposComida.Cereales.PASTA[0],  # "AD"
                GruposComida.Cereales.PIZZAS[0],  # "AE"
            }
        ]

    if tipo == "bebida_desayuno":
        return [
            i for i, item in enumerate(comida_bd) if item["grupo"].startswith(
                (
                    GruposComida.Lacteos.LecheVaca.LECHE_VACA[0],  # "BA"
                    GruposComida.Lacteos.BEBIDAS_LACTEAS[0],  # "BH"
                    GruposComida.Bebidas.BebidasEnPolvoEsenciasInfusiones.BEBIDAS_EN_POLVO_ESENCIAS_INFUSIONES[0],  # "PA"
                    GruposComida.Frutas.ZUMOS[0],  # "FE"
                    GruposComida.Frutas.JUGOS_DE_FRUTAS[0],  # "FC"
                )
            )
        ]

    if tipo == "snacks":
        return [
            i for i, item in enumerate(comida_bd) if item["grupo"].startswith(
                (
                    GruposComida.Frutas.FRUTAS[0],  # "F"
                    GruposComida.Azucares.AZUCARES[0],  # "S"
                )
            )
        ]

    raise ValueError(f"Unsupported meal type: {tipo}")


def traducir_solucion(solucion, comida_bd=None):
    """Convert the numeric solution into foods with their nutrient data."""
    if comida_bd is None:
        comida_bd = obtener_comida_bd()

    menu = {}
    datos_dia = {dia: {"calorias": 0, "proteinas": 0, "carbohidratos": 0, "grasas": 0} for dia in DIAS_SEMANA}
    
    indice = 0
    for dia in DIAS_SEMANA:
        menu[dia] = {}

        for comida in COMIDAS:
            num_alimentos = comida["num_alimentos"]
            alimentos = []
            calorias_totales = 0

            for _ in range(num_alimentos):

                # Map the index to a concrete food item
                if indice < len(solucion):
                    idx = int(solucion[indice])  
                    alimento = comida_bd[idx]
                    nombre_completo = f"- {alimento['nombre']} ({alimento['grupo']})"
                    alimentos.append(nombre_completo)

                    # Accumulate calories and macronutrients for the food item
                    calorias_totales += alimento["calorias"]
                    datos_dia[dia]["calorias"] += alimento["calorias"]
                    datos_dia[dia]["proteinas"] += alimento["proteinas"]
                    datos_dia[dia]["carbohidratos"] += alimento["carbohidratos"]
                    datos_dia[dia]["grasas"] += alimento["grasas"]

                    indice += 1

            menu[dia][comida["nombre"]] = (alimentos, calorias_totales)
    
    # Compute macronutrient percentages for each day
    for dia in DIAS_SEMANA:
        calorias = datos_dia[dia]["calorias"]

        if calorias > 0:
            datos_dia[dia]["porcentaje_proteinas"], datos_dia[dia]["porcentaje_carbohidratos"], datos_dia[dia]["porcentaje_grasas"] = \
                calculo_macronutrientes(datos_dia[dia]["proteinas"], datos_dia[dia]["carbohidratos"], datos_dia[dia]["grasas"])
        else:
            datos_dia[dia]["porcentaje_proteinas"] = datos_dia[dia]["porcentaje_carbohidratos"] = datos_dia[dia]["porcentaje_grasas"] = 0

    return menu, datos_dia
