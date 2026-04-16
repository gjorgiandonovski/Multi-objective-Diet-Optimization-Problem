"""Project constants used by legacy helper utilities.

This module mirrors the meal/group structure already encoded in
`src.utilidades.encoding` so older helpers can keep importing
`GruposComida`, `DIAS_SEMANA`, and `COMIDAS`.
"""

DIAS_SEMANA = (
    "Lunes",
    "Martes",
    "Miercoles",
    "Jueves",
    "Viernes",
    "Sabado",
    "Domingo",
)


COMIDAS = (
    {"nombre": "Snack 1", "num_alimentos": 1},
    {"nombre": "Bebida desayuno", "num_alimentos": 1},
    {"nombre": "Desayuno", "num_alimentos": 2},
    {"nombre": "Bebida almuerzo", "num_alimentos": 1},
    {"nombre": "Almuerzo", "num_alimentos": 2},
    {"nombre": "Snack 2", "num_alimentos": 1},
    {"nombre": "Bebida cena", "num_alimentos": 1},
    {"nombre": "Cena", "num_alimentos": 2},
)


class GruposComida:
    class Frutas:
        FRUTAS = ("F",)
        FRUTAS_GENERALES = ("FA",)
        JUGOS_DE_FRUTAS = ("FC",)
        ZUMOS = ("FE",)

    class Bebidas:
        BEBIDAS = ("P",)

        class BebidasEnPolvoEsenciasInfusiones:
            BEBIDAS_EN_POLVO_ESENCIAS_INFUSIONES = ("PA",)

    class Alcohol:
        ALCOHOL = ("Q",)

    class Lacteos:
        class LecheVaca:
            LECHE_VACA = ("BA",)

        BEBIDAS_LACTEAS = ("BH",)

    class Azucares:
        AZUCARES = ("S",)

    class Cereales:
        CEREALES = ("A",)
        ARROZ = ("AC",)
        PASTA = ("AD",)
        PIZZAS = ("AE",)
        PANES = ("AF",)

    class Huevos:
        HUEVOS = ("C",)

    class Carne:
        class CarneGeneral:
            BACON = ("MAA",)
