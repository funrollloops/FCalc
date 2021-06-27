#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import timedelta
from math import ceil
from queue import Queue
from typing import NamedTuple, TextIO
from sys import stdout, argv

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
    assert (len(modules) <=
            building.slots), f"{building.name} only has {building.slots} slots!"
    self.building = building
    self.modules = modules
    self.name = name
    self.productivity = 1 + sum(m.productivity for m in modules)
    self.crafting_speed = building.crafting_speed * (1 + sum(m.crafting_speed
                                                             for m in modules))


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
ASSEMBLER2_2PROD1 = ModdedBuilding('assembler-2:2×prod1', ASSEMBLER2,
                           [PRODUCTIVITY1, PRODUCTIVITY1])
ASSEMBLER = ASSEMBLER2_2PROD1

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


@dataclass
class Demand:
  name: str
  items_per_second: float


@dataclass
class Totals:
  buildings: float = 0
  items_per_sec: float = 0


def belts(items_per_sec: float):
  if items_per_sec <= 7.5: return ''
  return ' %1.1f|' % (items_per_sec / 7.5)

def calculate_recursive(name: str, items_per_second: float,
                        totals: dict[str, Totals], deferred: set[str],
                        output: TextIO):

  def process(name: str, items_per_sec: float,
              depth: int) -> dict[name, Totals]:
    totals.setdefault(name, Totals())
    totals[name].items_per_sec += items_per_sec
    if name in RAWS or (name in deferred and depth != 0):
      output.write("%s% 5.2f/s%s %s\n" %
                   ('  ' * depth, items_per_sec, belts(items_per_sec), name))
      return
    recipe = RECIPES[name]
    # Calculate how many assemblers are needed.
    per_building_per_sec = (recipe.output_qty / recipe.time.total_seconds() *
                            recipe.building.crafting_speed *
                            recipe.building.productivity)
    buildings = items_per_sec / per_building_per_sec
    output.write(
        "%s% 5.2f/s%s % 5.1f🏭 %s (%s)\n" %
        ('  ' * depth, items_per_sec, belts(items_per_sec), buildings, name, recipe.building.name))
    totals[name].buildings += buildings
    # Calculate demand on the inputs.
    for input in recipe.ingredients:
      process(
          input.name, input.qty * items_per_sec / recipe.output_qty /
          recipe.building.productivity, depth + 1)

  process(name, items_per_second, 0)
  return totals


def print_totals(totals: dict[str, Totals], output: TextIO):
  for name, totals in sorted(totals.items(),
                             key=lambda i:
                             (RECIPES[i[0]].building.name
                              if i[0] in RECIPES else 'xx', i[0])):
    output.write("% 6.1f🏭 % 6.2f/sec % 1.1f| %s (%s)\n" %
                 (totals.buildings, totals.items_per_sec, totals.items_per_sec / 7.5, name,
                  RECIPES[name].building.name if name in RECIPES else 'raw'))


def calculate(demands: list[Demand], output: TextIO):
  totals: dict[str, Totals] = {}
  deferred = set(d.name for d in demands)
  processed: dict[str, float] = {}
  for demand in demands:
    output.write("\n")
    if not demand.items_per_second:
      demand.items_per_second = totals[demand.name].items_per_sec
    processed[demand.name] = demand.items_per_second
    totals[demand.name] = Totals()
    calculate_recursive(
        demand.name, demand.items_per_second, totals, deferred, output)
    for name, items_per_sec in processed.items():
      assert (
          totals[name].items_per_sec == items_per_sec
      ), f"Demand for {name} added after it was processed while processing {demand.name}!"

  output.write("\n## Totals\n")
  print_totals(totals, output)


def main(args):
  assert (len(args) <= 1), "Too many arguments: %s" % args
  assert (check_recipes()), "Recipe database is inconsistent"

  if not args:
    output = stdout
  else:
    output = open(args[0], 'w', encoding='utf-8')

  calculate(
      [
          Demand('production-science-pack', .75),
          Demand('chemical-science-pack', .75),
          Demand('military-science-pack', .75),

          # Auto
          Demand('advanced-circuit', None),
          Demand('stone', None),
          Demand('steel-plate', None),
          Demand('iron-plate', None),
          Demand('copper-plate', None)
      ],
      output)

  output.close()


if __name__ == "__main__":
  main(argv[1:])