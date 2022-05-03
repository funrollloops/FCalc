#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import timedelta
from typing import NamedTuple, TextIO
from sys import stdout, argv

secs = lambda s: timedelta(seconds=s)


@dataclass
class Building:
  name: str
  crafting_speed: float
  productivity: float = 1.
  slots: int = 0


class Module(NamedTuple):
  name: str
  crafting_speed: float = 0
  productivity: float = 0
  power: float = 0


class ModdedBuilding(Building):

  def __init__(self,
               name: str,
               building: Building,
               modules: list[Module],
               beacon_modules: list[Module] = []):
    assert (len(modules) <=
            building.slots), f"{building.name} only has {building.slots} slots!"
    self.building = building
    self.modules = modules
    self.beacon_modules = beacon_modules
    self.name = name
    self.productivity = 1
    self.productivity += sum(m.productivity for m in modules)
    self.productivity += sum(m.productivity / 2 for m in beacon_modules)
    crafting_multiplier = 1
    crafting_multiplier += sum(m.crafting_speed for m in modules)
    crafting_multiplier += sum(m.crafting_speed / 2 for m in beacon_modules)
    self.crafting_speed = building.crafting_speed * crafting_multiplier


PRODUCTIVITY1 = Module('prod-1', crafting_speed=-0.05, productivity=0.04)
PRODUCTIVITY2 = Module('prod-2', crafting_speed=-0.10, productivity=0.06)
PRODUCTIVITY3 = Module('prod-3', crafting_speed=-0.15, productivity=0.10)
SPEED1 = Module('speed-1', crafting_speed=0.2, power=0.5)
SPEED2 = Module('speed-2', crafting_speed=0.3, power=0.6)
EFFICIENCY1 = Module('efficiency-1', power=-0.3)
STONE_FURNACE = Building('stone-furnace', 1)
STEEL_FURNACE = Building('steel-furnace', 2)
ELECTRIC_FURNACE = Building('electric-furnace', 2, slots=2)
FURNACE = ModdedBuilding('electric-furnace:2p₁', ELECTRIC_FURNACE,
                         [PRODUCTIVITY1, PRODUCTIVITY1])

ASSEMBLER1 = Building('assembler-1', .5)
ASSEMBLER2 = Building('assembler-2', .75, slots=2)
ASSEMBLER3 = Building('assembler-3', 1.25, slots=4)
ASSEMBLER2_2PROD1 = ModdedBuilding('assembler-2:2p₁', ASSEMBLER2,
                                   [PRODUCTIVITY1, PRODUCTIVITY1])
ASSEMBLER3_4PROD2 = ModdedBuilding('assembler-3:4p₂', ASSEMBLER3,
                                   [PRODUCTIVITY2] * 4)
ASSEMBLER3_3PROD2_1SPEED1 = ModdedBuilding('assembler-3:3p₂s₁',
                                           ASSEMBLER3,
                                           [PRODUCTIVITY2] * 3 + [SPEED1])
ASSEMBLER3_4PROD2_16SPDBCON = ModdedBuilding('assembler-3:4p₂☸16s₂',
                                             ASSEMBLER3, [PRODUCTIVITY2] * 4,
                                             [SPEED2] * 16)
ASSEMBLER_NOPROD = ASSEMBLER2
ASSEMBLER = ASSEMBLER2_2PROD1

SILO = Building('rocket-silo', 1, slots=4)
SILO_4PROD3 = ModdedBuilding('rocket-silo:4p₃', SILO, [PRODUCTIVITY3]*4)

CHEMICAL_PLANT = Building('chemical-plant', 1, slots=3)
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


RAWS = set(['petroleum-gas', 'heavy-oil', 'solid-fuel', 'light-oil'])

