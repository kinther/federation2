#!/usr/bin/python3

# Functions used by federation2.py

# Imports
from telnetlib import Telnet  # used to do all things telnet
from time import sleep  # used to provide sleep function
from datetime import datetime  # used to provide logging filename
from re import compile  # used to escape ansi characters
from json import load  # used to read planets.json file
from logging import basicConfig, getLogger  # used to write logs to file
from os import remove  # used to delete files
from argparse import ArgumentParser  # used to pass user/password credentials
from sys import exit  # used to exit script if criteria is met

# argparse constants
parser = ArgumentParser()
parser.add_argument("--user", type=str, action="store", required=True)
parser.add_argument("--password", type=str, action="store", required=True)
parser.add_argument("--planet", type=str, action="store", required=True)
parser.add_argument("--mode", type=str, action="store", required=True)
args = parser.parse_args()

# global constants
ranks = ["Founder", "Engineer", "Mogul", "Technocrat", "Gengineer", "Magnate", "Plutocrat"]
script_mode = (args.mode).lower()  # determines whether to focus on deficits or surpluses

# Telnetlib variables
host = "play.federation2.com"  # don't change this
port = 30003  # don't change this
timeout = 90  # maybe change this

# telnetlib constants
tn = Telnet(host, port, timeout=timeout)

# Logging constants
now = datetime.now()
day = now.strftime("%a")
hour = now.strftime("%H")
minute = now.strftime("%M")
LOG_FILENAME = (day + "-" + hour + minute + "-fed2.txt")
basicConfig(filename=LOG_FILENAME, level=20)
logger = getLogger()

# Character constants
HOME_PLANET = args.planet  # passed from player arguments
DEFICIT = -75  # How much we consider a deficit
SURPLUS = 18000  # How much we consider a surplus

# Character variables
balance = 0  # character's current balance, from output of score
current_stamina = 0  # character's current stamina, from output of score
stamina_min = 35  # lowest stamina level we want our character to fall to
stamina_max = 0  # character's maximum stamina level, from output of score
current_system = ""  # character is on this planet, from output of score
current_planet = ""  # character is in this system, from output of score
character_rank = ""  # character's rank, from output of score

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

# Global functions

def login():

    print("In the login fuction")
    # Wait for Login prompt, then write username and hit enter
    tn.read_until(b"Login:")
    tn.write((args.user).encode("ascii") + b"\n")
    sleep(2)

    # Wait for Password prompt, then write password and hit enter
    tn.read_until(b"Password:")
    tn.write((args.password).encode("ascii") + b"\n")
    sleep(2)

    # Wait for string indicating we have logged in successfully
    tn.read_until(b"Linking to Federation DataSpace.")
    logger.info(f"Logged in successfully to {host} on port {port} as {args.user}.")
    sleep(2)

def clearBuffer():

    print("In the clearBuffer function")
    # Attempts to clear the buffer
    i = ""
    try:
        tn.write(b"\n")
        i = tn.read_very_eager().decode("ascii")
        sleep(1)
    except Exception as e:
        print("Issue with clearing buffer.")
        logger.exception(e)
        pass
    i = ""  # get rid of whatever was in the buffer, we don't need it

def escape_ansi(line):
    # https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi
    # -escape-sequences-from-a-string-in-python
    ansi_escape = compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

def deleteFiles():

    while True:
        # deletes all generated files
        logger.info("Trying to delete previous files...")
        try:
            remove("score.txt")
        except FileNotFoundError as e:
            pass
        try:
            remove("ship.txt")
        except FileNotFoundError as e:
            pass
        try:
            remove("planet.txt")
        except FileNotFoundError as e:
            pass
        try:
            remove("exchange.txt")
        except FileNotFoundError as e:
            pass
        try:
            remove("price.txt")
        except FileNotFoundError as e:
            pass

        break

def nonblank_lines(f):
    # https://stackoverflow.com/questions/4842057/easiest-way-to-ignore-blank-
    # lines-when-reading-a-file-in-python
    for l in f:
        line = l.rstrip()
        if line:
            yield line

# Character functions

