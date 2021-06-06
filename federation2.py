#!/usr/bin/python3

# Federation 2 Community Edition hauling scripts for planet owners
# version 2.1 "Clandestine Clays"

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
parser.add_argument("--planet", type=str, action="store", required=True)
parser.add_argument("--mode", type=str, action="store", required=True)
args = parser.parse_args()

# global constants
ranks = ["Founder", "Engineer", "Mogul", "Technocrat", "Gengineer", "Magnate", "Plutrocrat"]
script_mode = (args.mode).lower()  # determines whether to focus on deficits or surpluses

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
HOME_PLANET = args.planet  # passed from player arguments
DEFICIT = -75  # How much we consider a deficit
SURPLUS = 18000  # How much we consider a surplus

# Character variables
balance = 0  # character's current balance, from output of score
current_stamina = 0  # character's current stamina, from output of score
stamina_min = 20  # lowest stamina level we want our character to fall to
stamina_max = 0  # character's maximum stamina level, from output of score
current_system = ""  # character is on this planet, from output of score
current_planet = ""  # character is in this system, from output of score
character_rank = ""  # character's rank, from output of score

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
    time.sleep(2)

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
    time.sleep(1)
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

def checkRank():

    # Bring in global variables
    global character_rank

    # Check character rank information
    logger.info(f"Checking rank of {args.user}...")
    with open("score.txt", "r") as f:
        for line in f:
            if args.user in line:
                i = line.split(" ")
                character_rank = i[0]

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
    time.sleep(1)
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
    time.sleep(1)

# Planet/Exchange functions

def updatePlanet():

    # Clear buffer before issuing commands
    clearBuffer()

    # Check planetary exchange information
    logger.info(f"Updating {HOME_PLANET} planet information...")
    tn.write(b"di planet " + str.encode(HOME_PLANET) + b"\n")
    time.sleep(1)
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
    time.sleep(1)
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
        lines = nonblank_lines(f)
        for line in lines:
            i = line.split(" ")
            i = list(filter(None, i))
            commodity = i[0]
            commodity = commodity[:-1]
            current = i[7]
            current = current.split("/")
            current = current[0]
            max = i[9]
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
    time.sleep(1)
    price = tn.read_very_eager().decode("ascii")
    price = escape_ansi(price)

    # Write score output to file
    file = open("price.txt", "w")
    f = file.write(price)
    file.close()

    # Check commodity level
    with open("price.txt", "r") as f:
        for line in f:
            if "+++ Exchange has" in line:
                i = line.split(" ")
                i = int(i[3])

    if i < SURPLUS:
        return True
    else:
        return False

# Move functions

def boardPlanet():

    # Lands or lifts off from planet
    logger.info("Boarding planet...")
    tn.write(b"board\n")
    time.sleep(1)

def moveDirection(direction):

    # Moves in a direction the function takes as an argument
    logger.info(f"Moving {direction}...")
    tn.write(str.encode(direction) + b"\n")
    time.sleep(1)

def jumpSystem(system):

    # Moves to a new system or cartel from the inter-stellar link
    logger.info(f"Jumping to {system}...")
    tn.write(b"jump " + str.encode(system) + b"\n")
    time.sleep(1)

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
    time.sleep(1)
    price = tn.read_very_eager().decode("ascii")
    price = escape_ansi(price)

    # Write score output to file
    file = open("price.txt", "w")
    f = file.write(price)
    file.close()

    # Check price
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
    time.sleep(1)

def checkIfSelling(commodity, planet):

    # Clear buffer before issuing commands
    clearBuffer()

    # Checks if a remote exchange is buying a commodity or not
    logger.info(f"Checking if {planet} is selling {commodity}...")
    tn.write(b"c price " + str.encode(commodity) + b" " + str.encode(planet) + b"\n")
    time.sleep(1)
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
    time.sleep(1)

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
    time.sleep(1)
    checkBalance()  # How much money do we have right now?
    time.sleep(1)
    checkStamina()  # How much stamina do we have right now?
    time.sleep(1)
    checkLocation()  # What planet and system are we on right now?
    time.sleep(1)