RECIPE_LIST = [
    Recipe('space-science-pack', SILO, 1000, secs(4), [
        Ingredient('rocket-part', 100),
        Ingredient('satellite', 1)
    ]),
    Recipe('rocket-part', SILO_4PROD3, 1, secs(3), [
        Ingredient('rocket-control-unit', 10),
        Ingredient('rocket-fuel', 10),
        Ingredient('low-density-structure', 10),
    ]),
    Recipe('satellite', ASSEMBLER, 1, secs(5), [
      Ingredient('processing-unit', 100),
      Ingredient('low-density-structure', 100),
      Ingredient('rocket-fuel', 50),
      Ingredient('solar-panel', 100),
      Ingredient('accumulator', 100),
      Ingredient('radar', 5)
    ]),
    Recipe('solar-panel', ASSEMBLER, 1, secs(10), [
      Ingredient('copper-plate', 5),
      Ingredient('steel-plate', 5),
      Ingredient('electronic-circuit', 15)
    ]),
    Recipe('accumulator', ASSEMBLER, 1, secs(10), [
      Ingredient('iron-plate', 2),
      Ingredient('battery', 5)
    ]),
    Recipe('radar', ASSEMBLER, 1, secs(0.5), [
      Ingredient('iron-plate', 10),
      Ingredient('iron-gear-wheel', 5),
      Ingredient('electronic-circuit', 5)
    ]),
    Recipe('rocket-control-unit', ASSEMBLER, 1, secs(30), [
        Ingredient('processing-unit', 1),
        Ingredient('speed-module-1', 1)
    ]),
    Recipe('rocket-fuel', ASSEMBLER, 1, secs(30), [
        Ingredient('solid-fuel', 10),
        Ingredient('light-oil', 10)
    ]),
    Recipe('speed-module-1', ASSEMBLER, 1, secs(15), [
        Ingredient('electronic-circuit', 5),
        Ingredient('advanced-circuit', 5)
    ]),
    Recipe('utility-science-pack', ASSEMBLER, 3, secs(21), [
        Ingredient('processing-unit', 2),
        Ingredient('flying-robot-frame', 1),
        Ingredient('low-density-structure', 3)
    ]),
    Recipe('processing-unit', ASSEMBLER, 1, secs(10), [
        Ingredient('electronic-circuit', 20),
        Ingredient('advanced-circuit', 2),
        Ingredient('sulfuric-acid', 5)
    ]),
    Recipe('flying-robot-frame', ASSEMBLER, 1, secs(20), [
        Ingredient('steel-plate', 1),
        Ingredient('battery', 2),
        Ingredient('electronic-circuit', 3),
        Ingredient('electric-engine-unit', 1),
    ]),
    Recipe('low-density-structure', ASSEMBLER, 1, secs(20), [
        Ingredient('steel-plate', 2),
        Ingredient('copper-plate', 20),
        Ingredient('plastic-bar', 5),
    ]),
    Recipe('electric-engine-unit', ASSEMBLER, 1, secs(10), [
        Ingredient('electronic-circuit', 2),
        Ingredient('engine-unit', 1),
        Ingredient('lubricant', 15)
    ]),
    Recipe('sulfuric-acid', CHEMICAL_PLANT, 50, secs(1), [
        Ingredient('iron-plate', 1),
        Ingredient('sulfur', 5),
        Ingredient('water', 100),
    ]),
    Recipe('battery', CHEMICAL_PLANT, 1, secs(4), [
        Ingredient('iron-plate', 1),
        Ingredient('copper-plate', 1),
        Ingredient('sulfuric-acid', 20),
    ]),
    Recipe('lubricant', CHEMICAL_PLANT, 10, secs(1), [
        Ingredient('heavy-oil', 10),
    ]),
    Recipe('production-science-pack', ASSEMBLER, 3, secs(21), [
        Ingredient('rail', 30),
        Ingredient('electric-furnace', 1),
        Ingredient('productivity-module-1', 1),
    ]),
    Recipe('rail', ASSEMBLER_NOPROD, 2, secs(.5), [
        Ingredient('stone', 1),
        Ingredient('steel-plate', 1),
        Ingredient('iron-stick', 1)
    ]),
    Recipe('electric-furnace', ASSEMBLER_NOPROD, 1, secs(5), [
        Ingredient('steel-plate', 10),
        Ingredient('advanced-circuit', 5),
        Ingredient('stone-brick', 10)
    ]),
    Recipe('productivity-module-1', ASSEMBLER_NOPROD, 1, secs(15), [
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
    Recipe('electronic-circuit', ASSEMBLER3_4PROD2_16SPDBCON, 1, secs(.5),
           [Ingredient('iron-plate', 1),
            Ingredient('copper-cable', 3)]),
    Recipe('copper-cable', ASSEMBLER3_4PROD2_16SPDBCON, 2, secs(.5),
           [Ingredient('copper-plate', 1)]),
    Recipe('steel-plate', FURNACE, 1, secs(16), [Ingredient('iron-plate', 5)]),
    Recipe('iron-gear-wheel', ASSEMBLER, 1, secs(.5),
           [Ingredient('iron-plate', 2)]),
    Recipe('pipe', ASSEMBLER_NOPROD, 1, secs(.5),
           [Ingredient('iron-plate', 1)]),
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
    Recipe('piercing-rounds-magazine', ASSEMBLER_NOPROD, 1, secs(4), [
        Ingredient('copper-plate', 5),
        Ingredient('steel-plate', 1),
        Ingredient('firearm-magazine', 1),
    ]),
    Recipe('grenade', ASSEMBLER_NOPROD, 1, secs(8), [
        Ingredient('coal', 10),
        Ingredient('iron-plate', 5),
    ]),
    Recipe('wall', ASSEMBLER_NOPROD, 1, secs(0.5), [
        Ingredient('stone-brick', 5),
    ]),
    Recipe('firearm-magazine', ASSEMBLER_NOPROD, 1, secs(1), [
        Ingredient('iron-plate', 4),
    ]),
    Recipe('stone-brick', FURNACE, 1, secs(3.2), [
        Ingredient('stone', 2),
    ]),
]

RECIPES: dict[str, Recipe] = {r.name: r for r in RECIPE_LIST}


def check_recipes():
  result = True
  for r in RECIPES.values():
    for i in r.ingredients:
      if i.name in RECIPES or i.name in RAWS:
        continue
      print(f"Recipe {r.name} references non-existent ingredient {i.name}")
      result = False
  return result


class Demand(NamedTuple):
  name: str
  min_items_per_second: float


@dataclass
class Totals:
  buildings: float = 0
  items_per_sec: float = 0


def belts(items_per_sec: float):
  if items_per_sec <= 7.5:
    return ''
  return ' %5.1f┋' % (items_per_sec / 7.5)


def calculate_recursive(name: str, items_per_second: float,
                        totals: dict[str, Totals], deferred: set[str],
                        output: TextIO) -> dict[str, Totals]:

  def process(name: str, items_per_sec: float,
              depth: int):
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
    output.write("%s% 5.2f/s%s % 5.1f🏭 %s (%s)\n" %
                 ('  ' * depth, items_per_sec, belts(items_per_sec), buildings,
                  name, recipe.building.name))
    totals[name].buildings += buildings
    # Calculate demand on the inputs.
    for input in recipe.ingredients:
      process(
          input.name, input.qty * items_per_sec / recipe.output_qty /
          recipe.building.productivity, depth + 1)

  process(name, items_per_second, 0)
  return totals


def print_totals(totals: dict[str, Totals], output: TextIO):
  for name, total in sorted(totals.items(),
                             key=lambda i:
                             (RECIPES[i[0]].building.name
                              if i[0] in RECIPES else 'xx', i[0])):
    output.write(
        "% 6.1f🏭 % 7.2f/sec % 6.1f┋ %s (%s)\n" %
        (total.buildings, total.items_per_sec, total.items_per_sec / 7.5,
         name, RECIPES[name].building.name if name in RECIPES else 'raw'))


def calculate(demands: list[Demand], output: TextIO):
  totals: dict[str, Totals] = {}
  deferred = set(d.name for d in demands)
  processed: dict[str, float] = {}
  for demand in demands:
    output.write("\n")
    requested = totals.get(demand.name, Totals()).items_per_sec
    if requested < demand.min_items_per_second:
      requested = demand.min_items_per_second
    processed[demand.name] = requested
    totals[demand.name] = Totals()
    calculate_recursive(demand.name, requested, totals, deferred, output)
    deferred.remove(demand.name)
    for name, items_per_sec in processed.items():
      if totals[name].items_per_sec != items_per_sec:
        print(
            f"WARNING: Demand for {name} added after it was processed while processing {demand.name}!"
        )
        processed[name] = totals[name].items_per_sec

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
          Demand('utility-science-pack', .75),
          Demand('production-science-pack', .75),
          Demand('chemical-science-pack', .75),
          Demand('military-science-pack', .75),
          Demand('space-science-pack', .75),

          # Subfactories.
          Demand('processing-unit', 0),
          Demand('advanced-circuit', 0),
          Demand('electronic-circuit', 0),
          Demand('low-density-structure', 0),
          Demand('rocket-fuel', 0),
          Demand('sulfuric-acid', 0),
          Demand('stone', 0),
          Demand('steel-plate', 0),
          Demand('iron-plate', 0),
          Demand('copper-plate', 0),
      ],
      output)

  output.close()




if __name__ == "__main__":
  main(argv[1:])
