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
import fed_vars as v  # used to makes variables global across files

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

# Character/ship constants
HOME_PLANET = args.planet  # passed from player arguments
DEFICIT = -75  # How much we consider a deficit
SURPLUS = 18000  # How much we consider a surplus

# Global functions

def login():

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
    v.score = tn.read_very_eager().decode("ascii")
    v.score = escape_ansi(v.score)

def checkRemoteService():

    # Check whether character has remote service or not
    logger.info(f"Checking whether {args.user} has remote service...")

    try:
        tn.write(b"c price alloys earth" + b"\n")
        i = tn.read_very_eager().decode("ascii")
        if "remote access subscription" in i:
            logger.info(f"Found {args.user} does not have remote service.")
            logger.info("Closing down.  Remote service is required to run this script.")
            exit(0)
        else:
            logger.info(f"Appears that {args.user} has remote service subscription.")
            logger.info("Moving on.")
            pass

    except Exception as e:
        logger.exception(e)

def checkBalance():

    # Check character balance information
    logger.info(f"Checking bank balance of {args.user}...")
    try:
        for line in v.score.splitlines():
            if "Bank Balance:" in line:
                i = line.split(" ")  # remove whitespace
                i = i[4]  # select fourth entry in list
                i = i[:-3]  # remove last 3 characters from string
                i = i.split(",")  # parse output to remove comma separation
                i = "".join(i)  # rejoin list entries into single string
                i = int(i)  # turn string into integer
                v.balance = i
            else:
                pass

    except Exception as e:
        logger.exception(e)

    logger.info(f"Balance of {args.user} found to be {v.balance}.")

def checkStamina():

    # Check character stamina information
    logger.info(f"Checking stamina of {args.user}...")
    try:
        for line in v.score.splitlines():
            if "Stamina" in line:
                i = line.split(" ")
                i = i[9]
                i = i.split("/")
                v.current_stamina = int(i[0])
                imax = i[1]
                v.stamina_max = int(imax[:-1])
            else:
                pass

    except Exception as e:
        logger.exception(e)

    logger.info(f"Stamina of {args.user} found to be {v.current_stamina}.")

def checkLocation():

    # Check character location information
    logger.info(f"Checking location of {args.user}...")
    try:
        for line in v.score.splitlines():
            if "You are currently on" in line:
                i = line.split(" ")
                v.current_planet = i[6]
                v.current_system = i[9]
            else:
                pass

    except Exception as e:
        logger.exception(e)

    logger.info(f"Location of {args.user} found to be {v.current_planet} in the {v.current_system} system.")

def checkRank():

    # Check character rank information
    logger.info(f"Checking rank of {args.user}...")
    try:
        for line in v.score.splitlines():
            if args.user in line:
                i = line.split(" ")
                v.character_rank = i[0]
            else:
                pass

    except Exception as e:
        logger.exception(e)

    logger.info(f"Rank of {args.user} found to be {v.character_rank}.")

# Ship functions

def updateShip():

    # Clear buffer before issuing commands
    clearBuffer()

    # Check ship status information
    logger.info(f"Updating ship info of {args.user}...")
    tn.write(b"st\n")
    sleep(1)
    v.ship = tn.read_very_eager().decode("ascii")
    v.ship = escape_ansi(v.ship)

def checkFuel():

    # Check character location information
    logger.info(f"Checking fuel of {args.user}'s ship...")
    try:
        for line in v.ship.splitlines():
            if "Fuel:" in line:
                i = line.split(" ")
                ii = i[13]
                ii = ii.split("/")
                v.current_fuel = int(ii[0])
                v.fuel_max = int(ii[1])
            else:
                pass

    except Exception as e:
        logger.exception(e)

    logger.info(f"Fuel of {args.user}'s ship found to be {v.current_fuel}.")

def checkCargo():

    # Check character location information
    logger.info(f"Checking cargo space of {args.user}'s ship...")
    try:
        for line in v.ship.splitlines():
            if "Cargo space:" in line:
                i = line.split(" ")
                i = i[7]
                i = i.split("/")
                v.current_cargo = int(i[0])
                v.cargo_max = int(i[1])
                v.current_cargo = (v.cargo_max - v.current_cargo)
            else:
                pass

    except Exception as e:
        logger.exception(e)

    logger.info(f"Cargo load of {args.user}'s ship found to be {v.current_cargo}.")

