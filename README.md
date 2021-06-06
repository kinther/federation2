# Strahd's Federation 2 planet owner (rank Founder and above) deficit hauling script.  
### Send mail in game to Strahd if you have any questions.

1. Add your planet to planets.json with your home planet information, copying
Ravenloft variables.  For example if you owned the planet Rhea, you would
change "Ravenloft" to "Rhea" for the name field.  Another important entry
is "ISL_to_Planet", which for Rhea would be a single entry of ["se"], and
the reverse "Planet_to_ISL" which would be ["nw"].  Do the same for the
remaining entries under your new planet entry.
2. Find out which planets you want to buy from by checking their exchange
prices for commodities that are your deficits.  If you don't know your full
deficits list, check out http://www.f2ea.com which should help you identify
anything that is in the negative.  Once you have found a planet you want to buy
from for all of your deficits, enter them into the respective planet's entry
in planets.json in the "Sell" category.  For example if I wanted to buy
Alloys and BioChips from Castillo, I would create an entry for it and in the
Sell line enter ["Alloys", "BioChips"].
3. Find out which planets you want to sell your surpluses to by checking their
exchange information.  For optimal selling make sure to find at least six to
eight planets which will buy your surplus item.  Ensure none of these planets
are "mixed" planets that treat this item as a surplus of their own to maximize
profits - ideally they should only buy 525 tons or seven bays in total.
4. Place your planet owner on your home planet landing pad before running and
ensure you have a ship capable of carrying at least 525 tons.  (clear your
cargo space ahead of time wherever possible)

Run the script with:

python3 federation2.py --user (username) --password (password) --planet
(planet name) --mode (deficit or surplus)

or (depending on how you have your environment setup)

python federation2.py --user (username) --password (password) --planet
(planet name) --mode (deficit or surplus)

version log:

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

REQUIRES PYTHON3 TO RUN.  THIS WILL NOT RUN WITH PYTHON2.x.
