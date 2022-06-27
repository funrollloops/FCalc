#!/usr/bin/env python3

from collections import defaultdict
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
ELECTRIC_FURNACE1 = Building('electric-furnace-1', 2, slots=2)
ELECTRIC_FURNACE2 = Building('electric-furnace-2', 3, slots=2)
ELECTRIC_FURNACE = ELECTRIC_FURNACE2
STONE_METAL_MIXING_FURNACE = Building('stone-metal-mixing-furnace', 1)
STEEL_METAL_MIXING_FURNACE = Building('steel-metal-mixing-furnace', 2)
STONE_CHEMICAL_FURNACE = Building('stone-chemical-furnace', 1)
STEEL_CHEMICAL_FURNACE = Building('steel-chemical-furnace', 2)
ELECTROLYSER1 = Building('electrolyser-1', 0.75)
ELECTROLYSER2 = Building('electrolyser-2', 1.25)
ELECTROLYSER3 = Building('electrolyser-3', 2.00)
ELECTROLYSER4 = Building('electrolyser-4', 2.75)
ELECTROLYSER = ELECTROLYSER3


ASSEMBLER1 = Building('assembler-1', 0.50, slots=0)
ASSEMBLER2 = Building('assembler-2', 0.75, slots=2)
ASSEMBLER3 = Building('assembler-3', 1.25, slots=4)
ASSEMBLER4 = Building('assembler-4', 2.00, slots=4)
ASSEMBLER5 = Building('assembler-5', 2.75, slots=4)
ELECTRONICS_ASSEMBLER1 = Building('electronics-assembler-1', 1)
ELECTRONICS_ASSEMBLER2 = Building('electronics-assembler-2', 2.25)
ELECTRONICS_ASSEMBLER3 = Building('electronics-assembler-3', 4)
ASSEMBLER3_4PROD2_16SPDBCON = ModdedBuilding('assembler-3:4p₂☸16s₂',
                                             ASSEMBLER3, [PRODUCTIVITY2] * 4,
                                             [SPEED2] * 16)
ASSEMBLER_NOPROD = ASSEMBLER4
ASSEMBLER = ASSEMBLER_NOPROD

CHEMICAL_PLANT = Building('chemical-plant', 1, slots=3)
ELECTRIC_MINING_DRILL = Building('electric-mining-drill', .5, slots=3)
WATER_PUMP = Building('water-pump', 1)
GREENHOUSE = Building('greenhouse', 0.75)
COMPRESSOR1 = Building('compressor', 1)

FURNACE = ELECTRIC_FURNACE
ASSEMBLER = ASSEMBLER2
METAL_MIXING_FURNACE = STEEL_METAL_MIXING_FURNACE
ELECTRONICS_ASSEMBLER = ELECTRONICS_ASSEMBLER3
CHEMICAL_FURNACE = STEEL_CHEMICAL_FURNACE
COMPRESSOR = COMPRESSOR1

class Ingredient(NamedTuple):
  name: str
  qty: int = 1


class Recipe(NamedTuple):
  name: str
  building: Building
  output_qty: int
  time: timedelta
  ingredients: list[Ingredient]


RAWS = set([
  'petroleum-gas', 'heavy-oil', 'solid-fuel', 'light-oil',
  'seedling', 'water',
  'tin-plate', 'lead-plate', 'copper-plate', 'steel-plate', 'iron-plate', 'brass-plate',
  'plastic-bar', 'glass',
  'silicon-ore', 'stone', 'coal', 'gold-ore', 'iron-ore', 'aluminium-ore', 'copper-ore',
  'chlorine', 'hydrogen', 'hydrogen-sulfide', 'sulfuric-acid'
])