def updateScore():

    # Clear buffer before issuing commands
    clearBuffer()

    # Check character score information
    logger.info(f"Updating score info of {args.user}...")
    tn.write(b"score\n")
    sleep(1)
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
    logger.info(f"Checking bank balance of {args.user}...")
    try:
        with open("score.txt", "r") as f:
            for line in f:
                if "Bank Balance:" in line:
                    i = line.split(" ")  # remove whitespace
                    i = i[4]  # select fourth entry in list
                    i = i[:-3]  # remove last 3 characters from string
                    i = i.split(",")  # parse output to remove comma separation
                    i = "".join(i)  # rejoin list entries into single string
                    i = int(i)  # turn string into integer
                    balance = i
                else:
                    pass

    except Exception as e:
        logger.exception(e)

def checkStamina():

    # Bring in global variables
    global current_stamina
    global stamina_max

    # Check character stamina information
    logger.info(f"Checking stamina of {args.user}...")
    try:
        with open("score.txt", "r") as f:
            for line in f:
                if "Stamina" in line:
                    i = line.split(" ")
                    i = i[9]
                    i = i.split("/")
                    current_stamina = int(i[0])
                    imax = i[1]
                    stamina_max = int(imax[:-1])
                else:
                    pass

    except Exception as e:
        logger.exception(e)

def checkLocation():

    # Bring in global variables
    global current_planet
    global current_system

    # Check character location information
    logger.info(f"Checking location of {args.user}...")
    try:
        with open("score.txt", "r") as f:
            for line in f:
                if "You are currently on" in line:
                    i = line.split(" ")
                    current_planet = i[6]
                    current_system = i[9]
                else:
                    pass

    except Exception as e:
        logger.exception(e)

def checkRank():

    # Bring in global variables
    global character_rank

    # Check character rank information
    logger.info(f"Checking rank of {args.user}...")
    try:
        with open("score.txt", "r") as f:
            for line in f:
                if args.user in line:
                    i = line.split(" ")
                    character_rank = i[0]
                else:
                    pass

    except Exception as e:
        logger.exception(e)

def buyFood():

    # Clear buffer before issuing commands
    clearBuffer()

    # Tries to buy food for the player
    logger.info(f"Buying food for {args.user}...")
    tn.write(b"buy food\n")
    sleep(1)

# Ship functions

def updateShip():

    # Clear buffer before issuing commands
    clearBuffer()

    # Check ship status information
    logger.info(f"Updating ship info of {args.user}...")
    tn.write(b"st\n")
    sleep(1)
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
    logger.info(f"Checking fuel of {args.user}'s ship...")
    try:
        with open("ship.txt", "r") as f:
            for line in f:
                if "Fuel:" in line:
                    i = line.split(" ")
                    ii = i[13]
                    ii = ii.split("/")
                    current_fuel = int(ii[0])
                    fuel_max = int(ii[1])
                else:
                    pass

    except Exception as e:
        logger.exception(e)

def checkCargo():

    # Bring in global variables
    global current_cargo
    global cargo_max

    # Check character location information
    logger.info(f"Checking cargo space of {args.user}'s ship...")
    try:
        with open("ship.txt", "r") as f:
            for line in f:
                if "Cargo space:" in line:
                    i = line.split(" ")
                    i = i[7]
                    i = i.split("/")
                    current_cargo = int(i[0])
                    cargo_max = int(i[1])
                    current_cargo = (cargo_max - current_cargo)
                else:
                    pass

    except Exception as e:
        logger.exception(e)

def buyFuel():

    # Clear buffer before issuing commands
    clearBuffer()

    # Tries to buy fuel for the player's ship
    logger.info(f"Buying fuel for {args.user}'s ship...")
    tn.write(b"buy fuel\n")
    sleep(1)

# Planet/Exchange functions

def updatePlanet():

    # Clear buffer before issuing commands
    clearBuffer()

    # Check planetary exchange information
    logger.info(f"Updating {HOME_PLANET} planet information...")
    tn.write(b"di planet " + str.encode(HOME_PLANET) + b"\n")
    sleep(1)
    planet = tn.read_very_eager().decode("ascii")
    planet = escape_ansi(planet)

    # Write score output to file
    file = open("planet.txt", "w")
    f = file.write(planet)
    file.close()

