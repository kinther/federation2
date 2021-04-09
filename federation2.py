#!/usr/bin/python3

# Federation 2 Community Edition automation scripts for planet owners
# Written by Strahd of the Barovia system
# Please don't tell anyone how I script *Lenny face*

# Imports
import telnetlib # used to do all things telnet
import time # used to provide sleep function and logging file name
import re # used to escape ansi characters
import json # used to read planets.json file
import logging # used to write logs to file

# Login variables
host = "play.federation2.com" # don't change this
port = 30003 # don't change this
timeout = 15 # maybe change this
user = "" # change this
password = "" # change this

# Telnetlib variables
tn = telnetlib.Telnet(host, port, timeout=timeout)

# Logging constants
LOG_FILENAME = time.strftime("%c" + "-fed2.txt")

# Logging variables
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
logger = logging.getLogger()

# Character constants
HOME_PLANET = "ravenloft" # constant variable used to check exchange info
DEFICIT = -75 # How much we consider a deficit
SURPLUS = 15000 # How much we consider a surplus

# Character variables
balance = 0 # character's current balance, from output of score
current_stamina = 0 # character's current stamina, from output of score
stamina_min = 20 # lowest stamina level we want our character to fall to
stamina_max = 0 # character's maximum stamina level, from output of score
current_system = "" # character is on this planet, from output of score
current_planet = "" # character is in this system, from output of score

# Ship variables
current_fuel = 0 # ship's current fuel level, from output of st
fuel_min = 50 # lowest fuel level we want our ship to fall to
fuel_max = 0 # ship's maximum stamina level, from output of st
current_cargo = 0 # total cargo currently being hauled
cargo_min = 0 # not sure if needed
cargo_max = 0 # maximum tonnage ship can haul

# Planet variables
treasury = 0 # planet's current balance, from output of di planet
exchange_dict = {}
deficits = []
surpluses = []

# Global functions

def login():

    # Wait for Login prompt, then write username and hit enter
    tn.read_until(b"Login:")
    tn.write(user.encode("ascii") + b"\n")
    time.sleep(2)

    # Wait for Password prompt, then write password and hit enter
    tn.read_until(b"Password:")
    tn.write(password.encode("ascii") + b"\n")
    time.sleep(2)

    # Wait for string indicating we have logged in successfully
    tn.read_until(b"Linking to Federation DataSpace.")
    logger.info(f"Logged in successfully to {host} on port {port} as {user}.")
    time.sleep(5)

def quit():

    # Exits game gracefully
    tn.write(b"quit")
    time.sleep(5)
    tn.write(b"\n")
    logger.info("Issued quit command.")
    tn.close()
    logger.info(f"Closed connection to {host} on port {port} as {user}.")

def clearBuffer():
    # Attempts to clear the buffer
    tn.write(b"\n")
    i = tn.read_very_eager().decode("ascii")
    time.sleep(5)

def escape_ansi(line):
    # https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi
    # -escape-sequences-from-a-string-in-python
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

# Character functions

def updateScore():

    # Clear buffer before issuing commands
    clearBuffer()

    # Check character score information
    logger.info(f"Updating score info of {user}...")
    tn.write(b"score\n")
    time.sleep(5)
    score = tn.read_very_eager().decode("ascii")
    score = escape_ansi(score)

    # Write score output to file
    file = open("score.txt", "w")
    f = file.write(score)
    file.close()

def checkBalance():

    # Bring in global variables
    global balance

    # Check character balance information
    logger.info(f"Checking bank balance of {user}...")
    with open("score.txt", "r") as f:
        for line in f:
            if "Bank" in line:
                i = line.split(" ") # remove whitespace
                i = i[4] # select fourth entry in list
                i = i[:-3] # remove last 3 characters from string
                i = i.split(",") # parse output to remove comma separation
                i = "".join(i) # rejoin list entries into single string
                i = int(i) # turn string into integer
                balance = i

def checkStamina():

    # Bring in global variables
    global current_stamina
    global stamina_max

    # Check character stamina information
    logger.info(f"Checking stamina of {user}...")
    with open("score.txt", "r") as f:
        for line in f:
            if "Stamina" in line:
                i = line.split(" ")
                i = i[9]
                i = i.split("/")
                current_stamina = int(i[0])
                imax = i[1]
                stamina_max = int(imax[:-1])

