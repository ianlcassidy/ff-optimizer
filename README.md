# ff-optimizer

This repo contains a quick and dirty fantasy football optimizer for weekly competitions found on DraftKings or FanDuel.

## Scraping data
I am scraping data from 3 sites:

1. [Roto Guru](http://rotoguru1.com/): provides weekly player salary information and historical FF points scored
2. [Football Locks](http://www.footballlocks.com/): provides weekly schedules, lines, and over/under
3. [Fantasy Pros](https://www.fantasypros.com/): provides weekly player points projections and a "start/sit grade"

Each site has its own quirks for actually getting the data into a usable form. I also tried creating a singular mapping
for teams and a primary key for merging the datasets together.

## Team Optimizer

The first step involves filtering the set of players. I chose to filter by position with minimum bounds on salary, "value,"
and "start/sit grade." Getting the number of "feasible" players down into 50s-60s helps with the optimization time since it
lowers the number of combinations.

The second step involves filtering down all the possible combinations to a set of "feasible" teams. I define a "feasible"
team by the following constraints/rules of thumb:
1. The total salary should equal $50k (i.e., don't leave money on the table);
2. The offensive players' teams should not be playing the defense;
3. No more than 2 players on the same team;
4. QB and RB _not_ on the same team;
5. QB and WR _on_ the same team; and
6. TE and WR _not_ on the same team.

The third step involves scoring each team. I use the following 4 metrics to score each team:
1. Total average historical points per game
2. Total expected team score based on O/U and lines
3. Total projected points
4. Average start/sit score (converting the grades to an academic 4.0 scale; i.e., A = 4.0, B = 3.0, etc.)

Using these scores, I sort the teams and create a "normalized" score based on the ordinal position of each team. I then 
take a weighted average of those scores and re-sort the entire list of teams.

## Running the code

Create a Python 3.8 virtual environment and run `pip install -r requirements.txt`.

Run the scraper: `python scraper.py`\
(note this will save the scraped data to a `/data` directory)

Run the optimizer: `python optimizer.py`\
(this could take a while depending on your computer)