def buyFuel():

    # Clear buffer before issuing commands
    clearBuffer()

    # Tries to buy fuel for the player's ship
    logger.info(f"Buying fuel for {args.user}'s ship...")
    tn.write(b"buy fuel\n")
    sleep(1)

# Planet functions

def updatePlanet():

    # Clear buffer before issuing commands
    clearBuffer()

    # Check planetary exchange information
    logger.info(f"Updating {HOME_PLANET} planet information...")
    tn.write(b"di planet " + str.encode(HOME_PLANET) + b"\n")
    sleep(1)
    v.planet = tn.read_very_eager().decode("ascii")
    v.planet = escape_ansi(v.planet)

def checkTreasury():

    # Check character location information
    logger.info(f"Checking treasury of {HOME_PLANET}...")
    try:
        for line in v.planet.splitlines():
            if "Treasury:" in line:
                i = line.split(" ")
                i = i[3]
                i = i[:-3]
                i = i.split(",")
                i = "".join(i)
                i = int(i)
                v.treasury = i
            else:
                pass

    except Exception as e:
        logger.exception(e)

    logger.info(f"Treasury of {args.planet} found to be {v.treasury}.")

# Exchange functions

def updateExchange():

    # Bring in global variables
    global HOME_PLANET

    # Clear buffer before issuing commands
    clearBuffer()

    # Check planetary exchange information
    logger.info(f"Updating {HOME_PLANET} exchange information...")
    tn.write(b"di exchange " + str.encode(HOME_PLANET) + b"\n")
    sleep(1)
    v.exchange = tn.read_very_eager().decode("ascii")
    v.exchange = escape_ansi(v.exchange)

def parseExchange():

    # parse plaintext exchange data and extract current data
    logger.info("Pulling exchange data into dictionary...")
    try:
        lines = nonblank_lines(v.exchange.splitlines())
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
                v.exchange_dict[commodity] = {"Current": current, "Max": max}
            else:
                pass

    except Exception as e:
        logger.exception(e)

def checkCurrentCommodity(commodity):

    # temporary variables
    current = 0

    # parse plaintext exchange data and extract current data
    logger.info("Checking current commodity level required...")
    try:
        lines = nonblank_lines(v.exchange.splitlines())
        for line in lines:
            if commodity in line:
                i = line.split(" ")
                i = list(filter(None, i))
                current = i[7]
                current = current.split("/")
                current = int(current[0])
                v.exchange_dict[commodity] = {"Current": current}
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
    for commodity in v.exchange_dict:
        if int(v.exchange_dict[commodity]["Current"]) < DEFICIT:
            v.deficits.append(commodity)

def checkSurpluses():

    # Bring in global variables
    global SURPLUS

    # Checks what home planet has current surpluses of and writes to list
    logger.info("Checking home planet surpluses...")
    for commodity in v.exchange_dict:
        if int(v.exchange_dict[commodity]["Current"]) > SURPLUS:
            v.surpluses.append(commodity)

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

    # Check commodity level
    try:
        for line in price.splitlines():
            if "+++ Exchange has" in line:
                i = line.split(" ")
                i = int(i[3])

    except Exception as e:
        logger.exception(e)

    if i < SURPLUS:
        return True
    else:
        return False

# Consumable functions

def buyFood():

    # Clear buffer before issuing commands
    clearBuffer()

    # Tries to buy food for the player
    logger.info(f"Buying food for {args.user}...")
    tn.write(b"buy food\n")
    sleep(1)

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

    # Check price
    try:
        for line in price.splitlines():  # check if buying - first variable check
            if "+++ Exchange will buy" in line:
                logger.info(f"Remote exchange is buying {commodity}.")
                i = True
            else:
                pass

        for line in price.splitlines():  # check if selling - second variable check
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

    # Check price
    try:
        for line in price.splitlines():
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

    # Temporary variables
    bays = 0

    # Used to determine how many bays of a deficit to buy
    logger.info(f"Identifying how many bays to buy of {commodity}...")
    # Check current deficit value by parsing dictionary based on commodity key
    for item in v.exchange_dict:
        if commodity in item:
            bays = int(v.exchange_dict[commodity]["Current"])
            bays = int((bays / 75) * -1)

    return bays

