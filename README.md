# Federation 2 hauling script
## Reach out to Strahd or Kinther in game if you have any questions.

### Requirements
* Python3
* Windows/MacOS/Linux
* Your planet owner must have a remote price checking service (help remote)

### General advice for running the script
* Place your planet owner on your home planet landing pad before running!
* Quit the game before running! The script will "take over" as your character.
* Ensure you have a ship capable of carrying at least 525 tons!
* Clear your cargo space ahead of time wherever possible!

### General advice for the "Sell" field in planets.json file (aka deficits)
* Add your planet to planets.json with your home planet information, copying
Ravenloft variables.  For example if you owned the planet Rhea, you would
change "Ravenloft" to "Rhea" for the name field.  Another important entry
is "ISL_to_Planet", which for Rhea would be a single entry of ["se"], and
the reverse "Planet_to_ISL" which would be ["nw"].  Do the same for the
remaining entries under your new planet entry.
* Make sure you add a comma after each new planet unless it is the last one
in planets.json.  Without this the file will not be read properly and the script
will fail!
* Find out which planets you want to buy from by checking their exchange
prices for commodities that are your deficits.  If you don't know your full
deficits list, run a "di exchange" and look for anything that is -525 current.
* Check whether planets you are buying a commodity from have surpluses of >
7500.  If a planet you want to buy from drops below 7500 it will be skipped so
that prices do not climb and impact your profits.  To get around this you can
add the same commodity to multiple planets, which will give you "backups".

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

### Run the script with

python3 federation2.py --user (username) --password (password) --planet
(planet name) --mode (deficit or surplus)

or (depending on how you have your environment setup)

python federation2.py --user (username) --password (password) --planet
(planet name) --mode (deficit or surplus)
