from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict, List


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
    gustos: List[str]
    disgustos: List[str]
    alergias: List[str]
