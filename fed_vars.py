#!/usr/bin/python3

# Variables used by federation2.py and fed_utils.py


# Character variables
score = ""  # output of the score command held in memory
balance = 0  # character's current balance, from output of score
current_stamina = 0  # character's current stamina, from output of score
stamina_max = 0  # character's maximum stamina level, from output of score
system_location = ""  # character is in this system, from output of score
current_planet = ""  # character is on this planet, from output of score
character_rank = ""  # character's rank, from output of score
stamina_min = 35  # lowest stamina level we want our character to fall to

# Ship variables
ship = ""  # output of the status report command held in memory
current_fuel = 0  # ship's current fuel level, from output of st
fuel_min = 250  # lowest fuel level we want our ship to fall to
fuel_max = 0  # ship's maximum stamina level, from output of st
current_cargo = 0  # total cargo currently being hauled
cargo_max = 0  # maximum tonnage ship can haul

# Planet variables
planet = ""  # output of the di planet command held in memory

exchange = ""  # output of the di exchange command held in memory
treasury = 0  # planet's current balance, from output of di planet
exchange_dict = {}  # used to hold the exchange information
deficits = []  # used to hold the current deficits list
surpluses = []  # used to hold the current surpluses list

# System variables

system = ""  # output of the di system command held in memory
owned_planets = []  # list of planets owned by the player

# Cartel variables

cartel = ""  # output of the di cartel command held in memory