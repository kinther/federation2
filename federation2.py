#!/usr/bin/python3

# Federation 2 Community Edition automation scripts for planet owners
# version 1.1 "Anomalous Alloys"
# Written by Strahd of the Barovia system
# Please don't tell anyone how I script *Lenny face*

# Imports
import telnetlib  # used to do all things telnet
import time  # used to provide sleep function
import datetime  # used to provide logging filename
import re  # used to escape ansi characters
import json  # used to read planets.json file
import logging  # used to write logs to file
import os  # used to delete files
import argparse  # used to pass user/password credentials
import sys  # used to exit script if criteria is met

# argparse constants
parser = argparse.ArgumentParser()
parser.add_argument("--user", type=str, action="store", required=True)
parser.add_argument("--password", type=str, action="store", required=True)
args = parser.parse_args()

# Telnetlib variables
host = "play.federation2.com"  # don't change this
port = 30003  # don't change this
timeout = 90  # maybe change this

# telnetlib constants
tn = telnetlib.Telnet(host, port, timeout=timeout)

# Logging constants
now = datetime.datetime.now()
day = now.strftime("%a")
hour = now.strftime("%H")
minute = now.strftime("%M")
LOG_FILENAME = (day + "-" + hour + minute + "-fed2.txt")
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
logger = logging.getLogger()

# Character constants
HOME_PLANET = "Ravenloft"  # constant variable used to check exchange info
DEFICIT = -75  # How much we consider a deficit
SURPLUS = 15000  # How much we consider a surplus

# Character variables
balance = 0  # character's current balance, from output of score
current_stamina = 0  # character's current stamina, from output of score
stamina_min = 20  # lowest stamina level we want our character to fall to
stamina_max = 0  # character's maximum stamina level, from output of score
current_system = ""  # character is on this planet, from output of score
current_planet = ""  # character is in this system, from output of score

# Ship variables
current_fuel = 0  # ship's current fuel level, from output of st
fuel_min = 100  # lowest fuel level we want our ship to fall to
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

    # Wait for Login prompt, then write username and hit enter
    tn.read_until(b"Login:")
    tn.write((args.user).encode("ascii") + b"\n")
    time.sleep(2)

    # Wait for Password prompt, then write password and hit enter
    tn.read_until(b"Password:")
    tn.write((args.password).encode("ascii") + b"\n")
    time.sleep(2)

    # Wait for string indicating we have logged in successfully
    tn.read_until(b"Linking to Federation DataSpace.")
    logger.info(f"Logged in successfully to {host} on port {port} as {args.user}.")
    time.sleep(5)

def clearBuffer():
    # Attempts to clear the buffer
    tn.write(b"\n")
    i = tn.read_very_eager().decode("ascii")
    time.sleep(3)

def escape_ansi(line):
    # https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi
    # -escape-sequences-from-a-string-in-python
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

def deleteFiles():

    while True:
        # deletes all generated files
        try:
            os.remove("score.txt")
            os.remove("ship.txt")
            os.remove("planet.txt")
            os.remove("exchange.txt")
            break
        except:
            continue
        break

# Character functions

def updateScore():

    # Clear buffer before issuing commands
    clearBuffer()

    # Check character score information
    logger.info(f"Updating score info of {args.user}...")
    tn.write(b"score\n")
    time.sleep(3)
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
    with open("score.txt", "r") as f:
        for line in f:
            if "Bank" in line:
                i = line.split(" ")  # remove whitespace
                i = i[4]  # select fourth entry in list
                i = i[:-3]  # remove last 3 characters from string
                i = i.split(",")  # parse output to remove comma separation
                i = "".join(i)  # rejoin list entries into single string
                i = int(i)  # turn string into integer
                balance = i

def checkStamina():

    # Bring in global variables
    global current_stamina
    global stamina_max

    # Check character stamina information
    logger.info(f"Checking stamina of {args.user}...")
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
    logger.info(f"Checking location of {args.user}...")
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
    logger.info(f"Buying food for {args.user}...")
    tn.write(b"buy food\n")
    time.sleep(3)

# Ship functions

def updateShip():

    # Clear buffer before issuing commands
    clearBuffer()

    # Check ship status information
    logger.info(f"Updating ship info of {args.user}...")
    tn.write(b"st\n")
    time.sleep(3)
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
    logger.info(f"Checking cargo space of {args.user}'s ship...")
    with open("ship.txt", "r") as f:
        for line in f:
            if "Cargo space" in line:
                i = line.split(" ")
                i = i[7]
                i = i.split("/")
                current_cargo = int(i[0])
                cargo_max = int(i[1])

