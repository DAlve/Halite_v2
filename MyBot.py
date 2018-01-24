"""
Welcome to your first Halite-II bot!

This bot's name is Settler. It's purpose is simple (don't expect it to win complex games :) ):
1. Initialize game
2. If a ship is not docked and there are unowned planets
2.a. Try to Dock in the planet if close enough
2.b If not, go towards the planet

Note: Please do not place print statements here as they are used to communicate with the Halite engine. If you need
to log anything use the logging module.
"""
import hlt
import logging
from collections import OrderedDict

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("Dais_v4")

# Then we print our start message to the logs
logging.info("Starting my Settler bot!")

#planned_planets = []

while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []

    # For every ship that I control
    for ship in game_map.get_me().all_ships():
        
        shipid = ship.id
        # If the ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        # get entities near the ship and sort the dictionary by the distance from the ship
        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

        # create list of the closest empty planets
        closest_empty_planets = []

        # go through the list of closest entities and check if it is an planet that is un-occupied
        for distance in entities_by_distance:
            if (isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not
                    entities_by_distance[distance][0].is_owned()):
                closest_empty_planets.append(entities_by_distance[distance][0])

        # get a list of all my ships
        team_ships = game_map.get_me().all_ships()

        # get a list of all the closets enemy ships
        closest_enemy_ships = []
        for distance in entities_by_distance:
            if (isinstance(entities_by_distance[distance][0],hlt.entity.Ship) and
                    entities_by_distance[distance][0] not in team_ships):
                closest_enemy_ships.append(entities_by_distance[distance][0])

        # check to see if we have any empty planets
        if len(closest_empty_planets) > 0:
            # get the closest one
            target_planet = closest_empty_planets[0]

            # dock the ship if we can
            if ship.can_dock(target_planet):
                # We add the command by appending it to the command_queue
                command_queue.append(ship.dock(target_planet))
            # else start moving towards it
            else:
                navigate_command = ship.navigate(
                        ship.closest_point_to(target_planet),
                        game_map,
                        speed=int(hlt.constants.MAX_SPEED),
                        ignore_ships=True)
                
                if navigate_command:
                    command_queue.append(navigate_command)
        
        # if no planets find the closest enemy ship and 
        # move towards that
        elif len(closest_enemy_ships) > 0:
            target_ship = closest_enemy_ships[0]
            navigate_command = ship.navigate(
                        ship.closest_point_to(target_ship),
                        game_map,
                        speed=int(hlt.constants.MAX_SPEED),
                        ignore_ships=False)
            
            if navigate_command:
                command_queue.append(navigate_command)


    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