RECIPE_LIST = [
  Recipe('logistic-science-pack', ASSEMBLER, 3, secs(21), [
    Ingredient('brass-chest', 2),
    Ingredient('express-transport-belt', 1),
    Ingredient('express-filter-inserter', 1),
    Ingredient('flying-robot-frame', 1),
  ]),
  Recipe('brass-chest', ASSEMBLER, 1, secs(.5), [
    Ingredient('brass-plate', 8)
  ]),
  Recipe('express-transport-belt', ASSEMBLER_NOPROD, 1, secs(0.5), [
    Ingredient('fast-transport-belt', 1),
    Ingredient('aluminium-plate', 2),
    Ingredient('cobalt-steel-gear-wheel', 4),
    Ingredient('cobalt-steel-bearing', 4)
  ]),
  Recipe('express-filter-inserter', ASSEMBLER_NOPROD, 1, secs(0.5), [
    Ingredient('fast-filter-inserter', 1),
    Ingredient('aluminium-plate', 1),
    Ingredient('electronic-circuit-board', 5),
    Ingredient('cobalt-steel-gear-wheel', 1),
    Ingredient('cobalt-steel-bearing', 1)
  ]),
  Recipe('flying-robot-frame', ASSEMBLER, 1, secs(20), [
    Ingredient('steel-plate', 1),
    Ingredient('battery', 2),
    Ingredient('electric-engine-unit', 1),
    Ingredient('basic-electronic-board', 3)
  ]),
  Recipe('fast-transport-belt', ASSEMBLER_NOPROD, 1, secs(0.5), [
    Ingredient('transport-belt', 1),
    Ingredient('bronze-plate', 2),
    Ingredient('steel-gear-wheel', 4),
  ]),
  Recipe('aluminium-plate', ELECTROLYSER, 2, secs(6.4), [
    Ingredient('carbon', 1),
    Ingredient('alumina', 2),
  ]),
  Recipe('cobalt-steel-gear-wheel', ASSEMBLER, 1, secs(0.5), [
    Ingredient('cobalt-steel-plate', 1),
  ]),
  Recipe('cobalt-steel-bearing', ASSEMBLER, 2, secs(0.5), [
    Ingredient('cobalt-steel-plate', 1),
    Ingredient('cobalt-steel-bearing-ball', 16),
  ]),
  Recipe('cobalt-steel-bearing-ball', ASSEMBLER, 12, secs(0.5), [
    Ingredient('cobalt-steel-plate', 1),
  ]),
  Recipe('cobalt-steel-plate', METAL_MIXING_FURNACE, 10, secs(32), [
    Ingredient('iron-plate', 14),
    Ingredient('cobalt-plate', 1),
  ]),
  Recipe('cobalt-plate', CHEMICAL_FURNACE, 1, secs(3.2), [
    Ingredient('cobalt-oxide', 1),
    Ingredient('sulfuric-acid', 10)
  ]),
  Recipe('fast-filter-inserter', ASSEMBLER_NOPROD, 1, secs(0.5), [
    Ingredient('filter-inserter', 1),
    Ingredient('bronze-plate', 1),
    Ingredient('basic-electronic-board', 1),
    Ingredient('steel-gear-wheel', 1),
  ]),
  Recipe('filter-inserter', ASSEMBLER_NOPROD, 1, secs(0.5), [
    Ingredient('inserter', 1),
    Ingredient('basic-electronic-board', 4)
  ]),
  Recipe('inserter', ASSEMBLER_NOPROD, 1, secs(0.5), [
    Ingredient('iron-plate', 1),
    Ingredient('iron-gear-wheel', 1),
    Ingredient('basic-circuit-board', 1),
  ]),
  Recipe('battery', CHEMICAL_PLANT, 1, secs(4), [
    Ingredient('plastic-bar', 1),
    Ingredient('lead-plate', 2),
    Ingredient('sulfuric-acid', 20)
  ]),
  Recipe('electric-engine-unit', ASSEMBLER, 1, secs(10), [
    Ingredient('engine-unit', 1),
    Ingredient('basic-electronic-board', 2),
    Ingredient('lubricant', 15)
  ]),
  Recipe('transport-belt', ASSEMBLER_NOPROD, 1, secs(0.5), [
    Ingredient('iron-gear-wheel', 2),
    Ingredient('basic-transport-belt', 1),
    Ingredient('tin-plate', 2),
  ]),
  Recipe('basic-transport-belt', ASSEMBLER_NOPROD, 2, secs(0.5), [
    Ingredient('iron-plate', 1),
    Ingredient('iron-gear-wheel', 1)
  ]),
  Recipe('bronze-plate', METAL_MIXING_FURNACE, 5, secs(16), [
    Ingredient('copper-plate', 3),
    Ingredient('tin-plate', 2),
  ]),
  Recipe('steel-gear-wheel', ASSEMBLER, 1, secs(0.5), [
    Ingredient('steel-plate', 1),
  ]),
  Recipe('basic-electronic-board', ELECTRONICS_ASSEMBLER, 1, secs(1), [
    Ingredient('solder', 1),
    Ingredient('basic-electronic-components', 5),
    Ingredient('basic-circuit-board', 1)
  ]),
  Recipe('basic-circuit-board', ELECTRONICS_ASSEMBLER, 1, secs(1), [
    Ingredient('copper-cable', 3),
    Ingredient('wooden-board', 1),
  ]),
  Recipe('wooden-board', ELECTRONICS_ASSEMBLER, 2, secs(0.5), [
    Ingredient('wood', 1)
  ]),
  Recipe('lubricant', CHEMICAL_PLANT, 10, secs(1), [
    Ingredient('heavy-oil', 10)
  ]),
  Recipe('alumina', CHEMICAL_FURNACE, 1, secs(2), [
    Ingredient('aluminium-ore', 1),
    Ingredient('sodium-hydroxide', 1)
  ]),
  Recipe('electronic-logic-board', ELECTRONICS_ASSEMBLER, 1, secs(10), [
    Ingredient('solder', 2),
    Ingredient('basic-electronic-components', 2),
    Ingredient('transistors', 4),
    Ingredient('integrated-circuits', 2),
    Ingredient('superior-circuit-board', 1)
  ]),
  Recipe('integrated-circuits', ELECTRONICS_ASSEMBLER, 5, secs(5), [
    Ingredient('plastic-bar'),
    Ingredient('silicon-wafer', 4),
    Ingredient('tinned-copper-wire', 1),
    Ingredient('sulfuric-acid', 5)
  ]),
  Recipe('superior-circuit-board', ELECTRONICS_ASSEMBLER, 1, secs(10), [
    Ingredient('copper-plate'),
    Ingredient('gold-plate'),
    Ingredient('fibreglass-board'),
    Ingredient('ferric-chloride-solution', 5)
  ]),
  Recipe('gold-plate', CHEMICAL_FURNACE, 1, secs(3.2), [
    Ingredient('gold-ore'),
    Ingredient('chlorine', 3)
  ]),
  Recipe('fibreglass-board', ELECTRONICS_ASSEMBLER, 2, secs(0.5), [
    Ingredient('plastic-bar'),
    Ingredient('glass')
  ]),
  Recipe('ferric-chloride-solution', CHEMICAL_PLANT, 50, secs(2.5), [
    Ingredient('iron-ore'),
    Ingredient('hydrogen-chloride', 30)
  ]),
  Recipe('cobalt-oxide', CHEMICAL_FURNACE, 2, secs(25), [
    Ingredient('copper-ore', 7),
    Ingredient('carbon', 1),
    Ingredient('limestone', 1),
    Ingredient('hydrogen', 5),
  ]),
  Recipe('chemical-science-pack', ASSEMBLER, 2, secs(14), [
    Ingredient('sulfur'),
    Ingredient('engine-unit', 2),
    Ingredient('sodium-hydroxide', 2),
    Ingredient('electronic-circuit-board', 3)
  ]),
  Recipe('sulfur', CHEMICAL_PLANT, 5, secs(1), [
    Ingredient('hydrogen-sulfide', 50),
    Ingredient('oxygen', 25)
  ]),
  Recipe('engine-unit', ASSEMBLER, 1, secs(10), [
    Ingredient('steel-plate'),
    Ingredient('iron-gear-wheel'),
    Ingredient('iron-pipe', 2)
  ]),
  Recipe('iron-gear-wheel', ASSEMBLER, 1, secs(0.5), [
    Ingredient('iron-plate', 2)
  ]),
  Recipe('iron-pipe', ASSEMBLER_NOPROD, 1, secs(0.5), [
    Ingredient('iron-plate', 1)
  ]),
  Recipe('sodium-hydroxide', ELECTROLYSER, 1, secs(2), [
    Ingredient('salt'),
    Ingredient('pure-water', 10)
  ]),
  Recipe('salt', CHEMICAL_FURNACE, 1, secs(0.5), [
    Ingredient('water', 25)
  ]),
  Recipe('electronic-circuit-board', ELECTRONICS_ASSEMBLER, 1, secs(5), [
    Ingredient('solder'),
    Ingredient('basic-electronic-components', 4),
    Ingredient('transistors', 4),
    Ingredient('circuit-board')
  ]),
  Recipe('solder', ELECTRONICS_ASSEMBLER, 8, secs(2), [
    Ingredient('resin'),
    Ingredient('solder-plate', 4)
  ]),
  Recipe('solder-plate', METAL_MIXING_FURNACE, 11, secs(7), [
    Ingredient('tin-plate', 4),
    Ingredient('lead-plate', 7)
  ]),
  Recipe('basic-electronic-components', ELECTRONICS_ASSEMBLER, 5, secs(2), [
    Ingredient('carbon'),
    Ingredient('tinned-copper-wire')
  ]),
  Recipe('carbon', CHEMICAL_FURNACE, 2, secs(2), [
    Ingredient('coal'),
    Ingredient('water', 5)
  ]),
  Recipe('tinned-copper-wire', ELECTRONICS_ASSEMBLER, 3, secs(0.5), [
    Ingredient('copper-cable', 3),
    Ingredient('tin-plate')
  ]),
  Recipe('transistors', ELECTRONICS_ASSEMBLER, 5, secs(3.5), [
    Ingredient('plastic-bar'),
    Ingredient('silicon-wafer', 2),
    Ingredient('tinned-copper-wire', 1)
  ]),
  Recipe('silicon-wafer', ASSEMBLER, 8, secs(5), [
    Ingredient('silicon-plate')
  ]),
  Recipe('silicon-plate', ELECTROLYSER, 2, secs(6.4), [
    Ingredient('silicon-ore', 2),
    Ingredient('carbon'),
    Ingredient('calcium-chloride', 2)
  ]),
  Recipe('calcium-chloride', CHEMICAL_PLANT, 1, secs(1), [
    Ingredient('limestone'),
    Ingredient('hydrogen-chloride', 50)
  ]),
  Recipe('hydrogen-chloride', CHEMICAL_PLANT, 25, secs(1), [
    Ingredient('chlorine', 12.5),
    Ingredient('hydrogen', 10)
  ]),
  Recipe('circuit-board', ELECTRONICS_ASSEMBLER, 1, secs(5), [
    Ingredient('phenolic-board'),
    Ingredient('copper-plate'),
    Ingredient('tin-plate')
  ]),
  Recipe('copper-cable', ELECTRONICS_ASSEMBLER, 2, secs(0.5), [
    Ingredient('copper-plate')
  ]),
  Recipe('phenolic-board', ELECTRONICS_ASSEMBLER, 2, secs(0.5), [
    Ingredient('wood'),
    Ingredient('resin')
  ]),
  Recipe('resin', ASSEMBLER, 1, secs(1), [
    Ingredient('wood')
  ]),
  Recipe('resin (heavy oil)', CHEMICAL_PLANT, 1, secs(1), [
    Ingredient('heavy-oil', 10)
  ]),
  Recipe('wood', GREENHOUSE, 15, secs(60), [
    Ingredient('seedling', 10),
    Ingredient('water', 20)
  ]),
  Recipe('wood (fertiliser, disabled)', GREENHOUSE, 30, secs(45), [
    Ingredient('seedling', 10),
    Ingredient('water', 20),
    Ingredient('fertiliser', 5)
  ]),
  Recipe('fertiliser', CHEMICAL_PLANT, 1, secs(3), [
    Ingredient('nitric-acid', 10),
    Ingredient('ammonia', 10)
  ]),
  Recipe('nitric-acid', CHEMICAL_PLANT, 20, secs(1), [
    Ingredient('nitrogen-dioxide', 20),
    Ingredient('hydrogen-peroxide', 20)
  ]),
  Recipe('ammonia', CHEMICAL_PLANT, 20, secs(1), [
    Ingredient('nitrogen', 10),
    Ingredient('hydrogen', 20)
  ]),
  Recipe('nitrogen-dioxide', CHEMICAL_PLANT, 20, secs(1), [
    Ingredient('nitric-oxide', 20),
    Ingredient('oxygen', 10)
  ]),
  Recipe('nitric-oxide', CHEMICAL_PLANT, 20, secs(1), [
    Ingredient('ammonia', 20),
    Ingredient('oxygen', 25)
  ]),
  Recipe('oxygen', CHEMICAL_PLANT, 12.5, secs(1), [
    Ingredient('pure-water', 10)
  ]),
  Recipe('pure-water', CHEMICAL_PLANT, 100, secs(2), [
    Ingredient('water', 100)
  ]),
  Recipe('hydrogen', CHEMICAL_PLANT, 20, secs(1), [
    Ingredient('pure-water', 10)
  ]),
  Recipe('nitrogen', CHEMICAL_PLANT, 20, secs(1), [
    Ingredient('compressed-air', 25)
  ]),
  Recipe('hydrogen-peroxide', CHEMICAL_PLANT, 8, secs(1), [
    Ingredient('hydrogen', 16),
    Ingredient('oxygen', 20)
  ]),
  Recipe('compressed-air', COMPRESSOR, 100, secs(1), [
  ]),
  Recipe('limestone', CHEMICAL_PLANT, 1, secs(2), [
    Ingredient('stone')
  ]),
  Recipe('water', WATER_PUMP, 1200, secs(1), [])
]

seen = defaultdict(lambda: 0)
for r in RECIPE_LIST:
  seen[r.name] += 1
for r in (n for r, c in seen.items() if c > 1):
  print(f'WARNING: duplicate recipe for {r}')

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
  min_items_per_second: float = 0


@dataclass
class Totals:
  buildings: float = 0
  items_per_sec: float = 0


def belts(items_per_sec: float):
  LANE_CAPACITY = 15 / 4
  if items_per_sec <= LANE_CAPACITY:
    return ''
  return ' %5.1f┋' % (items_per_sec / LANE_CAPACITY)


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

  """
  calculate([
          Demand('chemical-science-pack', 1),
          Demand('electronic-circuit-board', 2),
          Demand('electronic-logic-board', 2)
      ],
      output)
  """

  calculate([
    Demand('logistic-science-pack', 1),
    Demand('electronic-logic-board', 2),
    Demand('electronic-circuit-board', 2),
    Demand('basic-electronic-board'),
    Demand('cobalt-steel-plate'),
    Demand('bronze-plate'),
    Demand('solder'),
  ], output)

  output.close()




if __name__ == "__main__":
  main(argv[1:])