def ship():

    # Runs all ship functions with slight delay
    updateShip()  # Required before any other check can run
    time.sleep(1)
    checkFuel()  # How much fuel do we have right now?
    time.sleep(1)
    checkCargo()  # How much cargo do we have right now?
    time.sleep(1)

def planet():

    # Runs all planet functions with slight delay
    updatePlanet()  # Required before any other update can run
    time.sleep(1)
    checkTreasury()  # How much money does the treasury have right now?
    time.sleep(1)

def exchange():

    # Runs all planet exchange functions with slight delay
    updateExchange()  # Required before any other update can run
    time.sleep(1)
    parseExchange()  # Convert plain text to dictionary
    time.sleep(1)
    checkDeficits()
    time.sleep(1)
    checkSurpluses()
    time.sleep(1)

def gatherData():

    while True:
        try:
            # Runs all multi functions
            player()
            time.sleep(1)
            ship()
            time.sleep(1)
            planet()
            time.sleep(1)
            exchange()
            time.sleep(1)
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
        time.sleep(1)
        gatherData()
        time.sleep(1)
        checkRank()
        time.sleep(1)
        deleteFiles()
        time.sleep(1)
    except Exception as e:
        logger.error("Ran into error during initial setup and gathering data.")
        logger.error(e)

    # Check if character is sufficient rank to run script
    if character_rank not in ranks:
        logger.info("ERROR: This script is meant to be run by planet owners.")
        logger.info(f"Your current rank is detected as {character_rank}.")
        logger.info("Please re-run script when you rank up! Good luck :)")
        sys.exit(0)
    else:
        pass

    # Check if current_planet = HOME_PLANET.  If not, exit script.
    if HOME_PLANET not in current_planet:
        logger.info("ERROR: Character must be on their home planet on the landing pad.")
        logger.info(f"Detected character on {current_planet} rather than {HOME_PLANET}.")
        logger.info("Exiting.")
        sys.exit(0)
    else:
        pass

    # Check if cargo_max is less than 525 (can't haul a full 7 bays)
    if cargo_max < 525:
        i = str(cargo_max)
        logger.info("ERROR: Ship is not capable of hauling 525 tons of cargo right now.")
        logger.info(f"Detected {i} is the max tons we can haul.")
        logger.info("You may need to upgrade your ship in order to haul 525 tons.")
        logger.info("Exiting.")
        sys.exit(0)
    else:
        pass

    # Check if current_cargo is less than 525 (can't haul a full 7 bays)
    if current_cargo < 525:
        i = str(current_cargo)
        logger.info("ERROR: Ship is not capable of hauling 525 tons of cargo right now.")
        logger.info(f"Detected {i} is the max tons we can haul.")
        logger.info("Please sell some things from the hold and re-start script.")
        logger.info("Exiting.")
        sys.exit(0)
    else:
        pass


    # Check if current_cargo does not equal max cargo
    if current_cargo != cargo_max:
        i = str(cargo_max - current_cargo)
        logger.info("WARNING: Ship is hauling some cargo already in its hold.")
        logger.info(f"Detected {i} tons in use.")
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

    if "deficit" in script_mode:

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
                    time.sleep(1)
                    exchange()  # run exchange functions
                    time.sleep(1)
                    continue

            # Deficits loop specific vars
            def_item = deficits[0]

            # Buy fuel and food
            if current_fuel < fuel_min:
                buyFuel()
                logger.info("Current fuel is below minimum, buying fuel.")
                time.sleep(1)
            else:
                logger.info("Current fuel is above minimum.")
                pass
            if current_stamina < stamina_min:
                for dir in data[HOME_PLANET]["LP_to_Restaurant"]:
                    moveDirection(dir)
                    time.sleep(1)
                buyFood()
                logger.info("Current stamina is below minimum, buying food.")
                for dir in data[HOME_PLANET]["Restaurant_to_LP"]:
                    moveDirection(dir)
                    time.sleep(1)
            else:
                logger.info("Current stamina is above minimum.")
                pass

            # Determine which planet to buy deficits[cycle] from
            while True:

                i = False  # find out if deficit is in planets.json or not

                for entry in data:
                    if HOME_PLANET not in entry:
                        if def_item in data[entry]["Sell"]:
                            remote_planet_id = entry
                            i = True
                            break
                        else:
                            logger.info(f"{entry} does not sell {def_item}, moving on...")

                if i is False:
                    logger.info(f"WARNING: Could not find {def_item} in planets.json.")
                    logger.info("Please account for all deficits for maximum efficiency.")
                    logger.info(f"Removing {def_item} from deficit list.")
                    deficits.pop(0)
                    def_item = deficits[0]
                else:
                    if len(remote_planet_id) > 0:
                        def_item = deficits[0]
                        tn.write(b"say Deficit needed is " + str.encode(def_item) + b".\n")
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
            time.sleep(1)

            # Move to ISL from home planet
            logger.info(f"Moving to ISL from {HOME_PLANET} and not jumping...")
            for dir in data[HOME_PLANET]["Planet_to_ISL"]:
                moveDirection(dir)
                time.sleep(1)

            # Cartel/System jump logic
            # Local system logic
            if (data[HOME_PLANET]["System"] in data["remote_planet_id"]["System"])
            and (data[HOME_PLANET]["Cartel"] in data["remote_planet_id"]["Cartel"]):
                pass
            # Local cartel logic
            elif (data[HOME_PLANET]["System"] not in data["remote_planet_id"]["System"])
            and (data[HOME_PLANET]["Cartel"] in data["remote_planet_id"]["Cartel"]):
                logger.info("Jumping to remote system in same cartel...")
                jumpSystem(data[remote_planet_id]["System"])
                time.sleep(1)
            # Different cartel logic
            else:
                logger.info("Jumping to remote cartel...")
                jumpSystem(data[HOME_PLANET]["Cartel"])
                time.sleep(1)
                jumpSystem(data[remote_planet_id]["Cartel"])
                time.sleep(1)
                # Different cartel different system logic
                if data[remote_planet_id]["Cartel"] not in data[remote_planet_id]["System"]:
                    logger.info("Jumping to remote system...")
                    jumpSystem(data[remote_planet_id]["System"])
                    time.sleep(1)
                else:
                    pass

            # Move to remote planet from ISL
            logger.info(f"Moving to {remote_planet_id} from ISL...")
            for dir in data[remote_planet_id]["ISL_to_Planet"]:
                moveDirection(dir)
                time.sleep(1)

            # Board planet
            boardPlanet()
            time.sleep(1)

            # Move to exchange
            logger.info("Moving to exchange from landing pad...")
            for dir in data[remote_planet_id]["LP_to_Exchange"]:
                moveDirection(dir)
                time.sleep(1)

            # Buy deficits from remote exchange
            logger.info(f"Buying {def_item} from remote exchange...")
            for _ in range(bays):
                buyCommodity(def_item)
                time.sleep(1)
            time.sleep(1)

            # Move to landing pad
            logger.info("Moving to landing pad from exchange...")
            for dir in data[remote_planet_id]["Exchange_to_LP"]:
                moveDirection(dir)
                time.sleep(1)

            # Board planet
            boardPlanet()
            time.sleep(3)

            # Move to ISL from remote planet
            logger.info(f"Moving to ISL from {remote_planet_id} and not jumping...")
            for dir in data[remote_planet_id]["Planet_to_ISL"]:
                moveDirection(dir)
                time.sleep(1)

            # Cartel/System jump logic
            # Local cartel logic
            if (data[HOME_PLANET]["System"] in data["remote_planet_id"]["System"])
            and (data[HOME_PLANET]["Cartel"] in data["remote_planet_id"]["Cartel"]):
                pass
            # Local cartel logic
            elif (data[HOME_PLANET]["System"] not in data["remote_planet_id"]["System"])
            and (data[HOME_PLANET]["Cartel"] in data["remote_planet_id"]["Cartel"]):
                logger.info("Jumping to remote system in same cartel...")
                jumpSystem(data[HOME_PLANET]["System"])
                time.sleep(1)
            # Different cartel logic
            else:
                logger.info("Jumping to home cartel...")
                jumpSystem(data[remote_planet_id]["Cartel"])
                time.sleep(1)
                jumpSystem(data[HOME_PLANET]["Cartel"])
                time.sleep(1)
                # Different cartel different system logic
                if data[HOME_PLANET]["Cartel"] not in data[HOME_PLANET]["System"]:
                    logger.info("Jumping to home system...")
                    jumpSystem(data[HOME_PLANET]["System"])
                    time.sleep(1)
                else:
                    pass

            # Move to home planet from ISL
            logger.info(f"Moving to {HOME_PLANET} from ISL...")
            for dir in data[HOME_PLANET]["ISL_to_Planet"]:
                moveDirection(dir)
                time.sleep(1)

            # Board planet
            boardPlanet()
            time.sleep(1)

            # Move to exchange
            logger.info("Moving to exchange from landing pad...")
            for dir in data[HOME_PLANET]["LP_to_Exchange"]:
                moveDirection(dir)
                time.sleep(1)

            # Sell item to home exchange
            logger.info(f"Selling {def_item} to home exchange...")
            for _ in range(bays):
                sellCommodity(def_item)
                time.sleep(1)
            time.sleep(1)

            # Move to landing pad
            logger.info("Moving to landing pad from exchange...")
            for dir in data[HOME_PLANET]["Exchange_to_LP"]:
                moveDirection(dir)
                time.sleep(1)

            # Iteration data updates to keep things fresh
            iter += 1

            prev_balance = balance  # how much we had before cycle began
            player()  # gather new player data
            time.sleep(1)
            diff_balance = (balance-prev_balance)  # how much we made this iteration

            ship()  # gather new ship data
            time.sleep(1)
            prev_treasury = treasury  # how much we had before cycle began

            planet()  # gather new planet data
            time.sleep(1)
            diff_treasury = (treasury-prev_treasury)  # how much we made this iteration

            os.remove("score.txt")  # remove files
            os.remove("ship.txt")  # remove files
            os.remove("planet.txt")  # remove files
            logger.info("Removing entry from deficits list...")
            tn.write(b"say Filled " + str.encode(def_item) + b".\n")
            deficits.pop(0)
            time.sleep(1)

    elif "surplus" in script_mode:

        while True:

            # Iteration checks
            logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            logger.info(f" This is iteration number {iter}.")
            logger.info(f" {args.user}'s bank balance is {balance}.")
            logger.info(f" That's a difference of {diff_balance} compared to last iteration.")
            logger.info(f" {HOME_PLANET}'s treasury value is {treasury}.")
            logger.info(f" That's a difference of {diff_treasury} compared to last iteration.")
            logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            # Pause for 30 minutes if surpluses list is empty
            while True:
                if len(surpluses) > 0:  # is surpluses list empty yet?
                    break
                else:
                    logger.info("Surpluses all sold.  Sleeping for 30 minutes...")
                    tn.write(b"say All surpluses sold.  Sleeping for 30 minutes.\n")
                    for i in range(30):  # Keepalive function so BrokenPipe does not occur
                        tn.write(b"\n")
                        time.sleep(60)
                    clearBuffer()  # clear buffer, who knows what happened in 30 mins
                    time.sleep(1)
                    exchange()  # run exchange functions
                    time.sleep(1)
                    continue

            # Surpluses loop specific vars
            sur_item = surpluses[0]

            # Buy fuel and food
            if current_fuel < fuel_min:
                buyFuel()
                logger.info("Current fuel is below minimum, buying fuel.")
                time.sleep(1)
            else:
                logger.info("Current fuel is above minimum.")
                pass
            if current_stamina < stamina_min:
                for dir in data[HOME_PLANET]["LP_to_Restaurant"]:
                    moveDirection(dir)
                    time.sleep(1)
                buyFood()
                logger.info("Current stamina is below minimum, buying food.")
                for dir in data[HOME_PLANET]["Restaurant_to_LP"]:
                    moveDirection(dir)
                    time.sleep(1)
            else:
                logger.info("Current stamina is above minimum.")
                pass

            # Determine which planet to sell surpluses[cycle] from
            while True:

                i = False  # find out if surpluse is in planets.json or if not buying

                for entry in data:
                    if HOME_PLANET not in entry:
                        if sur_item in data[entry]["Buy"]:
                            if checkIfBuying(sur_item, entry) == True:
                                 remote_planet_id = entry
                                 i = True
                                 break
                            else:
                                continue
                        else:
                            logger.info(f"{entry} does not list {sur_item} as a Buy in planets.json.  Moving on...")

                if i is False:
                    logger.info(f"Removing {sur_item} from surplus list.")
                    surpluses.pop(0)
                    sur_item = surpluses[0]
                else:
                    if len(remote_planet_id) > 0:
                        sur_item = surpluses[0]
                        tn.write(b"say " + str.encode(sur_item) + b" is still on the surpluses list.\n")
                        logger.info(f"Will sell one {sur_item} to {remote_planet_id}...")
                        break
                    else:
                        continue

            # Move to exchange
            logger.info("Moving to exchange from landing pad...")
            for dir in data[HOME_PLANET]["LP_to_Exchange"]:
                moveDirection(dir)
                time.sleep(1)

            # Buy goods
            logger.info(f"Buying {sur_item} from home exchange...")
            buyCommodity(sur_item)
            time.sleep(1)

            # Move to landing pad
            logger.info("Moving to landing pad from exchange...")
            for dir in data[HOME_PLANET]["Exchange_to_LP"]:
                moveDirection(dir)
                time.sleep(1)

            # Board planet
            boardPlanet()
            time.sleep(1)

            # Move to ISL from home planet
            for dir in data[HOME_PLANET]["Planet_to_ISL"]:
                moveDirection(dir)
                time.sleep(1)

            # Cartel/System jump logic
            # Local system logic
            if (data[HOME_PLANET]["System"] in data["remote_planet_id"]["System"])
            and (data[HOME_PLANET]["Cartel"] in data["remote_planet_id"]["Cartel"]):
                pass
            # Local cartel logic
            elif (data[HOME_PLANET]["System"] not in data["remote_planet_id"]["System"])
            and (data[HOME_PLANET]["Cartel"] in data["remote_planet_id"]["Cartel"]):
                logger.info("Jumping to remote system in same cartel...")
                jumpSystem(data[remote_planet_id]["System"])
                time.sleep(1)
            # Different cartel logic
            else:
                logger.info("Jumping to remote cartel...")
                jumpSystem(data[HOME_PLANET]["Cartel"])
                time.sleep(1)
                jumpSystem(data[remote_planet_id]["Cartel"])
                time.sleep(1)
                # Different cartel different system logic
                if data[remote_planet_id]["Cartel"] not in data[remote_planet_id]["System"]:
                    logger.info("Jumping to remote system...")
                    jumpSystem(data[remote_planet_id]["System"])
                    time.sleep(1)
                else:
                    pass

            # Move to remote planet from ISL
            logger.info(f"Moving to {remote_planet_id} from ISL...")
            for dir in data[remote_planet_id]["ISL_to_Planet"]:
                moveDirection(dir)
                time.sleep(1)

            # Board planet
            boardPlanet()
            time.sleep(1)

            # Move to exchange
            logger.info("Moving to exchange from landing pad...")
            for dir in data[remote_planet_id]["LP_to_Exchange"]:
                moveDirection(dir)
                time.sleep(1)

            # Sell goods
            logger.info(f"Selling {sur_item} to remote exchange...")
            sellCommodity(sur_item)
            time.sleep(1)

            # Move to landing pad
            logger.info("Moving to landing pad from exchange...")
            for dir in data[remote_planet_id]["Exchange_to_LP"]:
                moveDirection(dir)
                time.sleep(1)

            # Board planet
            boardPlanet()
            time.sleep(3)

            # Move to ISL from remote planet
            logger.info(f"Moving to ISL from {remote_planet_id} and not jumping...")
            for dir in data[remote_planet_id]["ISL_to_Planet"]:
                moveDirection(dir)
                time.sleep(1)

            # Cartel/System jump logic
            # Local cartel logic
            if (data[HOME_PLANET]["System"] in data["remote_planet_id"]["System"])
            and (data[HOME_PLANET]["Cartel"] in data["remote_planet_id"]["Cartel"]):
                pass
            # Local cartel logic
            elif (data[HOME_PLANET]["System"] not in data["remote_planet_id"]["System"])
            and (data[HOME_PLANET]["Cartel"] in data["remote_planet_id"]["Cartel"]):
                logger.info("Jumping to remote system in same cartel...")
                jumpSystem(data[HOME_PLANET]["System"])
                time.sleep(1)
            # Different cartel logic
            else:
                logger.info("Jumping to home cartel...")
                jumpSystem(data[remote_planet_id]["Cartel"])
                time.sleep(1)
                jumpSystem(data[HOME_PLANET]["Cartel"])
                time.sleep(1)
                # Different cartel different system logic
                if data[HOME_PLANET]["Cartel"] not in data[HOME_PLANET]["System"]:
                    logger.info("Jumping to home system...")
                    jumpSystem(data[HOME_PLANET]["System"])
                    time.sleep(1)
                else:
                    pass

            # Move to home planet from ISL
            logger.info(f"Moving to {HOME_PLANET} from ISL...")
            for dir in data[HOME_PLANET]["ISL_to_Planet"]:
                moveDirection(dir)
                time.sleep(1)

            # Board planet
            boardPlanet()
            time.sleep(1)

            # Iteration data updates to keep things fresh
            iter += 1

            prev_balance = balance  # how much we had before cycle began
            player()  # gather new player data
            time.sleep(1)
            diff_balance = (balance-prev_balance)  # how much we made this iteration

            ship()  # gather new ship data
            time.sleep(1)
            prev_treasury = treasury  # how much we had before cycle began

            planet()  # gather new planet data
            time.sleep(1)
            diff_treasury = (treasury-prev_treasury)  # how much we made this iteration

            os.remove("score.txt")  # remove files
            os.remove("ship.txt")  # remove files
            os.remove("planet.txt")  # remove files
            os.remove("price.txt")  # remove files
            tn.write(b"say Sold " + str.encode(sur_item) + b" to " + str.encode(remote_planet_id) + b".\n")

            # check if we are below SURPLUS defined threshold
            if checkCommodityThreshold(sur_item, HOME_PLANET) == True:
                logger.info(f"{sur_item} is under SURPLUS defined threshold.  Removing from list.")
                surpluses.pop(0)
            else:
                logger.info(f"{sur_item} is above SURPLUS defined threshold.  Continuing.")

    else:

        # no mode selected or input was incorrect
        print("Mode must be either 'deficit' or 'surplus'.  Please re-run script.")
        logger.info("Mode must be either 'deficit' or 'surplus'.  Please re-run script.")
        sys.exit(0)

if __name__ == "__main__":
    main()
