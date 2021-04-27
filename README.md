Strahd's Federation 2 planet owner (rank Founder and above) deficit hauling
script.  Send mail in game to Strahd if you have any questions.

1. Modify planets.json file with your home planet information, replacing
Ravenloft variables.  For example if you owned the planet Rhea, you would
replace "Ravenloft" with "Rhea" for the name field.  Another important entry
is "ISL_to_Planet", which for Rhea would be a single entry of ["se"], and
the reverse "Planet_to_ISL" which would be ["nw"].  Do the same for the
remaining entries under your planet.
2. Find out which planets you want to buy from by checking their exchange
prices for commodities that are your deficits.  If you don't know your full
deficits list, check out https://www.f2ea.com which should help you identify
anything that is in the negative.  Once you have found a planet you want to buy
from for all of your deficits, enter them into the respective planet's entry
in planets.json in the "Sell" category.  For example if I wanted to buy
Alloys and BioChips from Castillo, I would create an entry for it and in the
Sell line enter ["Alloys", "BioChips"].  (Make sure you account for all your
deficits here - this is important)
3. Place your planet owner on your home planet landing pad before running and
ensure you have a ship capable of carrying at least 525 tons.  (clear your
cargo space ahead of time wherever possible)

Run the script with:

python3 federation2.py --user (username) --password (password) --planet (planet you own)

version log:

1.0 "Deficit Dance" - Initial release.  Runs through deficit loop cycle.

1.1 "Anomalous Alloys" - bug fixes in deficit loop logic, minor enhancements
to print further data to logfile, conversion of user/password passing to
command line arguments rather than static entries in script, and some PEP8
updates.
