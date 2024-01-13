from game_message import *
from actions import *
import random
import math


class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")

    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        actions = []

        team_id = game_message.currentTeamId
        my_ship = game_message.ships.get(team_id)
        other_ships_ids = [shipId for shipId in game_message.shipsPositions.keys() if shipId != team_id]

        # Find who's not doing anything and try to give them a job?
        idle_crewmates = [crewmate for crewmate in my_ship.crew if
                          crewmate.currentStation is None and crewmate.destination is None]

        for crewmate in idle_crewmates:
            visitable_stations = crewmate.distanceFromStations.shields + crewmate.distanceFromStations.turrets + crewmate.distanceFromStations.helms + crewmate.distanceFromStations.radars
            station_to_move_to = random.choice(visitable_stations)
            actions.append(CrewMoveAction(crewmate.id, station_to_move_to.stationPosition))

        # Now crew members at stations should do something!
        operatedTurretStations = [station for station in my_ship.stations.turrets if station.operator is not None]
        for turret_station in operatedTurretStations:
            possible_actions = [
                # Charge the turret.
                TurretChargeAction(turret_station.id),
                # Aim the turret itself.
                TurretLookAtAction(turret_station.id, self.get_interception_point(self.get_debris_id(game_message), turret_station, game_message)),
                # Shoot!
                TurretShootAction(turret_station.id)
            ]

            actions.append(random.choice(possible_actions))

        # operatedHelmStation = [station for station in my_ship.stations.helms if station.operator is not None]
        # if operatedHelmStation:
        #     actions.append(ShipRotateAction(random.uniform(0, 360)))

        operatedRadarStation = [station for station in my_ship.stations.radars if station.operator is not None]
        for radar_station in operatedRadarStation:
            actions.append(RadarScanAction(radar_station.id, random.choice(other_ships_ids)))

        # You can clearly do better than the random actions above! Have fun!
        return actions

    def get_debris_id(self, game_message: GameMessage):
        debris = [debris for debris in game_message.debris]
        return random.choice(debris)
    def smallestWhichIsntNegativeOrNan(self, numbers):
        smallest = math.inf
        for number in numbers:
            if not math.isnan(number) and 0 <= number < smallest:
                smallest = number
        if smallest == math.inf:
            return 0
        return smallest

    def get_interception_point(self, target: Debris, turret: TurretStation, game_message: GameMessage):
        P0 = target.position
        # P0 = Vector(meteor.position.x + meteor.velocity.x, meteor.position.y + meteor.velocity.y)
        V0 = target.velocity
        s0 = math.sqrt(abs(V0.x) + abs(V0.y))
        P1 = turret.worldPosition
        s1 = game_message.constants.ship.stations.turretInfos[turret.turretType].rocketSpeed

        interception_point = Vector(0, 0)

        # print(P0, V0, s0, P1, s1)
        a = (V0.x * V0.x) + (V0.y * V0.y) - (s1 * s1)
        b = 2 * ((P0.x * V0.x) + (P0.y * V0.y) -
                 (P1.x * V0.x) - (P1.y * V0.y))
        c = (P0.x * P0.x) + (P0.y * P0.y) + (P1.x * P1.x) + \
            (P1.y * P1.y) - (2 * P1.x * P0.x) - (2 * P1.y * P0.y)

        t1 = (-b + math.sqrt((b * b) - (4 * a * c))) / (2 * a)
        t2 = (-b - math.sqrt((b * b) - (4 * a * c))) / (2 * a)

        t = self.smallestWhichIsntNegativeOrNan([t1, t2])

        interception_point = Vector(P0.x + (t * V0.x), P0.y + (t * V0.y))

        return interception_point

    def get_to_station(self, crewmate, station_to_move_to):
        return CrewMoveAction(crewmate.id, station_to_move_to.stationPosition)
