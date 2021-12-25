#!/usr/bin/python3

# Federation 2 Community Edition hauling scripts for planet owners
# version 2.4 "Kurious Katydidics"

# Imports
from fed_utils import *  # used to pull in all custom functions from fed_utils.py

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

# Main function

def main():

    print("Starting up... please check logging file for more info...")
    # Perform initial setup and gather game data
    try:
        login()
        sleep(1)

    except Exception as e:
        logger.error("Ran into error during initial logon.  Please try again.")
        logger.exception(e)

    try:
        gatherData()
        sleep(1)

    except Exception as e:
        logger.error("Ran into error during initial gathering of data.  Please try again.")
        logger.exception(e)

    try:
        checkRank()
        sleep(1)

    except Exception as e:
        logger.error("Ran into error during check of character rank.  Please try again.")
        logger.exception(e)

    try:
        deleteFiles()
        sleep(1)

    except Exception as e:
        logger.error("Ran into error during initial deleting of files.  Please try again.")
        logger.exception(e)

    # Check if character is sufficient rank to run script
    if character_rank not in ranks:
        logger.info("ERROR: This script is meant to be run by planet owners.")
        logger.info(f"Your current rank is detected as {character_rank}.")
        logger.info("Please re-run script when you rank up! Good luck :)")
        exit(0)
    else:
        pass

    # Check if current_planet = HOME_PLANET.  If not, exit script.
    if HOME_PLANET not in current_planet:
        logger.info("ERROR: Character must be on their home planet on the landing pad.")
        logger.info(f"Detected character on {current_planet} rather than {HOME_PLANET}.")
        logger.info("Exiting.")
        exit(0)
    else:
        pass

    # Check if cargo_max is less than 525 (can't haul a full 7 bays)
    if cargo_max < 525:
        i = str(cargo_max)
        logger.info("ERROR: Ship is not capable of hauling 525 tons of cargo right now.")
        logger.info(f"Detected {i} is the max tons we can haul.")
        logger.info("You may need to upgrade your ship in order to haul 525 tons.")
        logger.info("Exiting.")
        exit(0)
    else:
        pass

    # Check if current_cargo is less than 525 (can't haul a full 7 bays)
    if (cargo_max - current_cargo) < 525:
        i = str(current_cargo)
        logger.info("ERROR: Ship is not capable of hauling 525 tons of cargo right now.")
        logger.info(f"Detected {i} is the max tons we can haul.")
        logger.info("Please sell some things from the hold and re-start script.")
        logger.info("Exiting.")
        exit(0)
    else:
        pass


    # Check if current_cargo does not equal max cargo
    if current_cargo > 0:
        i = str(current_cargo)
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
    data = load(f)

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
                        sleep(60)
                    clearBuffer()  # clear buffer, who knows what happened in 30 mins
                    sleep(1)
                    exchange()  # run exchange functions
                    sleep(1)
                    continue

            # Deficits loop specific vars
            def_item = deficits[0]

            # Buy fuel and food
            if current_fuel < fuel_min:
                buyFuel()
                logger.info("Current fuel is below minimum, buying fuel.")
                sleep(1)
            else:
                logger.info("Current fuel is above minimum.")
                pass
            if current_stamina < stamina_min:
                for dir in data[HOME_PLANET]["LP_to_Restaurant"]:
                    moveDirection(dir)
                    sleep(1)
                buyFood()
                logger.info("Current stamina is below minimum, buying food.")
                for dir in data[HOME_PLANET]["Restaurant_to_LP"]:
                    moveDirection(dir)
                    sleep(1)
            else:
                logger.info("Current stamina is above minimum.")
                pass

            # Determine which planet to buy deficits[cycle] from
            while True:

                i = False  # find out if deficit is in planets.json or not
                ii = False  # do we still need this deficit item?

                for entry in data:
                    if HOME_PLANET not in entry:
                        if def_item in data[entry]["Sell"]:
                            if checkIfSelling(def_item, entry) == True:
                                remote_planet_id = entry
                                i = True
                                break
                            else:
                                logger.info(f"{entry} is below buying threshold of 7500 tons, moving on...")
                                pass
                        else:
                            logger.info(f"{entry} does not sell {def_item}, moving on...")

                if i is False:  # item wasn't in planets.json
                    logger.info(f"WARNING: Could not find {def_item} in planets.json.")
                    logger.info("Please account for all deficits for maximum efficiency.")
                    logger.info(f"Removing {def_item} from deficit list.")
                    deficits.pop(0)
                    try:
                        def_item = deficits[0]
                    except:
                        print(deficits[0])
                        print("Ran into an error")
                        exit(0)
                else:  # item was found and remote planet is selling it
                    if len(remote_planet_id) > 0:
                        def_item = deficits[0]
                        updateExchange()
                        sleep(1)
                        ii = checkCurrentCommodity(def_item)
                        if ii < DEFICIT:  # item is still needed
                            tn.write(b"say Deficit needed is " + str.encode(def_item) + b".\n")
                            logger.info(f"Will buy {def_item} from {remote_planet_id}...")
                            break
                        elif ii > DEFICIT:  # item is not needed anymore
                            logger.info(f"{def_item} appears to not be needed anymore, removing...")
                            deficits.pop(0)
                            def_item = deficits[0]
                            continue
                        else:
                            continue
                    else:
                        continue

            # Determine how many bays to buy of deficit[cycle]
            bays = deficitToBays(def_item)
            logger.info(f"Will buy {bays} bays of deficit from remote planet...")
            tn.write(b"say Will buy " + str.encode(str(bays)) + b" " + str.encode(def_item) + b".\n")

            # Board planet
            boardPlanet()
            sleep(1)

            # Move to ISL from home planet
            logger.info(f"Moving to ISL from {HOME_PLANET}...")
            for dir in data[HOME_PLANET]["Planet_to_ISL"]:
                moveDirection(dir)
                sleep(1)

            # Cartel/System jump logic
            # Local system logic
            if (data[HOME_PLANET]["System"] in data[remote_planet_id]["System"]) and (data[HOME_PLANET]["Cartel"] in data[remote_planet_id]["Cartel"]):
                pass
            # Local cartel logic
            elif (data[HOME_PLANET]["System"] not in data[remote_planet_id]["System"]) and (data[HOME_PLANET]["Cartel"] in data[remote_planet_id]["Cartel"]):
                logger.info("Jumping to remote system in same cartel...")
                jumpSystem(data[remote_planet_id]["System"])
                sleep(1)
            # Different cartel logic
            else:
                logger.info("Jumping to remote cartel...")
                jumpSystem(data[HOME_PLANET]["Cartel"])
                sleep(1)
                jumpSystem(data[remote_planet_id]["Cartel"])
                sleep(1)
                # Different cartel different system logic
                if data[remote_planet_id]["Cartel"] not in data[remote_planet_id]["System"]:
                    logger.info("Jumping to remote system...")
                    jumpSystem(data[remote_planet_id]["System"])
                    sleep(1)
                else:
                    pass

            # Move to remote planet from ISL
            logger.info(f"Moving to {remote_planet_id} from ISL...")
            for dir in data[remote_planet_id]["ISL_to_Planet"]:
                moveDirection(dir)
                sleep(1)

            # Board planet
            boardPlanet()
            sleep(1)

            # Move to exchange
            logger.info("Moving to exchange from landing pad...")
            for dir in data[remote_planet_id]["LP_to_Exchange"]:
                moveDirection(dir)
                sleep(1)

            # Buy deficits from remote exchange
            logger.info(f"Buying {def_item} from remote exchange...")
            for _ in range(bays):
                buyCommodity(def_item)
                sleep(1)
            sleep(1)

            # Move to landing pad
            logger.info("Moving to landing pad from exchange...")
            for dir in data[remote_planet_id]["Exchange_to_LP"]:
                moveDirection(dir)
                sleep(1)

            # Board planet
            boardPlanet()
            sleep(3)

            # Move to ISL from remote planet
            logger.info(f"Moving to ISL from {remote_planet_id}...")
            for dir in data[remote_planet_id]["Planet_to_ISL"]:
                moveDirection(dir)
                sleep(1)

            # Cartel/System jump logic
            # Local cartel logic
            if (data[HOME_PLANET]["System"] in data[remote_planet_id]["System"]) and (data[HOME_PLANET]["Cartel"] in data[remote_planet_id]["Cartel"]):
                pass
            # Local cartel logic
            elif (data[HOME_PLANET]["System"] not in data[remote_planet_id]["System"]) and (data[HOME_PLANET]["Cartel"] in data[remote_planet_id]["Cartel"]):
                logger.info("Jumping to remote system in same cartel...")
                jumpSystem(data[HOME_PLANET]["System"])
                sleep(1)
            # Different cartel logic
            else:
                logger.info("Jumping to home cartel...")
                jumpSystem(data[remote_planet_id]["Cartel"])
                sleep(1)
                jumpSystem(data[HOME_PLANET]["Cartel"])
                sleep(1)
                # Different cartel different system logic
                if data[HOME_PLANET]["Cartel"] not in data[HOME_PLANET]["System"]:
                    logger.info("Jumping to home system...")
                    jumpSystem(data[HOME_PLANET]["System"])
                    sleep(1)
                else:
                    pass

            # Move to home planet from ISL
            logger.info(f"Moving to {HOME_PLANET} from ISL...")
            for dir in data[HOME_PLANET]["ISL_to_Planet"]:
                moveDirection(dir)
                sleep(1)

            # Board planet
            boardPlanet()
            sleep(1)

            # Move to exchange
            logger.info("Moving to exchange from landing pad...")
            for dir in data[HOME_PLANET]["LP_to_Exchange"]:
                moveDirection(dir)
                sleep(1)

            # Sell item to home exchange
            logger.info(f"Selling {def_item} to home exchange...")
            for _ in range(bays):
                sellCommodity(def_item)
                sleep(1)
            sleep(1)

            # Move to landing pad
            logger.info("Moving to landing pad from exchange...")
            for dir in data[HOME_PLANET]["Exchange_to_LP"]:
                moveDirection(dir)
                sleep(1)

            # Iteration data updates to keep things fresh
            iter += 1

            prev_balance = balance  # how much we had before cycle began
            player()  # gather new player data
            sleep(1)
            diff_balance = (balance-prev_balance)  # how much we made this iteration

            ship()  # gather new ship data
            sleep(1)
            prev_treasury = treasury  # how much we had before cycle began

            planet()  # gather new planet data
            sleep(1)
            diff_treasury = (treasury-prev_treasury)  # how much we made this iteration

            remove("score.txt")  # remove files
            remove("ship.txt")  # remove files
            remove("planet.txt")  # remove files
            logger.info("Removing entry from deficits list...")
            tn.write(b"say Filled " + str.encode(def_item) + b".\n")
            deficits.pop(0)
            sleep(1)

            # end of iteration checks to ensure we are still able to move forward
            if current_planet not in HOME_PLANET:
                logger.info(f"Detected location is not {HOME_PLANET}.")
                logger.info("Something went wrong, closing script to ensure player safety.")
                exit(0)
            else:
                pass

            if (cargo_max - current_cargo) < 525:
                logger.info(f"Detected {current_cargo} extra tons in ship's hold.")
                logger.info("This is below the minimum tons required of 525 to function properly.")
                logger.info("Something went wrong, closing script to ensure we don't buy items unnecessarily.")
                exit(0)
            else:
                pass

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
                        sleep(60)
                    clearBuffer()  # clear buffer, who knows what happened in 30 mins
                    sleep(1)
                    exchange()  # run exchange functions
                    sleep(1)
                    continue

            # Surpluses loop specific vars
            sur_item = surpluses[0]

            # Buy fuel and food
            if current_fuel < fuel_min:
                buyFuel()
                logger.info("Current fuel is below minimum, buying fuel.")
                sleep(1)
            else:
                logger.info("Current fuel is above minimum.")
                pass
            if current_stamina < stamina_min:
                for dir in data[HOME_PLANET]["LP_to_Restaurant"]:
                    moveDirection(dir)
                    sleep(1)
                buyFood()
                logger.info("Current stamina is below minimum, buying food.")
                for dir in data[HOME_PLANET]["Restaurant_to_LP"]:
                    moveDirection(dir)
                    sleep(1)
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
                sleep(1)

            # Buy goods
            logger.info(f"Buying {sur_item} from home exchange...")
            buyCommodity(sur_item)
            sleep(1)

            # Move to landing pad
            logger.info("Moving to landing pad from exchange...")
            for dir in data[HOME_PLANET]["Exchange_to_LP"]:
                moveDirection(dir)
                sleep(1)

            # Board planet
            boardPlanet()
            sleep(1)

            # Move to ISL from home planet
            for dir in data[HOME_PLANET]["Planet_to_ISL"]:
                moveDirection(dir)
                sleep(1)

            # Cartel/System jump logic
            # Local system logic
            if (data[HOME_PLANET]["System"] in data[remote_planet_id]["System"]) and (data[HOME_PLANET]["Cartel"] in data[remote_planet_id]["Cartel"]):
                pass
            # Local cartel logic
            elif (data[HOME_PLANET]["System"] not in data[remote_planet_id]["System"]) and (data[HOME_PLANET]["Cartel"] in data[remote_planet_id]["Cartel"]):
                logger.info("Jumping to remote system in same cartel...")
                jumpSystem(data[remote_planet_id]["System"])
                sleep(1)
            # Different cartel logic
            else:
                logger.info("Jumping to remote cartel...")
                jumpSystem(data[HOME_PLANET]["Cartel"])
                sleep(1)
                jumpSystem(data[remote_planet_id]["Cartel"])
                sleep(1)
                # Different cartel different system logic
                if data[remote_planet_id]["Cartel"] not in data[remote_planet_id]["System"]:
                    logger.info("Jumping to remote system...")
                    jumpSystem(data[remote_planet_id]["System"])
                    sleep(1)
                else:
                    pass

            # Move to remote planet from ISL
            logger.info(f"Moving to {remote_planet_id} from ISL...")
            for dir in data[remote_planet_id]["ISL_to_Planet"]:
                moveDirection(dir)
                sleep(1)

            # Board planet
            boardPlanet()
            sleep(1)

            # Move to exchange
            logger.info("Moving to exchange from landing pad...")
            for dir in data[remote_planet_id]["LP_to_Exchange"]:
                moveDirection(dir)
                sleep(1)

            # Sell goods
            logger.info(f"Selling {sur_item} to remote exchange...")
            sellCommodity(sur_item)
            sleep(1)

            # Move to landing pad
            logger.info("Moving to landing pad from exchange...")
            for dir in data[remote_planet_id]["Exchange_to_LP"]:
                moveDirection(dir)
                sleep(1)

            # Board planet
            boardPlanet()
            sleep(3)

            # Move to ISL from remote planet
            logger.info(f"Moving to ISL from {remote_planet_id}...")
            for dir in data[remote_planet_id]["ISL_to_Planet"]:
                moveDirection(dir)
                sleep(1)

            # Cartel/System jump logic
            # Local cartel logic
            if (data[HOME_PLANET]["System"] in data[remote_planet_id]["System"]) and (data[HOME_PLANET]["Cartel"] in data[remote_planet_id]["Cartel"]):
                pass
            # Local cartel logic
            elif (data[HOME_PLANET]["System"] not in data[remote_planet_id]["System"]) and (data[HOME_PLANET]["Cartel"] in data[remote_planet_id]["Cartel"]):
                logger.info("Jumping to remote system in same cartel...")
                jumpSystem(data[HOME_PLANET]["System"])
                sleep(1)
            # Different cartel logic
            else:
                logger.info("Jumping to home cartel...")
                jumpSystem(data[remote_planet_id]["Cartel"])
                sleep(1)
                jumpSystem(data[HOME_PLANET]["Cartel"])
                sleep(1)
                # Different cartel different system logic
                if data[HOME_PLANET]["Cartel"] not in data[HOME_PLANET]["System"]:
                    logger.info("Jumping to home system...")
                    jumpSystem(data[HOME_PLANET]["System"])
                    sleep(1)
                else:
                    pass

            # Move to home planet from ISL
            logger.info(f"Moving to {HOME_PLANET} from ISL...")
            for dir in data[HOME_PLANET]["ISL_to_Planet"]:
                moveDirection(dir)
                sleep(1)

            # Board planet
            boardPlanet()
            sleep(1)

            # Iteration data updates to keep things fresh
            iter += 1

            prev_balance = balance  # how much we had before cycle began
            player()  # gather new player data
            sleep(1)
            diff_balance = (balance-prev_balance)  # how much we made this iteration

            ship()  # gather new ship data
            sleep(1)
            prev_treasury = treasury  # how much we had before cycle began

            planet()  # gather new planet data
            sleep(1)
            diff_treasury = (treasury-prev_treasury)  # how much we made this iteration

            remove("score.txt")  # remove files
            remove("ship.txt")  # remove files
            remove("planet.txt")  # remove files
            remove("price.txt")  # remove files
            tn.write(b"say Sold " + str.encode(sur_item) + b" to " + str.encode(remote_planet_id) + b".\n")

            # end of iteration checks to ensure we are still able to move forward
            if current_planet not in HOME_PLANET:
                logger.info(f"Detected location is not {HOME_PLANET}.")
                logger.info("Something went wrong, closing script to ensure player safety.")
                exit(0)
            else:
                pass

            if (cargo_max - current_cargo) < 525:
                logger.info(f"Detected {current_cargo} extra tons in ship's hold.")
                logger.info("This is below the minimum tons required of 525 to function properly.")
                logger.info("Something went wrong, closing script to ensure we don't buy items unnecessarily.")
                exit(0)
            else:
                pass

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
        exit(0)

if __name__ == "__main__":
    main()
