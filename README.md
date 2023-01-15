# Federation 2 hauling script
## Reach out to Strahd or Kinther in game if you have any questions.

### Requirements
* Python3
* Windows/MacOS/Linux
* Your planet owner must have a remote price checking service (help remote)

### General advice for running the script
* Place your planet owner on the planet you pass to the --planet flag.  Make sure they
are on the landing pad.  Failing to do so will cause the script to exit.
* Make sure your ship can carry at least 525 tons (7 bays) of cargo.  Failing to have
this will cause the script to exit.
* Make sure your ship has nothing in its cargo hold prior to starting.  Failing to
have an empty hold will cause the script to exit.
* Quit the game before running! The script will "take over" as your character.
* If using Linux, install tmux or screen so that you can run the script in the
background.
* You -must- have a remote service subscription that is active.  You can buy
this for 30 days at a time on Earth.  The cost is one slithy tove.

### General advice for updating planets.json
* Copy/paste an existing planet into this file, then update the parameters to suit
your planet's needs.  Make sure the name, cartel, and system are accurate.
* If you have multiple planets in this file, each one must have a comma after its
entry.  The final entry in the file should -not- have a comma to indicate the end
of the file.
* Be absolutely certain about the movement patterns in planets.json.  If you enter
the wrong movement steps to/from a location, you player could end up in the wrong
room at the end of an iteration.  This will cause the script to exit to keep your
player safe (no one wants their player to die).
* The "Sell" field is what the planet is selling.  This is where you identify where
you want to buy commodities from the planet.
* The "Buy" field is what the planet is buying.  This is where you identify what
commodities you want to sell to the planet.
* The "ISL_to_Planet" is the movement steps required to reach the planet from the
interstellar link.
* The "Planet_to_ISL" is the movement steps required to reach the interstellar
link from the planet.
* Not all planets need to have restaurant movement steps.  Only your owned planets.

### General advice for the "Sell" field in planets.json file (aka deficits)
* Find out which planets you want to buy from by checking their exchange
prices for commodities that are your deficits.  If you don't know your full
deficits list, run a "di exchange" and look for anything that is -525 current.
* Check whether planets you are buying a commodity from have surpluses of 
greater than 7500.  If a planet you want to buy from drops below 7500 it will
be skipped so that prices do not climb and impact your profits.  To get around
this you can add the same commodity to multiple planets, which will give you "backups".
* Make sure you have at least three backups if you intend to run this script
all the time.  Exchanges can run out of commodities quickly, especially if you
have multiple planets to fill.

### General advice for the "Buy" field in planets.json file (aka surpluses)
* Check which planets you want to sell your surpluses to by checking their
exchange information.  A quick "check price commodity" will help you figure
out if they are buying.  If you're in a cartel you can also run the more
verbose "check price commodity cartel" to get a full list.
* For optimal selling make sure to find at least six to eight planets which will
buy your surplus commodity.  Ensure none of these planets are "mixed" planets
that treat this item as a surplus of their own.  This would be one that both
buys and sells the commodity, which means they have set their commodity max to
something higher than 0. **To maximize profits** - ideally each planet should
only buy 525 tons or seven bays in total.
* Cartels can impose an import tax on cargo brought into their cartel from
another.  Be careful entering cartels which have an import tax into your
planets.json file.
* It is considered polite to not "dump" commodities on other exchanges.  As
with most things in life, ask if it's ok ahead of time.

### Run the script with

python3 federation2.py --user (username) --password (password) --planet
(planet name) --mode (deficit or surplus)

or (depending on how you have your environment setup)

python federation2.py --user (username) --password (password) --planet
(planet name) --mode (deficit or surplus)
