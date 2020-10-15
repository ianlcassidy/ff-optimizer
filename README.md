# ff-optimizer

This notebook contains a quick and dirty fantasy football optimizer for weekly competitions found on DraftKings or FanDuel.

A few notes:
- I wrote this because I had a hard time creating a team that satisfies some basic constraints/rules of thumb:
    + Should try to max out the $50k salary constraint
    + Should not have any offensive players playing your defense
    + Should try have a diverse team (e.g., no more than 2 players on the same time)
- I often get stuck after I pick my QB, top RB, top WR, and TE to fill in the rest of slots
- It's hard to find "good" weekly fantasy football data that contains both prior week's performance and projections/rankings against the upcoming component
- This approach mainly relies on historical performance
    + However, salary is somewhat correlated with projections, so :shrug:
- I did not do anything fancy - the approach relies on a grid search over the range of possibile teams (with certain filters in place) that satisfies a set of constraints (listed above)