def checkLocation():

    # Bring in global variables
    global current_planet
    global current_system

    # Check character location information
    logger.info(f"Checking location of {user}...")
    with open("score.txt", "r") as f:
        for line in f:
            if "system" in line:
                i = line.split(" ")
                current_planet = i[6]
                current_system = i[9]

def buyFood():

    # Clear buffer before issuing commands
    clearBuffer()

    # Tries to buy food for the player
    logger.info(f"Buying food for {user}...")
    tn.write(b"buy food\n")
    time.sleep(5)

# Ship functions

def updateShip():

    # Clear buffer before issuing commands
    clearBuffer()

    # Check ship status information
    logger.info(f"Updating ship info of {user}...")
    tn.write(b"st\n")
    time.sleep(5)
    ship = tn.read_very_eager().decode("ascii")
    ship = escape_ansi(ship)

    # Write st output to file
    file = open("ship.txt", "w")
    f = file.write(ship)
    file.close()

def checkFuel():

    # Bring in global variables
    global current_fuel
    global fuel_max

    # Check character location information
    logger.info(f"Checking treasury of {current_planet}...")
    with open("ship.txt", "r") as f:
        for line in f:
            if "Fuel" in line:
                i = line.split(" ")
                ii = i[13]
                ii = ii.split("/")
                current_fuel = int(ii[0])
                fuel_max = int(ii[1])

def checkCargo():

    # Bring in global variables
    global current_cargo
    global cargo_max

    # Check character location information
    logger.info(f"Checking cargo of {user} ship...")
    with open("ship.txt", "r") as f:
        for line in f:
            if "Cargo" in line:
                i = line.split(" ")
                i = i[7]
                i = i.split("/")
                current_cargo = int(i[0])
                cargo_max = int(i[1])

def buyFuel():

    # Clear buffer before issuing commands
    clearBuffer()

    # Tries to buy fuel for the player's ship
    logger.info(f"Buying fuel for {user}'s ship...")
    tn.write(b"buy fuel\n")
    time.sleep(5)

# Planet/Exchange functions

def updatePlanet():

    # Clear buffer before issuing commands
    clearBuffer()

    # Check planetary exchange information
    logger.info(f"Updating {current_planet} planet information...")
    tn.write(b"di planet\n")
    time.sleep(5)
    planet = tn.read_very_eager().decode("ascii")
    planet = escape_ansi(planet)

    # Write score output to file
    file = open("planet.txt", "w")
    f = file.write(planet)
    file.close()

def updateExchange():

    # Bring in global variables
    global HOME_PLANET

    # Clear buffer before issuing commands
    clearBuffer()

    # Check planetary exchange information
    logger.info(f"Updating {current_planet} exchange information...")
    tn.write(b"di exchange " + str.encode(HOME_PLANET) + b"\n")
    time.sleep(5)
    exchange = tn.read_very_eager().decode("ascii")
    exchange = escape_ansi(exchange)

    # Write score output to file
    file = open("exchange.txt", "w")
    f = file.write(exchange)
    file.close()

def checkTreasury():

    # Bring in global variables
    global treasury

    # Check character location information
    logger.info(f"Checking treasury of {current_planet}...")
    with open("planet.txt", "r") as f:
        for line in f:
            if "Treasury" in line:
                i = line.split(" ")
                i = i[3]
                i = i[:-3]
                i = i.split(",")
                i = "".join(i)
                i = int(i)
                treasury = i

def parseExchange():

    # Bring in global variables
    global exchange_dict

    # parse plaintext exchange data and extract current data
    logger.info("Pulling exchange data into dictionary...")
    with open("exchange.txt", "r") as f:
        next(f)
        for line in f:
            i = line.split(" ")
            commodity = i[2]
            commodity = commodity[:-1] # strip colon after commodity name
            current = i[12]
            current = current.split("/")
            current = current[0]
            max = i[14]
            exchange_dict[commodity] = {"Current": current, "Max": max}

def checkDeficits():

    # Bring in global variables
    global DEFICIT

    # Checks what home planet has current deficits of and writes to list
    logger.info("Checking home planet deficits...")
    for commodity in exchange_dict:
        if int(exchange_dict[commodity]["Current"]) < DEFICIT:
            deficits.append(commodity)

def checkSurpluses():

    # Bring in global variables
    global SURPLUS

    # Checks what home planet has current surpluses of and writes to list
    logger.info("Checking home planet surpluses...")
    for commodity in exchange_dict:
        if int(exchange_dict[commodity]["Current"]) > SURPLUS:
            surpluses.append(commodity)

