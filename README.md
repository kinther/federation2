Federation 2 automation scripts

1. Input your home planet to federation2.py (line 36)
2. Update the planets.json file with the planets you expect to trade with by
finding the best price for commodities and putting those in the "Sell" list.
Ensure that all movement paths, such as Exchange_to_LP and ISL_to_Planet are
updated accordingly or your PC will not move in the right directions.
3. Place your planet owner on your home planet landing pad before running.

Run the script with:

python3 federation2.py --user (username) --password (password)

version log:

1.0 "Deficit Dance" - Initial release.  Runs through deficit loop cycle.

1.1 "Anomalous Alloys" - bug fixes in deficit loop logic, minor enhancements
to print further data to logfile, conversion of user/password passing to
command line arguments rather than static entries in script, and some PEP8
updates.
