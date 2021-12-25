#!/usr/bin/python3

# Variables used by federation2.py and fed_utils.py


# Character variables
balance = 0  # character's current balance, from output of score
current_stamina = 0  # character's current stamina, from output of score
stamina_max = 0  # character's maximum stamina level, from output of score
current_system = ""  # character is on this planet, from output of score
current_planet = ""  # character is in this system, from output of score
character_rank = ""  # character's rank, from output of score
stamina_min = 35  # lowest stamina level we want our character to fall to

# Ship variables
current_fuel = 0  # ship's current fuel level, from output of st
fuel_min = 250  # lowest fuel level we want our ship to fall to
fuel_max = 0  # ship's maximum stamina level, from output of st
current_cargo = 0  # total cargo currently being hauled
cargo_min = 0  # not sure if needed
cargo_max = 0  # maximum tonnage ship can haul

# Planet variables
treasury = 0  # planet's current balance, from output of di planet
exchange_dict = {}  # used to hold the exchange information
deficits = []  # used to hold the current deficits list
surpluses = []  # used to hold the current surpluses list
