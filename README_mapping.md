# Database Mapping Guide

This project does **not** require translation for food names in the provided dump.
The key task is to understand table/column meanings and how `grupo` codes map to meal constraints.

## Main tables

### `comida`
- `id`: food identifier (primary key)
- `nombre`: food name
- `grupo`: food group code (used to filter valid foods per meal slot)
- `proteinas`, `grasas`, `carbohidratos`: grams of macronutrients
- `calorias`: kcal

### `sujetos`
- `id`: subject identifier
- `peso`, `altura`, `edad`: profile values
- `sexo`: `H` (male), `M` (female)
- `actividad`: activity level (`Sedentario`, `Ligero`, `Moderado`, `Alto`, `Muy Alto`)

### `sujetos_calorias` (view)
- Computes per-subject target daily calories from profile and activity.

### `sujetos_gustos`, `sujetos_disgustos`, `sujetos_alergias`
- Relationship tables with:
  - `sujeto_id`
  - `grupo`
- These codes represent preferred, disliked, or restricted food groups for each subject.

## Meal-slot mapping used in code

From `src/utilidades/funciones_auxiliares.py`, slots are selected by `grupo` prefixes:

- `snacks`: groups starting with `F` or `S`
- `bebida_desayuno`: groups starting with `BA`, `BH`, `PA`, `FE`, `FC`
- `desayuno` foods: groups starting with `A`, `C`, `FA`, `MAA`
  - excludes exact groups `AC`, `AD`, `AE`
- `bebidas` (lunch/dinner drinks): starts with `P`, `FC`, `FE`
  - excludes `PA`
  - includes alcohol `Q*` only if age >= 18
- `almuerzo_cena` foods: excludes drink/sugar/breakfast-drink groups, while allowing cereal subgroups `AC`, `AD`, `AE`, `AF`

## Common code prefixes seen in this project

- `A*`: cereals/bakery family
  - examples used directly: `AC` (rice), `AD` (pasta), `AE` (pizza), `AF` (bread)
- `C*`: eggs family (`C`)
- `F*`: fruits family
  - examples: `FA` (general fruits), `FC` (fruit juices), `FE` (juices/zumos)
- `B*`: dairy family
  - `BA` (cow milk), `BH` (dairy beverages)
- `P*`: beverages family
  - `PA` is powder/infusions subfamily (handled separately)
- `Q*`: alcohol family
- `M*`: meats family
  - `MAA`: bacon subfamily
- `S*`: sugars/sweets family

## Useful SQL to inspect mapping quickly

```sql
-- 1) See all group codes and counts
SELECT grupo, COUNT(*) AS n
FROM comida
GROUP BY grupo
ORDER BY grupo;

-- 2) See top-level prefixes and counts
SELECT LEFT(grupo, 1) AS pref1, COUNT(*) AS n
FROM comida
GROUP BY LEFT(grupo, 1)
ORDER BY pref1;

-- 3) Sample foods for a specific group code (replace 'AC')
SELECT id, nombre, grupo, calorias, proteinas, carbohidratos, grasas
FROM comida
WHERE grupo = 'AC'
LIMIT 20;

-- 4) Subject preferences/restrictions by group code
SELECT 'gusto' AS tipo, sujeto_id, grupo FROM sujetos_gustos
UNION ALL
SELECT 'disgusto', sujeto_id, grupo FROM sujetos_disgustos
UNION ALL
SELECT 'alergia', sujeto_id, grupo FROM sujetos_alergias
ORDER BY sujeto_id, tipo, grupo;
```

## Encoding reference

The weekly encoding implemented in `src/utilidades/encoding.py` uses:
- `L = 77` genes (`7 days * 11 items/day`)
- Daily order:
  - `gsnack1, gdrinkB, gfoodB1, gfoodB2, gdrinkL, gfoodL1, gfoodL2, gsnack2, gdrinkD, gfoodD1, gfoodD2`
