from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict


class FoodItem(TypedDict):
    nombre: str
    grupo: str
    calorias: float
    grasas: float
    proteinas: float
    carbohidratos: float


@dataclass(frozen=True)
class SubjectProfile:
    sujeto_id: int
    edad: int
    calorias: float
    gustos: list[str]
    disgustos: list[str]
    alergias: list[str]
