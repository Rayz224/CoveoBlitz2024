from game_message import *
from actions import *
import random

class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")

    def get_to_station(self, crewmate, station_to_move_to):
        return CrewMoveAction(crewmate.id, station_to_move_to.stationPosition)
    
    def get_min_distance_station(self, stations):
        min_distance = float('inf')
        min_station = None

        for station in stations:
            distance = station.distance
            if distance < min_distance:
                min_distance = distance
                min_station = station

        return min_station
    
    def begin_allowing_cremates(self, my_ship):
        actions = []
        for crewmate in my_ship.crew:
            visitable_stations = crewmate.distanceFromStations.shields + crewmate.distanceFromStations.turrets + crewmate.distanceFromStations.helms + crewmate.distanceFromStations.radars
            
            station_to_move_to = self.get_min_distance_station(crewmate.distanceFromStations.turrets)
            actions.append(self.get_to_station(crewmate, station_to_move_to))
        return actions


    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        actions = []

        team_id = game_message.currentTeamId
        my_ship = game_message.ships.get(team_id)
        other_ships_ids = [shipId for shipId in game_message.shipsPositions.keys() if shipId != team_id]

        # Find who's not doing anything and try to give them a job?
        idle_crewmates = [crewmate for crewmate in my_ship.crew if crewmate.currentStation is None and crewmate.destination is None]

        if len(idle_crewmates) == len(my_ship.crew):
            actions = self.begin_allowing_cremates(my_ship)

        """for crewmate in idle_crewmates:
            visitable_stations = crewmate.distanceFromStations.shields + crewmate.distanceFromStations.turrets + crewmate.distanceFromStations.helms + crewmate.distanceFromStations.radars
            
            
            station_to_move_to = random.choice(visitable_stations)
            actions.append(self.get_to_station(self, crewmate, station_to_move_to))

        # Now crew members at stations should do something!
        operatedTurretStations = [station for station in my_ship.stations.turrets if station.operator is not None]
        for turret_station in operatedTurretStations:
            possible_actions = [
                # Charge the turret.
                TurretChargeAction(turret_station.id),
                # Aim the turret itself.
                TurretLookAtAction(turret_station.id, 
                                   Vector(random.uniform(0, game_message.constants.world.width), random.uniform(0, game_message.constants.world.height))
                ),
                # Shoot!
                TurretShootAction(turret_station.id)
            ]

            actions.append(random.choice(possible_actions))

        operatedHelmStation = [station for station in my_ship.stations.helms if station.operator is not None]
        if operatedHelmStation:
            actions.append(ShipRotateAction(random.uniform(0, 360)))

        operatedRadarStation = [station for station in my_ship.stations.radars if station.operator is not None]
        for radar_station in operatedRadarStation:
            actions.append(RadarScanAction(radar_station.id, random.choice(other_ships_ids)))

        # You can clearly do better than the random actions above! Have fun!"""
        return actions
    

