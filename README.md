Federation 2 automation scripts

1. Input your user, password, and home planet to federation2.py
2. Update the planets.json file with the planets you expect to trade with by
finding the best price for commodities and putting those in the "Sell" list.
Ensure that all movement paths, such as Exchange_to_LP and ISL_to_Planet are
updated accordingly or your PC will not move in the right directions.
3. Place your planet owner on your home planet landing pad before running.

Run the script with:

python3 federation2.py

version log:

1.0 "Deficit Dance" - Will continuously run through your exchange's deficits
and buy them from planets you set in planets.json.  Bugs should be expected.