def buyFuel():

    # Clear buffer before issuing commands
    clearBuffer()

    # Tries to buy fuel for the player's ship
    logger.info(f"Buying fuel for {args.user}'s ship...")
    tn.write(b"buy fuel\n")
    time.sleep(3)

# Planet/Exchange functions

def updatePlanet():

    # Clear buffer before issuing commands
    clearBuffer()

    # Check planetary exchange information
    logger.info(f"Updating {HOME_PLANET} planet information...")
    tn.write(b"di planet " + str.encode(HOME_PLANET) + b"\n")
    time.sleep(3)
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

def updateExchange():

    # Bring in global variables
    global HOME_PLANET

    # Clear buffer before issuing commands
    clearBuffer()

    # Check planetary exchange information
    logger.info(f"Updating {HOME_PLANET} exchange information...")
    tn.write(b"di exchange " + str.encode(HOME_PLANET) + b"\n")
    time.sleep(3)
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
    with open("exchange.txt", "r") as f:
        next(f)
        for line in f:
            i = line.split(" ")
            commodity = i[2]
            commodity = commodity[:-1]  # strip colon after commodity name
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
    time.sleep(3)

def moveDirection(direction):

    # Moves in a direction the function takes as an argument
    logger.info(f"Moving {direction}...")
    tn.write(str.encode(direction) + b"\n")
    time.sleep(3)

def jumpSystem(system):

    # Moves to a new system or cartel from the inter-stellar link
    logger.info(f"Jumping to {system}...")
    tn.write(b"jump " + str.encode(system) + b"\n")
    time.sleep(3)

# Trade functions

def checkPrice(commodity, planet):

    # Clear buffer before issuing commands
    clearBuffer()

    # Checks if a remote exchange is buying a commodity or not
    logger.info(f"Checking if {planet} is buying {commodity}...")
    tn.write(b"c price " + str.encode(commodity) + b" " + str.encode(planet) + b"\n")
    time.sleep(3)
    price = tn.read_very_eager().decode("ascii")
    price = escape_ansi(price)

    # Write score output to file
    file = open("price.txt", "w")
    f = file.write(price)
    file.close()

    # Check price
    with open("price.txt", "r") as f:
        for line in f:
            if "not currently trading" in line:
                logger.info(f"Remote exchange is not buying {commodity}")
                return False
            elif "Exchange will buy":
                logger.info(f"Remote exchange is buying {commodity}.")
                return True

def buyCommodity(commodity):

    # Used to buy commodities at an exchange
    logger.info(f"Buying {commodity}...")
    tn.write(b"buy " + str.encode(commodity) + b"\n")
    time.sleep(3)

def checkIfSelling(commodity, planet):

    # Clear buffer before issuing commands
    clearBuffer()

    # Checks if a remote exchange is buying a commodity or not
    logger.info(f"Checking if {planet} is selling {commodity}...")
    tn.write(b"c price " + str.encode(commodity) + b" " + str.encode(planet) + b"\n")
    time.sleep(3)
    price = tn.read_very_eager().decode("ascii")
    price = escape_ansi(price)

    # Write score output to file
    file = open("price.txt", "w")
    f = file.write(price)
    file.close()

    # Check price
    with open("price.txt", "r") as f:
        for line in f:
            if "not currently trading" in line:
                logger.info(f"Remote exchange is not selling {commodity}")
                return False
            elif "tons for sale":
                logger.info(f"Remote exchange is selling {commodity}.")
                return True

def sellCommodity(commodity):

    # Used to sell commodities at an exchange
    logger.info(f"Selling {commodity}...")
    tn.write(b"sell " + str.encode(commodity) + b"\n")
    time.sleep(3)

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
    time.sleep(3)
    checkBalance()  # How much money do we have right now?
    time.sleep(3)
    checkStamina()  # How much stamina do we have right now?
    time.sleep(3)
    checkLocation()  # What planet and system are we on right now?
    time.sleep(3)

def ship():

    # Runs all ship functions with slight delay
    updateShip()  # Required before any other check can run
    time.sleep(3)
    checkFuel()  # How much fuel do we have right now?
    time.sleep(3)
    checkCargo()  # How much cargo do we have right now?
    time.sleep(3)

