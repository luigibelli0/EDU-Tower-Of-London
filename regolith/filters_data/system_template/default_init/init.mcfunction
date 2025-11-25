# The function that initializes basic scoreboards, fake players, gamerules etc.

# Commonly used scoreboards
# Temporary variables
scoreboard objectives add shapescape_tmp dummy
for <i 1..11 1>:
    scoreboard objectives add shapescape_tmp`eval:i` dummy

# The scoreboard for the fake players
scoreboard objectives add shapescape_var dummy

# The scoreboard for temporary variables stored in the fake players
scoreboard objectives add shapescape_tmp_var dummy

# The scoreboard for numbers
scoreboard objectives add shapescape_const dummy
for <i -1..11 1>:
    scoreboard players set _`eval:i` shapescape_const `eval:i`