def checkTreasury():

    # Bring in global variables
    global treasury

    # Check character location information
    logger.info(f"Checking treasury of {HOME_PLANET}...")
    try:
        with open("planet.txt", "r") as f:
            for line in f:
                if "Treasury:" in line:
                    i = line.split(" ")
                    i = i[3]
                    i = i[:-3]
                    i = i.split(",")
                    i = "".join(i)
                    i = int(i)
                    treasury = i
                else:
                    pass

    except Exception as e:
        logger.exception(e)

def updateExchange():

    # Bring in global variables
    global HOME_PLANET

    # Clear buffer before issuing commands
    clearBuffer()

    # Check planetary exchange information
    logger.info(f"Updating {HOME_PLANET} exchange information...")
    tn.write(b"di exchange " + str.encode(HOME_PLANET) + b"\n")
    sleep(1)
    exchange = tn.read_very_eager().decode("ascii")
    exchange = escape_ansi(exchange)

    # Write score output to file
    file = open("exchange.txt", "w")
    f = file.write(exchange)
    file.close()

def parseExchange():

    # Bring in global variables
    global exchange_dict

    # parse plaintext exchange data and extract current data
    logger.info("Pulling exchange data into dictionary...")
    try:
        with open("exchange.txt", "r") as f:
            lines = nonblank_lines(f)
            for line in lines:
                if "Stock: current" in line:
                    i = line.split(" ")
                    i = list(filter(None, i))
                    commodity = i[0]
                    commodity = commodity[:-1]
                    current = i[7]
                    current = current.split("/")
                    current = current[0]
                    max = i[9]
                    exchange_dict[commodity] = {"Current": current, "Max": max}
                else:
                    pass

    except Exception as e:
        logger.exception(e)

def checkCurrentCommodity(commodity):

    # Bring in global variables
    global exchange_dict

    # temporary variables
    current = 0

    # parse plaintext exchange data and extract current data
    logger.info("Checking current commodity level required...")
    try:
        with open("exchange.txt", "r") as f:
            lines = nonblank_lines(f)
            for line in lines:
                if commodity in line:
                    i = line.split(" ")
                    i = list(filter(None, i))
                    current = i[7]
                    current = current.split("/")
                    current = int(current[0])
                    exchange_dict[commodity] = {"Current": current}
                else:
                    pass

    except Exception as e:
        logger.exception(e)

    return current

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

def checkCommodityThreshold(commodity, planet):

    # idea is to check current commodity value for comparison against SURPLUS constant

    # global variables
    global SURPLUS

    # temp variables
    i = 0

    # Clear buffer before issuing commands
    clearBuffer()

    # Checks commodity level of remote exchange
    logger.info(f"Checking {commodity} level of {planet} exchange...")
    tn.write(b"c price " + str.encode(commodity) + b" " + str.encode(planet) + b"\n")
    sleep(1)
    price = tn.read_very_eager().decode("ascii")
    price = escape_ansi(price)

    # Write score output to file
    file = open("price.txt", "w")
    f = file.write(price)
    file.close()

    # Check commodity level
    try:
        with open("price.txt", "r") as f:
            for line in f:
                if "+++ Exchange has" in line:
                    i = line.split(" ")
                    i = int(i[3])

    except Exception as e:
        logger.exception(e)

    if i < SURPLUS:
        return True
    else:
        return False

# Move functions

def boardPlanet():

    # Lands or lifts off from planet
    logger.info("Boarding planet...")
    tn.write(b"board\n")
    sleep(1)

def moveDirection(direction):

    # Moves in a direction the function takes as an argument
    logger.info(f"Moving {direction}...")
    tn.write(str.encode(direction) + b"\n")
    sleep(1)

def jumpSystem(system):

    # Moves to a new system or cartel from the inter-stellar link
    logger.info(f"Jumping to {system}...")
    tn.write(b"jump " + str.encode(system) + b"\n")
    sleep(1)

# Trade functions

