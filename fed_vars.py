#!/usr/bin/python3

# Variables used by federation2.py and fed_utils.py


# Character variables
score = ""  # output of the score command held in memory
balance = 0  # character's current balance, from output of score
current_stamina = 0  # character's current stamina, from output of score
stamina_max = 0  # character's maximum stamina level, from output of score
current_system = ""  # character is on this planet, from output of score
current_planet = ""  # character is in this system, from output of score
character_rank = ""  # character's rank, from output of score
stamina_min = 35  # lowest stamina level we want our character to fall to

# Character class structure

class Player:
    def __init__(self, score, balance, current_stamina, stamina_max,
    current_system, current_planet, character_rank, stamina_min):
        self.score = ""
        self.balance = 0
        self.current_stamina = 0
        self.stamina_max = 0
        self.current_system = ""
        self.current_planet = ""
        self.character_rank = ""
        self.stamina_min = 35

# Ship variables
ship = ""  # output of the status report command held in memory
current_fuel = 0  # ship's current fuel level, from output of st
fuel_min = 250  # lowest fuel level we want our ship to fall to
fuel_max = 0  # ship's maximum stamina level, from output of st
current_cargo = 0  # total cargo currently being hauled
cargo_min = 0  # not sure if needed
cargo_max = 0  # maximum tonnage ship can haul

# Ship class structure

class Ship:
    def __init__(self, ship, current_fuel, fuel_min, fuel_max,
    current_cargo, cargo_min, cargo_max):
        self.ship = ""
        self.current_fuel = 0
        self.fuel_min = 250
        self.fuel_max = 0
        self.current_cargo = 0
        self.cargo_min = 0
        self.cargo_max = 0

# Planet variables
planet = ""  # output of the di planet command held in memory
exchange = ""  # output of the di exchange command held in memory
treasury = 0  # planet's current balance, from output of di planet
exchange_dict = {}  # used to hold the exchange information
deficits = []  # used to hold the current deficits list
surpluses = []  # used to hold the current surpluses list

# Planet class structure

class Planet:
    def __init__(self, planet, exchange, treasury, exchange_dict,
    deficits, surpluses):
        self.planet = ""
        self.exchange = ""
        self.treasury = 0
        self.exchange_dict = {}
        self.deficits = []
        self.surpluses = []