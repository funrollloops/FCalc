#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import timedelta
from math import ceil
from queue import Queue
from typing import NamedTuple

secs = lambda s: timedelta(seconds=s)


class Building(NamedTuple):
  name: str
  crafting_speed: float
  productivity: float = 1.
  slots: int = 0


class Module(NamedTuple):
  name: str
  crafting_speed: float = 1
  productivity: float = 1
  power: float = 1


class ModdedBuilding:
  def __init__(self, name: str, building: Building, modules: list[Module]):
    assert(len(modules) <= building.slots), f"{building.name} only has {building.slots} slots!"
    self.building = building
    self.modules = modules
    self.name = name
    self.productivity = 1 + sum(m.productivity for m in modules)
    self.crafting_speed = building.crafting_speed * (1 + sum(m.crafting_speed for m in modules))


PRODUCTIVITY1 = Module('prod-1', crafting_speed=-0.05, productivity=0.04)
PRODUCTIVITY2 = Module('prod-2', crafting_speed=-0.10, productivity=0.06)
SPEED1 = Module('speed-1', crafting_speed=0.2, power=0.5)
SPEED2 = Module('speed-2', crafting_speed=0.3, power=0.6)
STONE_FURNACE = Building('stone-furnace', 1)
STEEL_FURNACE = Building('steel-furnace', 2)
ELECTRIC_FURNACE = Building('electric-furnace', 2, slots=2)
FURNACE = STEEL_FURNACE

ASSEMBLER1 = Building('assembler-1', .5)
ASSEMBLER2 = Building('assembler-2', .75, slots=2)
ASSEMBLER = ModdedBuilding('assembler-2:2×prod1', ASSEMBLER2, [PRODUCTIVITY1, PRODUCTIVITY1])

CHEMICAL_PLANT = Building('chemical-plant', 1)
ELECTRIC_MINING_DRILL = Building('electric-mining-drill', .5, slots=3)
WATER_PUMP = Building('water-pump', 1)


class Ingredient(NamedTuple):
  name: str
  qty: int


class Recipe(NamedTuple):
  name: str
  building: Building
  output_qty: int
  time: timedelta
  ingredients: list[Ingredient]


RAWS = set(['petroleum-gas'])

RECIPES = [
    Recipe('production-science-pack', ASSEMBLER, 3, secs(21), [
        Ingredient('rail', 30),
        Ingredient('electric-furnace', 1),
        Ingredient('productivity-module-1', 1),
    ]),
    Recipe('rail', ASSEMBLER, 2, secs(.5), [
        Ingredient('stone', 1),
        Ingredient('steel-plate', 1),
        Ingredient('iron-stick', 1)
    ]),
    Recipe('electric-furnace', ASSEMBLER, 1, secs(5), [
        Ingredient('steel-plate', 10),
        Ingredient('advanced-circuit', 5),
        Ingredient('stone-brick', 10)
    ]),
    Recipe('productivity-module-1', ASSEMBLER, 1, secs(15), [
        Ingredient('electronic-circuit', 5),
        Ingredient('advanced-circuit', 5)
    ]),
    Recipe('iron-stick', ASSEMBLER, 2, secs(.5), [Ingredient('iron-plate', 1)]),
    Recipe('chemical-science-pack', ASSEMBLER, 2, secs(24), [
        Ingredient('sulfur', 1),
        Ingredient('advanced-circuit', 3),
        Ingredient('engine-unit', 2)
    ]),
    Recipe('sulfur', CHEMICAL_PLANT, 2, secs(1),
           [Ingredient('water', 30),
            Ingredient('petroleum-gas', 30)]),
    Recipe('advanced-circuit', ASSEMBLER, 1, secs(6), [
        Ingredient('plastic-bar', 2),
        Ingredient('copper-cable', 4),
        Ingredient('electronic-circuit', 2)
    ]),
    Recipe('engine-unit', ASSEMBLER, 1, secs(10), [
        Ingredient('steel-plate', 1),
        Ingredient('iron-gear-wheel', 1),
        Ingredient('pipe', 2)
    ]),
    Recipe('plastic-bar', CHEMICAL_PLANT, 2, secs(1),
           [Ingredient('coal', 1),
            Ingredient('petroleum-gas', 20)]),
    Recipe('electronic-circuit', ASSEMBLER, 1, secs(.5),
           [Ingredient('iron-plate', 1),
            Ingredient('copper-cable', 3)]),
    Recipe('copper-cable', ASSEMBLER, 2, secs(.5),
           [Ingredient('copper-plate', 1)]),
    Recipe('steel-plate', FURNACE, 1, secs(16), [Ingredient('iron-plate', 5)]),
    Recipe('iron-gear-wheel', ASSEMBLER, 1, secs(.5),
           [Ingredient('iron-plate', 2)]),
    Recipe('pipe', ASSEMBLER, 1, secs(.5), [Ingredient('iron-plate', 1)]),
    Recipe('iron-plate', STEEL_FURNACE, 1, secs(3.2),
           [Ingredient('iron-ore', 1)]),
    Recipe('copper-plate', STEEL_FURNACE, 1, secs(3.2),
           [Ingredient('copper-ore', 1)]),
    Recipe('iron-ore', ELECTRIC_MINING_DRILL, 1, secs(1), []),
    Recipe('copper-ore', ELECTRIC_MINING_DRILL, 1, secs(1), []),
    Recipe('stone', ELECTRIC_MINING_DRILL, 1, secs(1), []),
    Recipe('coal', ELECTRIC_MINING_DRILL, 1, secs(1), []),
    Recipe('water', WATER_PUMP, 1200, secs(1), []),
    Recipe('military-science-pack', ASSEMBLER, 2, secs(10), [
        Ingredient('piercing-rounds-magazine', 1),
        Ingredient('grenade', 1),
        Ingredient('wall', 2),
    ]),
    Recipe('piercing-rounds-magazine', ASSEMBLER, 1, secs(4), [
        Ingredient('copper-plate', 5),
        Ingredient('steel-plate', 1),
        Ingredient('firearm-magazine', 1),
    ]),
    Recipe('grenade', ASSEMBLER, 1, secs(8), [
        Ingredient('coal', 10),
        Ingredient('iron-plate', 5),
    ]),
    Recipe('wall', ASSEMBLER, 1, secs(0.5), [
        Ingredient('stone-brick', 5),
    ]),
    Recipe('firearm-magazine', ASSEMBLER, 1, secs(1), [
        Ingredient('iron-plate', 4),
    ]),
    Recipe('stone-brick', FURNACE, 1, secs(3.2), [
        Ingredient('stone', 2),
    ]),
]

