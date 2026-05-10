import random

from diet_bao.encoding import INDIVIDUAL_LENGTH, create_individual


def _foods():
    def item(nombre, grupo, cal, p, c, g):
        return {
            "nombre": nombre,
            "grupo": grupo,
            "calorias": float(cal),
            "proteinas": float(p),
            "carbohidratos": float(c),
            "grasas": float(g),
        }

    return [
        item("Apple", "FA", 52, 0.3, 14, 0.2),
        item("Banana", "FA", 89, 1.1, 23, 0.3),
        item("Candy", "S1", 400, 0.0, 100, 0.0),
        item("Orange juice", "FE", 45, 0.7, 10, 0.2),
        item("Fruit juice", "FC", 50, 0.1, 12, 0.0),
        item("Cow milk", "BA", 60, 3.2, 4.8, 3.3),
        item("Yogurt drink", "BH", 70, 3.5, 8, 2.0),
        item("Tea", "PA", 2, 0.0, 0.5, 0.0),
        item("Egg", "C1", 78, 6.0, 0.6, 5.0),
        item("Cereal", "A1", 110, 4.0, 22.0, 1.0),
        item("Bacon", "MAA", 90, 6.0, 0.0, 7.0),
        item("Water", "P1", 0, 0.0, 0.0, 0.0),
        item("Rice", "AC", 130, 2.7, 28.0, 0.3),
        item("Chicken", "M1", 165, 31.0, 0.0, 3.6),
        item("Broccoli", "V1", 55, 3.7, 11.0, 0.6),
        item("Bread", "AF", 80, 3.0, 15.0, 1.0),
    ]


def test_create_individual_length():
    individual = create_individual(_foods(), edad=25, rng=random.Random(0))
    assert len(individual) == INDIVIDUAL_LENGTH