def planet():

    # Runs all planet functions with slight delay
    updatePlanet()  # Required before any other update can run
    time.sleep(3)
    checkTreasury()  # How much money does the treasury have right now?
    time.sleep(3)

def exchange():

    # Runs all planet exchange functions with slight delay
    updateExchange()  # Required before any other update can run
    time.sleep(3)
    parseExchange()  # Convert plain text to dictionary
    time.sleep(3)
    checkDeficits()
    time.sleep(3)
    checkSurpluses()
    time.sleep(3)

def gatherData():

    while True:
        try:
            # Runs all multi functions
            player()
            time.sleep(3)
            ship()
            time.sleep(3)
            planet()
            time.sleep(3)
            exchange()
            time.sleep(3)
            deleteFiles()
            time.sleep(3)
            break
        except IndexError:
            logger.info("IndexError occurred, trying again...")
            continue
        except ValueError:
            logger.info("ValueError occurred, trying again...")
            continue
        break


# Main function

def main():

    print("Starting up... please check logging file for more info...")
    # Perform initial setup and gather game data
    try:
        login()
        time.sleep(3)
        gatherData()
        time.sleep(3)
    except Exception as e:
        logger.error("Ran into error during initial setup and gathering data.")
        logger.error(e)

    # Check if current_planet = HOME_PLANET.  If not, exit script.
    if HOME_PLANET not in current_planet:
        print("Character must be on their home planet on the landing pad.")
        print(f"Detected character on {current_planet} rather than {HOME_PLANET}.}")
        print("Exiting.")
        sys.exit(0)
    else:
        pass

    # global variables
    global deficits
    global surpluses
    global balance
    global treasury

    # while loop variables
    iter = 0  # how many times have we gone through the loop?
    bays = 0  # starting amount of bays to buy
    remote_planet_id = ""  # picked from planets.json and pinned
    prev_balance = 0  # how much money pc had last iteration
    diff_balance = 0  # difference +/- gained from last iteration
    prev_treasury = 0  # how much planet treasury had last iteration
    diff_treasury = 0  # difference +/- gained from last iteration

    # Open planets.json file
    f = open("planets.json")
    data = json.load(f)

    while True:

        # Iteration checks
        logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        logger.info(f" This is iteration number {iter}.")
        logger.info(f" {args.user}'s bank balance is {balance}.")
        logger.info(f" That's a difference of {diff_balance} compared to last iteration.")
        logger.info(f" {HOME_PLANET}'s treasury value is {treasury}.")
        logger.info(f" That's a difference of {diff_treasury} compared to last iteration.")
        logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        # Pause for 30 minutes if deficits list is empty
        while True:
            if len(deficits) > 0:  # is deficits list empty yet?
                break
            else:
                logger.info("Deficits all filled.  Sleeping for 30 minutes...")
                tn.write(b"say All deficits filled.  Sleeping for 30 minutes.\n")
                for i in range(30):  # Keepalive function so BrokenPipe does not occur
                    tn.write(b"\n")
                    time.sleep(60)
                clearBuffer()  # clear buffer, who knows what happened in 30 mins
                time.sleep(3)
                exchange()  # run exchange functions
                time.sleep(3)
                continue

        # Deficits loop specific vars
        def_item = deficits[0]
        tn.write(b"say Deficit needed is " + str.encode(def_item) + b".\n")

        # Buy fuel and food
        if current_fuel < fuel_min:
            buyFuel()
            logger.info("Current fuel is below minimum, buying fuel.")
            time.sleep(3)
        else:
            logger.info("Current fuel is above minimum.")
            pass
        if current_stamina < stamina_min:
            for dir in data[HOME_PLANET]["LP_to_Restaurant"]:
                moveDirection(dir)
                time.sleep(3)
            buyFood()
            logger.info("Current stamina is below minimum, buying food.")
            for dir in data[HOME_PLANET]["Restaurant_to_LP"]:
                moveDirection(dir)
                time.sleep(3)
        else:
            logger.info("Current stamina is above minimum.")
            pass

        # Determine which planet to buy deficits[cycle] from
        while True:
            for entry in data:
                if HOME_PLANET not in entry:
                    if def_item in data[entry]["Sell"]:
                        remote_planet_id = entry
                        break
                    else:
                        logger.info(f"{entry} does not sell {def_item}, moving on...")

            if len(remote_planet_id) > 0:
                logger.info(f"Will buy {def_item} from {remote_planet_id}...")
                break
            else:
                continue

        # Determine how many bays to buy of deficit[cycle]
        bays = deficitToBays(def_item)
        logger.info(f"Will buy {bays} bays of deficit from remote planet...")
        tn.write(b"say Will buy " + str.encode(str(bays)) + b" " + str.encode(def_item) + b".\n")

        # Board planet
        boardPlanet()
        time.sleep(3)

        # Jump to remote system
        if data[HOME_PLANET]["Cartel"] in data[remote_planet_id]["Cartel"]:
            logger.info("Jumping to remote system in same cartel...")
            jumpSystem(data[remote_planet_id]["System"])
            time.sleep(3)
        else:
            logger.info("Jumping to remote system in remote cartel...")
            jumpSystem(data[HOME_PLANET]["Cartel"])
            time.sleep(3)
            jumpSystem(data[remote_planet_id]["Cartel"])
            time.sleep(3)
            jumpSystem(data[remote_planet_id]["System"])
            time.sleep(3)

        # Move to remote planet from ISL
        logger.info(f"Moving to {remote_planet_id} from ISL...")
        for dir in data[remote_planet_id]["ISL_to_Planet"]:
            moveDirection(dir)
            time.sleep(3)

        # Board planet
        boardPlanet()
        time.sleep(3)

        # Move to exchange
        logger.info("Moving to exchange from landing pad...")
        for dir in data[remote_planet_id]["LP_to_Exchange"]:
            moveDirection(dir)
            time.sleep(3)

        # Buy deficits from remote exchange
        logger.info("Buying deficit from remote exchange...")
        for _ in range(bays):
            buyCommodity(def_item)
            time.sleep(2)
        time.sleep(3)

        # Move to landing pad
        logger.info("Moving to landing pad from exchange...")
        for dir in data[remote_planet_id]["Exchange_to_LP"]:
            moveDirection(dir)
            time.sleep(3)

        # Board planet
        boardPlanet()
        time.sleep(3)

        # Move to ISL from remote planet
        logger.info(f"Moving to ISL from {remote_planet_id}...")
        for dir in data[remote_planet_id]["Planet_to_ISL"]:
            moveDirection(dir)
            time.sleep(3)

        # Jump to remote system
        if data[remote_planet_id]["Cartel"] in data[HOME_PLANET]["Cartel"]:
            logger.info("Jumping to remote system in same cartel...")
            jumpSystem(data[HOME_PLANET]["System"])
            time.sleep(3)
        else:
            logger.info("Jumping to remote system in remote cartel...")
            jumpSystem(data[remote_planet_id]["Cartel"])
            time.sleep(3)
            jumpSystem(data[HOME_PLANET]["Cartel"])
            time.sleep(3)
            jumpSystem(data[HOME_PLANET]["System"])
            time.sleep(3)

        # Board planet
        boardPlanet()
        time.sleep(3)

        # Move to exchange
        logger.info("Moving to exchange from landing pad...")
        for dir in data[HOME_PLANET]["LP_to_Exchange"]:
            moveDirection(dir)
            time.sleep(3)

        # Sell goods
        logger.info("Selling deficit item to remote exchange...")
        for _ in range(bays):
            sellCommodity(def_item)
            time.sleep(2)
        time.sleep(3)

        # Move to landing pad
        logger.info("Moving to landing pad from exchange...")
        for dir in data[HOME_PLANET]["Exchange_to_LP"]:
            moveDirection(dir)
            time.sleep(3)

        # Iteration data updates to keep things fresh
        iter += 1

        prev_balance = balance  # how much we had before cycle began
        player()  # gather new player data
        time.sleep(2)
        diff_balance = (balance-prev_balance)  # how much we made this iteration

        ship()  # gather new ship data
        time.sleep(2)
        prev_treasury = treasury  # how much we had before cycle began

        planet()  # gather new planet data
        time.sleep(2)
        diff_treasury = (treasury-prev_treasury)  # how much we made this iteration

        os.remove("score.txt")  # remove files
        os.remove("ship.txt")  # remove files
        os.remove("planet.txt")  # remove files
        logger.info("Removing entry from deficits list...")
        tn.write(b"say Filled " + str.encode(def_item) + b".\n")
        deficits.pop(0)
        time.sleep(3)

if __name__ == "__main__":
    main()