RECIPES = {r.name: r for r in RECIPES}


def check_recipes():
  result = True
  for r in RECIPES.values():
    for i in r.ingredients:
      if i.name in RECIPES or i.name in RAWS:
        continue
      print(f"Recipe {r.name} references non-existent ingredient {i.name}")
      result = False
  return result


def calculate_recursive(name: str, items_per_minute: float):

  @dataclass
  class Totals:
    buildings: float = 0
    items_per_sec: float = 0

  totals: dict[str, Totals] = {}

  def process(name: str, items_per_sec: float, depth: int):
    totals.setdefault(name, Totals())
    totals[name].items_per_sec += items_per_sec
    if name in RAWS:
      return
    recipe = RECIPES[name]
    # Calculate how many assemblers are needed.
    per_building_per_sec = (recipe.output_qty / recipe.time.total_seconds() *
                            recipe.building.crafting_speed * recipe.building.productivity)
    buildings = items_per_sec / per_building_per_sec
    if depth < 0:
      quiet = True
    else:
      quiet = recipe.building in (ELECTRIC_MINING_DRILL, STEEL_FURNACE,
                                  STONE_FURNACE, WATER_PUMP)
      print(
          "%s% 5.1f/s % 5.1f🏭 %s (%s)" %
          ('  ' * depth, items_per_sec, buildings, name, recipe.building.name))
    totals[name].buildings += buildings
    # Calculate demand on the inputs.
    for input in recipe.ingredients:
      process(input.name, input.qty * items_per_sec / recipe.output_qty / recipe.building.productivity,
              depth + 1 if not quiet else -1000)

  print(f"# Factory for {items_per_minute} {name} per minute")
  process(name, items_per_minute / 60, 0)

  print("## Totals")
  for name, totals in sorted(totals.items(),
                             key=lambda i:
                             (RECIPES[i[0]].building.name
                              if i[0] in RECIPES else 'xx', i[0])):
    print("% 6.1f🏭 % 6.1f/sec %s (%s)" %
          (totals.buildings, totals.items_per_sec, name,
           RECIPES[name].building.name if name in RECIPES else 'raw'))


def main():
  assert (check_recipes())
  print("Recipes ok!")
  calculate_recursive('chemical-science-pack', 45)
  print()
  calculate_recursive('military-science-pack', 45)
  print()
  calculate_recursive('production-science-pack', 45)
  print()
  calculate_recursive('advanced-circuit', 4*60)


if __name__ == "__main__":
  main()