def checkIfBuying(commodity, planet):

    # idea is to only find planets that are buying, not buying and selling
    # which implies this commodity is a surplus on their planet and is not
    # profitable to sell to

    # temp variables
    i = False  # is it buying?
    ii = False  # is it selling?

    # Clear buffer before issuing commands
    clearBuffer()

    # Checks if a remote exchange is buying a commodity or not
    logger.info(f"Checking if {planet} is buying {commodity}...")
    tn.write(b"c price " + str.encode(commodity) + b" " + str.encode(planet) + b"\n")
    sleep(1)
    price = tn.read_very_eager().decode("ascii")
    price = escape_ansi(price)

    # Write score output to file
    file = open("price.txt", "w")
    f = file.write(price)
    file.close()

    # Check price
    try:
        with open("price.txt", "r") as f:
            for line in f:  # check if buying - first variable check
                if "+++ Exchange will buy" in line:
                    logger.info(f"Remote exchange is buying {commodity}.")
                    i = True
                else:
                    pass

            for line in f:  # check if selling - second variable check
                if "+++ Offer price is" in line:
                    logger.info(f"Remote exchange is selling {commodity}.")
                    ii = True
                else:
                    pass

    except Exception as e:
        logger.exception(e)

    # Evaluate whether we should sell to this exchange or not
    if i == True and ii != True:
        return True
    elif i == True and ii == True:
        return False
    else:
        return False

def buyCommodity(commodity):

    # Used to buy commodities at an exchange
    logger.info(f"Buying {commodity}...")
    tn.write(b"buy " + str.encode(commodity) + b"\n")
    sleep(1)

def checkIfSelling(commodity, planet):

    # idea is to only find planets that are selling and have current stock
    # above a certain threshold.

    # temp variables
    i = 0  # commodity current value
    ii = False  # is exchange selling?

    # Clear buffer before issuing commands
    clearBuffer()

    # Checks if a remote exchange is buying a commodity or not
    logger.info(f"Checking if {planet} is selling {commodity}...")
    tn.write(b"c price " + str.encode(commodity) + b" " + str.encode(planet) + b"\n")
    sleep(1)
    price = tn.read_very_eager().decode("ascii")
    price = escape_ansi(price)

    # Write score output to file
    file = open("price.txt", "w")
    f = file.write(price)
    file.close()

    # Check price
    try:
        with open("price.txt", "r") as f:
            for line in f:
                if "not currently trading" in line:
                    logger.info(f"Remote exchange is not selling {commodity}")
                elif "tons for sale" in line:
                    logger.info(f"Remote exchange is selling {commodity}.")
                    ii = True
                    iii = line.split(" ")
                    i = int(iii[3])
                else:
                    pass

    except Exception as e:
        logger.exception(e)

    # Check threshold and True/False
    if ii == True and i > 7500:
        return True
    else:
        return False

def sellCommodity(commodity):

    # Used to sell commodities at an exchange
    logger.info(f"Selling {commodity}...")
    tn.write(b"sell " + str.encode(commodity) + b"\n")
    sleep(1)

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
    updateScore()  # Required before any other check can run
    sleep(1)
    checkBalance()  # How much money do we have right now?
    sleep(1)
    checkStamina()  # How much stamina do we have right now?
    sleep(1)
    checkLocation()  # What planet and system are we on right now?
    sleep(1)

def ship():

    # Runs all ship functions with slight delay
    updateShip()  # Required before any other check can run
    sleep(1)
    checkFuel()  # How much fuel do we have right now?
    sleep(1)
    checkCargo()  # How much cargo do we have right now?
    sleep(1)

def planet():

    # Runs all planet functions with slight delay
    updatePlanet()  # Required before any other update can run
    sleep(1)
    checkTreasury()  # How much money does the treasury have right now?
    sleep(1)

def exchange():

    # Runs all planet exchange functions with slight delay
    updateExchange()  # Required before any other update can run
    sleep(1)
    parseExchange()  # Convert plain text to dictionary
    sleep(1)
    checkDeficits()
    sleep(1)
    checkSurpluses()
    sleep(1)

def gatherData():

    # Runs all multi functions

    while True:
        try:
            player()
            sleep(1)

        except Exception as e:
            logger.error("Ran into error running player function.  Please try again.")
            logger.exception(e)

        try:
            ship()
            sleep(1)

        except Exception as e:
            logger.error("Ran into error running ship function.  Please try again.")
            logger.exception(e)

        try:
            planet()
            sleep(1)

        except Exception as e:
            logger.error("Ran into error running planet function.  Please try again.")
            logger.exception(e)

        try:
            exchange()
            sleep(1)

        except Exception as e:
            logger.error("Ran into error running exchange function.  Please try again.")
            logger.exception(e)

        break