# System functions

def updateSystem():

    # Clear buffer before issuing commands
    clearBuffer()

    # Check system data
    logger.info(f"Checking current system information...")
    tn.write(b"di system" + b"\n")
    sleep(1)
    v.system = tn.read_very_eager().decode("ascii")
    v.system = escape_ansi(v.system)

def checkPlanetOwner():

    # Check di system output for ownership of other planets
    logger.info(f"Checking planet ownership in this system...")
    try:
        for line in v.system.splitlines():
            if "system - Owner" in line:
                if "Space," in line:
                    pass
                else:
                    i = line.split(" ")
                    if args.user in i[-1]:
                        if "," in i[0]:  # for planets with one word names
                            ii = i[0]
                            ii = list(ii)  # make list of string
                            ii.pop()  # remove comma from list
                            ii = "".join(ii)  # rejoin list into string
                            v.owned_planets.append(ii)
                        elif "," in i[1]: ## for planets with two word names:
                            ii = i[0]  # first name of planet
                            jj = i[1]  # second name of planet
                            jj = list(jj)
                            jj.pop()
                            jj = "".join(jj)
                            kk = ii + " " + jj
                            v.owned_planets.append(kk)
                        else:
                            pass  # someone could add a check for a third name here
            else:
                pass

    except Exception as e:
        logger.exception(e)

    if len(v.owned_planets) <= 1:  # only owns one planet
        logger.info(f"{args.user} owns the following planet:")
        for entry in v.owned_planets:
            logger.info(entry)
    else:  # must be more then one
        logger.info(f"{args.user} owns the following planets:")
        for entry in v.owned_planets:
            logger.info(entry)   


# Cartel functions

def updateCartel():

    # Clear buffer before issuing commands
    clearBuffer()

    # Check system data
    logger.info(f"Checking current system information...")
    tn.write(b"di cartel" + b"\n")
    sleep(1)
    v.cartel = tn.read_very_eager().decode("ascii")
    v.cartel = escape_ansi(v.cartel)

# Multi functions

def player_data():

    # Runs all player functions with slight delay
    updateScore()  # Required before any other check can run
    sleep(1)
    checkBalance()  # How much money do we have right now?
    sleep(1)
    checkStamina()  # How much stamina do we have right now?
    sleep(1)
    checkLocation()  # What planet and system are we on right now?
    sleep(1)

def ship_data():

    # Runs all ship functions with slight delay
    updateShip()  # Required before any other check can run
    sleep(1)
    checkFuel()  # How much fuel do we have right now?
    sleep(1)
    checkCargo()  # How much cargo do we have right now?
    sleep(1)

def planet_data():

    # Runs all planet functions with slight delay
    updatePlanet()  # Required before any other update can run
    sleep(1)
    checkTreasury()  # How much money does the treasury have right now?
    sleep(1)

def exchange_data():

    # Runs all planet exchange functions with slight delay
    updateExchange()  # Required before any other update can run
    sleep(1)
    parseExchange()  # Convert plain text to dictionary
    sleep(1)
    checkDeficits()  # Checks deficits and makes list
    sleep(1)
    checkSurpluses()  # Checks surpluses and makes list
    sleep(1)

def system_data():

    # Runs all system functions with slight delay
    updateSystem()  # Required before any update or check can be run
    sleep(1)
    checkPlanetOwner()  # Which planets does the player own in this system?
    sleep(1)

def gatherData():

    # Runs all multi functions

    while True:
        try:
            player_data()
            sleep(1)

        except Exception as e:
            logger.error("Ran into error running player function.  Please try again.")
            logger.exception(e)

        try:
            ship_data()
            sleep(1)

        except Exception as e:
            logger.error("Ran into error running ship function.  Please try again.")
            logger.exception(e)

        try:
            planet_data()
            sleep(1)

        except Exception as e:
            logger.error("Ran into error running planet function.  Please try again.")
            logger.exception(e)

        try:
            exchange_data()
            sleep(1)

        except Exception as e:
            logger.error("Ran into error running exchange function.  Please try again.")
            logger.exception(e)

        try:
            system_data()
            sleep(1)

        except Exception as e:
            logger.error("Ran into error running system function.  Please try again.")
            logger.exception(e)

        break