# Move functions

def boardPlanet():

    # Lands or lifts off from planet
    logger.info("Boarding planet...")
    tn.write(b"board\n")
    time.sleep(5)

def moveDirection(direction):

    # Moves in a direction the function takes as an argument
    logger.info(f"Moving {direction}...")
    tn.write(str.encode(direction) + b"\n")
    time.sleep(5)

def jumpSystem(system):

    # Moves to a new system or cartel from the inter-stellar link
    logger.info(f"Jumping to {system}...")
    tn.write(b"jump " + str.encode(system) + b"\n")
    time.sleep(5)

# Trade functions

def buyCommodity(commodity):

    # Used to buy commodities at an exchange
    logger.info(f"Buying {commodity}...")
    tn.write(b"buy " + str.encode(commodity) + "\n")
    time.sleep(5)

def sellCommodity(commodity):

    # Used to sell commodities at an exchange
    logger.info(f"Selling {commodity}...")
    tn.write(b"sell " + str.encode(commodity) + b"\n")
    time.sleep(5)

def deficitToBays(commodity):

    # Bring in global variables
    global exchange_dict

    # Temporary variables
    bays = 0

    # Used to determine how many bays of a deficit to buy
    logger.info(f"Identifying how many bays to buy of {commodity}...")
    # Check current deficit value by parsing dictionary based on commodity key
    for item in exchange_dict:
        if commodity in item:
            bays = int(exchange_dict[commodity]["Current"])
            bays = int((bays / 75) * -1)

    return bays

# Multi functions

def player():

    # Runs all player functions with slight delay
    updateScore() # Required before any other check can run
    time.sleep(5)
    checkBalance() # How much money do we have right now?
    time.sleep(5)
    checkStamina() # How much stamina do we have right now?
    time.sleep(5)
    checkLocation() # What planet and system are we on right now?
    time.sleep(5)

def ship():

    # Runs all ship functions with slight delay
    updateShip() #  Required before any other check can run
    time.sleep(5)
    checkFuel() # How much fuel do we have right now?
    time.sleep(5)
    checkCargo() # How much cargo do we have right now?
    time.sleep(5)

def planet():

    # Runs all planet functions with slight delay
    updatePlanet() # Required before any other update can run
    time.sleep(5)
    checkTreasury() # How much money does the treasury have right now?
    time.sleep(5)

def exchange():

    # Runs all planet exchange functions with slight delay
    updateExchange() # Required before any other update can run
    time.sleep(5)
    parseExchange() # Convert plain text to dictionary
    time.sleep(5)
    checkDeficits()
    time.sleep(5)
    checkSurpluses()
    time.sleep(5)

def gatherData():

    # Runs all multi functions
    player()
    time.sleep(5)
    ship()
    time.sleep(5)
    planet()
    time.sleep(5)
    exchange()
    time.sleep(5)

# Main function

def main():

    print("Starting up... please check logging file for more info...")
    # Perform initial setup and gather game data
    try:
        login()
        time.sleep(5)
        gatherData()
        time.sleep(5)
    except:
        logger.error("Ran into error during initial setup and gathering data.")

### Print functions for debugging during initial coding

    # Check updated character variables
    print("+---------------------------------------------+")
    print(f"Current balance of {user} is {balance}")
    print(f"Current stamina is at {current_stamina}/{stamina_max}")
    print(f"{user} is currently on planet {current_planet}")
    print(f"{user} is currently in the {current_system} system")
    print("+---------------------------------------------+")

    # Check updated ship variables
    print("+---------------------------------------------+")
    print(f"Current ship fuel is {current_fuel}/{fuel_max}")
    print(f"Current cargo usage is {current_cargo}/{cargo_max}")
    print("+---------------------------------------------+")

    # Check updated planetary variables
    print("+---------------------------------------------+")
    print(f"{current_planet} has a treasury value of {treasury}")
    print("+---------------------------------------------+")

    # Check updated exchange variables
    print("+---------------------------------------------+")
    print(f"{current_planet} has the following deficits:")
    print(f"{deficits}")
    print(f"{current_planet} has the following surpluses:")
    print(f"{surpluses}")
    print("+---------------------------------------------+")

### End print functions

    # Exits game
    quit()

if __name__ == "__main__":
    main()
