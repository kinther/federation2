#!/usr/bin/python3

# Federation 2 Community Edition hauling scripts for planet owners
# version 3.0 "Strictly Spices"

# Imports
from fed_utils import *  # used to pull in all custom functions from fed_utils.py
import fed_vars as v  # used to makes variables global across files

# Main function

def main():

    print("Starting up... please check logging file for more info...")
    # Perform initial setup and gather game data
    try:
        login()
        sleep(0.5)

    except Exception as e:
        logger.error("Ran into error during initial logon.  Please try again.")
        logger.exception(e)

    try:
        gatherData()
        sleep(0.5)

    except Exception as e:
        logger.error("Ran into error during initial gathering of data.  Please try again.")
        logger.exception(e)

    try:
        checkRank()
        sleep(0.5)

    except Exception as e:
        logger.error("Ran into error during check of character rank.  Please try again.")
        logger.exception(e)

    try:
        checkRemoteService()
        sleep(0.5)

    except Exception as e:
        logger.error("Ran into error during check of remote checking service.  Please try again.")
        logger.exception(e)

    # Check if character is sufficient rank to run script
    if v.character_rank not in ranks:
        logger.info("ERROR: This script is meant to be run by planet owners.")
        logger.info(f"Your current rank is detected as {v.character_rank}.")
        logger.info("Please re-run script when you rank up! Good luck :)")
        exit(0)
    else:
        pass

    # Check if planet_location = v.current_planet.  If not, exit script.
    if v.current_planet not in v.planet_location:
        logger.info("ERROR: Character must be on their home planet on the landing pad.")
        logger.info(f"Detected character on {v.planet_location} rather than {v.current_planet}.")
        logger.info("Exiting.")
        exit(0)
    else:
        pass

    # Check if cargo_max is less than 525 (can't haul a full 7 bays)
    if v.cargo_max < 525:
        i = str(v.cargo_max)
        logger.info("ERROR: Ship is not capable of hauling 525 tons of cargo right now.")
        logger.info(f"Detected {i} is the max tons we can haul.")
        logger.info("You may need to upgrade your ship in order to haul 525 tons.")
        logger.info("Exiting.")
        exit(0)
    else:
        pass

    # Check if current_cargo is less than 525 (can't haul a full 7 bays)
    if (v.cargo_max - v.current_cargo) < 525:
        i = str(v.current_cargo)
        logger.info("ERROR: Ship is not capable of hauling 525 tons of cargo right now.")
        logger.info(f"Detected {i} is the max tons we can haul.")
        logger.info("Please sell some things from the hold and re-start script.")
        logger.info("Exiting.")
        exit(0)
    else:
        pass


    # Check if current_cargo does not equal max cargo
    if v.current_cargo > 0:
        i = str(v.current_cargo)
        logger.info("WARNING: Ship is hauling some cargo already in its hold.")
        logger.info(f"Detected {i} tons in use.")
    else:
        pass    

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
            logger.info(f" We are currently filling deficits on {v.current_planet}.")
            logger.info(f" {args.user}'s bank balance is {v.balance}.")
            logger.info(f" That's a difference of {diff_balance} compared to last iteration.")
            logger.info(f" {v.current_planet}'s treasury value is {v.treasury}.")
            logger.info(f" That's a difference of {diff_treasury} compared to last iteration.")
            logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            # Pause for 30 minutes if deficits list is empty
            while True:

                if v.current_planet in v.planet_location:  # Are we on the planet we are starting loop on?
                    pass
                else:  # Found player is not on starting planet.

                    # Leave current planet and head to starting planet
                    boardPlanet()
                    sleep(0.5)

                    # Move to ISL from previous planet
                    logger.info(f"Moving to ISL from {v.planet_location}...")
                    for dir in data[v.planet_location]["Planet_to_ISL"]:
                        moveDirection(dir)
                        sleep(0.5)

                    # Move from ISL to starting planet
                    logger.info(f"Moving from ISL from {v.current_planet}...")
                    for dir in data[v.current_planet]["Planet_to_ISL"]:
                        moveDirection(dir)
                        sleep(0.5)          

                    # Land on starting planet
                    boardPlanet()
                    sleep(0.5)  

                    # Check if we made it to the starting planet successfully
                    checkLocation()
                    sleep(0.5)

                    if v.current_planet in v.planet_location:  # Did we make it there successfully?
                        pass
                    else:  # If not, exit script
                        logger.info("ERROR: Tried to move character to starting planet and ran into issue.")
                        logger.info("Please start your character on a landing pad of an owned planet.")
                        logger.info("Exiting.")
                        exit(0)

                if len(v.deficits) > 0:  # is deficits list of current planet empty yet?
                    break  # if more is to be done here, break and go back to filling deficits on current planet

                elif len(v.owned_planets) > 0:  # have we already filled deficits of all owned planets?

                    # Previous planet deficits are now filled and there are still planets remaining to be filled
                    logger.info("Deficits all filled.  Moving on to next planet.")
                    tn.write(b"say All deficits filled on current planet.  Moving on to next.\n")

                    # Board planet
                    boardPlanet()
                    sleep(0.5)

                    # Move to ISL from previous planet
                    logger.info(f"Moving to ISL from {v.current_planet}...")
                    for dir in data[v.current_planet]["Planet_to_ISL"]:
                        moveDirection(dir)
                        sleep(0.5)

                    # Change planet routine
                    v.current_planet = v.owned_planets[0]  # switch over to first planet in owned_planets list
                    v.owned_planets.pop(0)  # remove planet from list since we have switched over to it
                    logger.info(f"New planet to fill deficits on is {v.current_planet}...")

                    # Move from ISL to new planet
                    logger.info(f"Moving from ISL to {v.current_planet}...")
                    for dir in data[v.current_planet]["ISL_to_Planet"]:
                        moveDirection(dir)
                        sleep(0.5)

                    # Board planet
                    boardPlanet()
                    sleep(0.5)

                    # Check new planet's current treasury, deficits, surpluses
                    planet_data()  # update stored planetary information to reflect new planet
                    sleep(0.5)
                    exchange_data()  # update stored exchange data to reflect new planet
                    sleep(0.5)

                    break  # planet switch routine finalized, moving to main routine to fill deficits

                else:  # catch all if deficits have been filled entirely
                    logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.")
                    logger.info("Deficits all filled.  Restarting cycle after sleeping for 30 minutes.")
                    logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.")
                    tn.write(b"say All deficits filled.  Sleeping for 30 minutes and then restarting cycle.\n")
                    for i in range(30):  # Keepalive routine so BrokenPipe does not occur
                        tn.write(b"\n")
                        sleep(60)
                    checkPlanetOwner()
                    continue

            # Deficits loop specific vars
            def_item = v.deficits[0]

            # Buy fuel and food
            if v.current_fuel < v.fuel_min:
                buyFuel()
                logger.info("Current fuel is below minimum, buying fuel.")
                sleep(0.5)
            else:
                logger.info("Current fuel is above minimum.")
                pass
            if v.current_stamina < v.stamina_min:
                for dir in data[v.current_planet]["LP_to_Restaurant"]:
                    moveDirection(dir)
                    sleep(0.5)
                buyFood()
                logger.info("Current stamina is below minimum, buying food.")
                for dir in data[v.current_planet]["Restaurant_to_LP"]:
                    moveDirection(dir)
                    sleep(0.5)
            else:
                logger.info("Current stamina is above minimum.")
                pass

            # Determine which planet to buy deficits[cycle] from
            while True:

                i = False  # find out if deficit is in planets.json or not
                ii = False  # do we still need this deficit item?

                for entry in data:
                    if v.current_planet not in entry:
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
                    v.deficits.pop(0)
                    try:
                        def_item = v.deficits[0]
                    except:
                        print(v.deficits[0])
                        print("Ran into an error")
                        exit(0)
                else:  # item was found and remote planet is selling it
                    if len(remote_planet_id) > 0:
                        def_item = v.deficits[0]
                        updateExchange()
                        sleep(0.5)
                        ii = checkCurrentCommodity(def_item)
                        if ii < DEFICIT:  # item is still needed
                            tn.write(b"say Deficit needed is " + str.encode(def_item) + b".\n")
                            logger.info(f"Will buy {def_item} from {remote_planet_id}...")
                            break
                        elif ii > DEFICIT:  # item is not needed anymore
                            logger.info(f"{def_item} appears to not be needed anymore, removing...")
                            v.deficits.pop(0)
                            def_item = v.deficits[0]
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
            sleep(0.5)

            # Move to ISL from home planet
            logger.info(f"Moving to ISL from {v.current_planet}...")
            for dir in data[v.current_planet]["Planet_to_ISL"]:
                moveDirection(dir)
                sleep(0.5)

            # Cartel/System jump logic
            # Local system logic
            if (data[v.current_planet]["System"] in data[remote_planet_id]["System"]) and (data[v.current_planet]["Cartel"] in data[remote_planet_id]["Cartel"]):
                pass
            # Local cartel logic
            elif (data[v.current_planet]["System"] not in data[remote_planet_id]["System"]) and (data[v.current_planet]["Cartel"] in data[remote_planet_id]["Cartel"]):
                logger.info("Jumping to remote system in same cartel...")
                jumpSystem(data[remote_planet_id]["System"])
                sleep(0.5)
            # Different cartel logic
            else:
                logger.info("Jumping to remote cartel...")
                jumpSystem(data[v.current_planet]["Cartel"])
                sleep(0.5)
                jumpSystem(data[remote_planet_id]["Cartel"])
                sleep(0.5)
                # Different cartel different system logic
                if data[remote_planet_id]["Cartel"] not in data[remote_planet_id]["System"]:
                    logger.info("Jumping to remote system...")
                    jumpSystem(data[remote_planet_id]["System"])
                    sleep(0.5)
                else:
                    pass

            # Move to remote planet from ISL
            logger.info(f"Moving to {remote_planet_id} from ISL...")
            for dir in data[remote_planet_id]["ISL_to_Planet"]:
                moveDirection(dir)
                sleep(0.5)

            # Board planet
            boardPlanet()
            sleep(0.5)

            # Move to exchange
            logger.info("Moving to exchange from landing pad...")
            for dir in data[remote_planet_id]["LP_to_Exchange"]:
                moveDirection(dir)
                sleep(0.5)

            # Buy deficits from remote exchange
            logger.info(f"Buying {def_item} from remote exchange...")
            for _ in range(bays):
                buyCommodity(def_item)
                sleep(0.5)
            sleep(0.5)

            # Move to landing pad
            logger.info("Moving to landing pad from exchange...")
            for dir in data[remote_planet_id]["Exchange_to_LP"]:
                moveDirection(dir)
                sleep(0.5)

            # Board planet
            boardPlanet()
            sleep(3)

            # Move to ISL from remote planet
            logger.info(f"Moving to ISL from {remote_planet_id}...")
            for dir in data[remote_planet_id]["Planet_to_ISL"]:
                moveDirection(dir)
                sleep(0.5)

            # Cartel/System jump logic
            # Local cartel logic
            if (data[v.current_planet]["System"] in data[remote_planet_id]["System"]) and (data[v.current_planet]["Cartel"] in data[remote_planet_id]["Cartel"]):
                pass
            # Local cartel logic
            elif (data[v.current_planet]["System"] not in data[remote_planet_id]["System"]) and (data[v.current_planet]["Cartel"] in data[remote_planet_id]["Cartel"]):
                logger.info("Jumping to remote system in same cartel...")
                jumpSystem(data[v.current_planet]["System"])
                sleep(0.5)
            # Different cartel logic
            else:
                logger.info("Jumping to home cartel...")
                jumpSystem(data[remote_planet_id]["Cartel"])
                sleep(0.5)
                jumpSystem(data[v.current_planet]["Cartel"])
                sleep(0.5)
                # Different cartel different system logic
                if data[v.current_planet]["Cartel"] not in data[v.current_planet]["System"]:
                    logger.info("Jumping to home system...")
                    jumpSystem(data[v.current_planet]["System"])
                    sleep(0.5)
                else:
                    pass

            # Move to home planet from ISL
            logger.info(f"Moving to {v.current_planet} from ISL...")
            for dir in data[v.current_planet]["ISL_to_Planet"]:
                moveDirection(dir)
                sleep(0.5)

            # Board planet
            boardPlanet()
            sleep(0.5)

            # Move to exchange
            logger.info("Moving to exchange from landing pad...")
            for dir in data[v.current_planet]["LP_to_Exchange"]:
                moveDirection(dir)
                sleep(0.5)

            # Sell item to home exchange
            logger.info(f"Selling {def_item} to exchange...")
            for _ in range(bays):
                sellCommodity(def_item)
                sleep(0.5)
            sleep(0.5)

            # Move to landing pad
            logger.info("Moving to landing pad from exchange...")
            for dir in data[v.current_planet]["Exchange_to_LP"]:
                moveDirection(dir)
                sleep(0.5)

            # Iteration data updates to keep things fresh
            iter += 1

            prev_balance = v.balance  # how much we had before cycle began
            player_data()  # gather new player data
            sleep(0.5)
            diff_balance = (v.balance-prev_balance)  # how much we made this iteration

            ship_data()  # gather new ship data
            sleep(0.5)
            prev_treasury = v.treasury  # how much we had before cycle began

            planet_data()  # gather new planet data
            sleep(0.5)
            diff_treasury = (v.treasury-prev_treasury)  # how much we made this iteration

            logger.info("Removing entry from deficits list...")
            tn.write(b"say Filled " + str.encode(def_item) + b".\n")
            v.deficits.pop(0)
            sleep(0.5)

            # end of iteration checks to ensure we are still able to move forward
            if v.planet_location not in v.current_planet:
                logger.info(f"Detected location is not {v.current_planet}.")
                logger.info(f"Somehow we ended up on {v.planet_location}.")
                logger.info("Something went wrong, closing script to ensure player safety.")
                exit(0)
            else:
                pass

            if (v.cargo_max - v.current_cargo) < 525:
                logger.info(f"Detected {v.current_cargo} extra tons in ship's hold.")
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
            logger.info(f" We are currently selling surpluses from {v.current_planet}.")
            logger.info(f" {args.user}'s bank balance is {v.balance}.")
            logger.info(f" That's a difference of {diff_balance} compared to last iteration.")
            logger.info(f" {v.current_planet}'s treasury value is {v.treasury}.")
            logger.info(f" That's a difference of {diff_treasury} compared to last iteration.")
            logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            # Pause for 30 minutes if surpluses list is empty
            while True:
                if len(v.surpluses) > 0:  # is surpluses list empty yet?
                    break
                else:
                    logger.info("Surpluses all sold.  Sleeping for 30 minutes...")
                    tn.write(b"say All surpluses sold.  Sleeping for 30 minutes.\n")
                    for i in range(30):  # Keepalive function so BrokenPipe does not occur
                        tn.write(b"\n")
                        sleep(60)
                    clearBuffer()  # clear buffer, who knows what happened in 30 mins
                    sleep(0.5)
                    exchange_data()  # run exchange functions
                    sleep(0.5)
                    continue

            # Surpluses loop specific vars
            sur_item = v.surpluses[0]

            # Buy fuel and food
            if v.current_fuel < v.fuel_min:
                buyFuel()
                logger.info("Current fuel is below minimum, buying fuel.")
                sleep(0.5)
            else:
                logger.info("Current fuel is above minimum.")
                pass
            if v.current_stamina < v.stamina_min:
                for dir in data[v.current_planet]["LP_to_Restaurant"]:
                    moveDirection(dir)
                    sleep(0.5)
                buyFood()
                logger.info("Current stamina is below minimum, buying food.")
                for dir in data[v.current_planet]["Restaurant_to_LP"]:
                    moveDirection(dir)
                    sleep(0.5)
            else:
                logger.info("Current stamina is above minimum.")
                pass

            # Determine which planet to sell surpluses[cycle] from
            while True:

                i = False  # find out if surpluse is in planets.json or if not buying

                for entry in data:
                    if v.current_planet not in entry:
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
                    v.surpluses.pop(0)
                    sur_item = v.surpluses[0]
                else:
                    if len(remote_planet_id) > 0:
                        sur_item = v.surpluses[0]
                        tn.write(b"say " + str.encode(sur_item) + b" is still on the surpluses list.\n")
                        logger.info(f"Will sell one {sur_item} to {remote_planet_id}...")
                        break
                    else:
                        continue

            # Move to exchange
            logger.info("Moving to exchange from landing pad...")
            for dir in data[v.current_planet]["LP_to_Exchange"]:
                moveDirection(dir)
                sleep(0.5)

            # Buy goods
            logger.info(f"Buying {sur_item} from home exchange...")
            buyCommodity(sur_item)
            sleep(0.5)

            # Move to landing pad
            logger.info("Moving to landing pad from exchange...")
            for dir in data[v.current_planet]["Exchange_to_LP"]:
                moveDirection(dir)
                sleep(0.5)

            # Board planet
            boardPlanet()
            sleep(0.5)

            # Move to ISL from home planet
            for dir in data[v.current_planet]["Planet_to_ISL"]:
                moveDirection(dir)
                sleep(0.5)

            # Cartel/System jump logic
            # Local system logic
            if (data[v.current_planet]["System"] in data[remote_planet_id]["System"]) and (data[v.current_planet]["Cartel"] in data[remote_planet_id]["Cartel"]):
                pass
            # Local cartel logic
            elif (data[v.current_planet]["System"] not in data[remote_planet_id]["System"]) and (data[v.current_planet]["Cartel"] in data[remote_planet_id]["Cartel"]):
                logger.info("Jumping to remote system in same cartel...")
                jumpSystem(data[remote_planet_id]["System"])
                sleep(0.5)
            # Different cartel logic
            else:
                logger.info("Jumping to remote cartel...")
                jumpSystem(data[v.current_planet]["Cartel"])
                sleep(0.5)
                jumpSystem(data[remote_planet_id]["Cartel"])
                sleep(0.5)
                # Different cartel different system logic
                if data[remote_planet_id]["Cartel"] not in data[remote_planet_id]["System"]:
                    logger.info("Jumping to remote system...")
                    jumpSystem(data[remote_planet_id]["System"])
                    sleep(0.5)
                else:
                    pass

            # Move to remote planet from ISL
            logger.info(f"Moving to {remote_planet_id} from ISL...")
            for dir in data[remote_planet_id]["ISL_to_Planet"]:
                moveDirection(dir)
                sleep(0.5)

            # Board planet
            boardPlanet()
            sleep(0.5)

            # Move to exchange
            logger.info("Moving to exchange from landing pad...")
            for dir in data[remote_planet_id]["LP_to_Exchange"]:
                moveDirection(dir)
                sleep(0.5)

            # Sell goods
            logger.info(f"Selling {sur_item} to remote exchange...")
            sellCommodity(sur_item)
            sleep(0.5)

            # Move to landing pad
            logger.info("Moving to landing pad from exchange...")
            for dir in data[remote_planet_id]["Exchange_to_LP"]:
                moveDirection(dir)
                sleep(0.5)

            # Board planet
            boardPlanet()
            sleep(3)

            # Move to ISL from remote planet
            logger.info(f"Moving to ISL from {remote_planet_id}...")
            for dir in data[remote_planet_id]["ISL_to_Planet"]:
                moveDirection(dir)
                sleep(0.5)

            # Cartel/System jump logic
            # Local cartel logic
            if (data[v.current_planet]["System"] in data[remote_planet_id]["System"]) and (data[v.current_planet]["Cartel"] in data[remote_planet_id]["Cartel"]):
                pass
            # Local cartel logic
            elif (data[v.current_planet]["System"] not in data[remote_planet_id]["System"]) and (data[v.current_planet]["Cartel"] in data[remote_planet_id]["Cartel"]):
                logger.info("Jumping to remote system in same cartel...")
                jumpSystem(data[v.current_planet]["System"])
                sleep(0.5)
            # Different cartel logic
            else:
                logger.info("Jumping to home cartel...")
                jumpSystem(data[remote_planet_id]["Cartel"])
                sleep(0.5)
                jumpSystem(data[v.current_planet]["Cartel"])
                sleep(0.5)
                # Different cartel different system logic
                if data[v.current_planet]["Cartel"] not in data[v.current_planet]["System"]:
                    logger.info("Jumping to home system...")
                    jumpSystem(data[v.current_planet]["System"])
                    sleep(0.5)
                else:
                    pass

            # Move to home planet from ISL
            logger.info(f"Moving to {v.current_planet} from ISL...")
            for dir in data[v.current_planet]["ISL_to_Planet"]:
                moveDirection(dir)
                sleep(0.5)

            # Board planet
            boardPlanet()
            sleep(0.5)

            # Iteration data updates to keep things fresh
            iter += 1

            prev_balance = v.balance  # how much we had before cycle began
            player_data()  # gather new player data
            sleep(0.5)
            diff_balance = (v.balance-prev_balance)  # how much we made this iteration

            ship_data()  # gather new ship data
            sleep(0.5)
            prev_treasury = v.treasury  # how much we had before cycle began

            planet_data()  # gather new planet data
            sleep(0.5)
            diff_treasury = (v.treasury-prev_treasury)  # how much we made this iteration

            tn.write(b"say Sold " + str.encode(sur_item) + b" to " + str.encode(remote_planet_id) + b".\n")

            # end of iteration checks to ensure we are still able to move forward
            if v.planet_location not in v.current_planet:
                logger.info(f"Detected location is not {v.current_planet}.")
                logger.info("Something went wrong, closing script to ensure player safety.")
                exit(0)
            else:
                pass

            if (v.cargo_max - v.current_cargo) < 525:
                logger.info(f"Detected {v.current_cargo} extra tons in ship's hold.")
                logger.info("This is below the minimum tons required of 525 to function properly.")
                logger.info("Something went wrong, closing script to ensure we don't buy items unnecessarily.")
                exit(0)
            else:
                pass

            # check if we are below SURPLUS defined threshold
            if checkCommodityThreshold(sur_item, v.current_planet) == True:
                logger.info(f"{sur_item} is under SURPLUS defined threshold.  Removing from list.")
                v.surpluses.pop(0)
            else:
                logger.info(f"{sur_item} is above SURPLUS defined threshold.  Continuing.")

    else:

        # no mode selected or input was incorrect
        print("Mode must be either 'deficit' or 'surplus'.  Please re-run script.")
        logger.info("Mode must be either 'deficit' or 'surplus'.  Please re-run script.")
        exit(0)

if __name__ == "__main__":
    main()
