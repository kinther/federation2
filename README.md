# Federation 2 hauling script
## Reach out to Strahd or Kinther in game if you have any questions.

### Requirements
* Python3
* Windows/MacOS/Linux

### General advice for running the script
* Place your planet owner on your home planet landing pad before running!
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

### Version log

1.0 "Deficit Dance" - Initial release.  Runs through deficit loop cycle.

1.1 "Anomalous Alloys" - bug fixes in deficit loop logic, minor enhancements
to print further data to logfile, conversion of user/password passing to
command line arguments rather than static entries in script, and some PEP8
updates.

1.2 "BBQ BioChips" - cargo bay checks/notifications, script will now exit
if run by character below Founder rank, script will exit when character is not
on their home planet when started, home planet is now passed from command line,
deficits not accounted for in planets.json will be skipped, and fixed a
timestamp error on Windows preventing script from running.

1.3 "Bargain BioComponents" - fix exchange parsing issue caused by recent
update and improve script speed by decreasing time.sleep in most cases.

1.4 "Celestial Cereals" - support for multiple planets in your system

2.0 "Surplus Shuffle" - adds support for selling surpluses to remote planets
with the --mode parameter (allows either "deficit" or "surplus").  Defaults
to deficit if not specified.

2.1 "Clandestine Clays" - adds checks on whether a remote exchange is selling
a commodity and if that is above a certain threshold, improvements to the jump
system routine to reduce extra jumps, rank is checked only once instead of
every iteration, and improvements to logging.
