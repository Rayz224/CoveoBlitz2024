from game_message import *
from actions import *
import random
import math


class Bot:
    enemy_ship_scan_index = 0
    def __init__(self):
        print("Initializing your super mega duper bot")

<<<<<<< HEAD
    def get_to_station(self, crewmate, station_to_move_to):
        return CrewMoveAction(crewmate.id, station_to_move_to.stationPosition)
    
    def get_station(self, id, stations):
        for station in stations:
            if(station.id == id):
                return station
        raise Exception("ds")
        return None
    
    def get_min_distance_turret_type(self, stationDistances, my_ship, turret_types):
        min_distance = float('inf')
        min_station = None

        for stationDistance in stationDistances:
            distance = stationDistance.distance
            print(self.get_station(stationDistance.stationId, my_ship.stations.turrets).turretType)
            if distance < min_distance and (turret_types.count(self.get_station(stationDistance.stationId, my_ship.stations.turrets).turretType) >= 1):
                min_distance = distance
                min_station = stationDistance
        return min_station
    
    def get_min_distance_station(self, stations):
        min_distance = float('inf')
        min_station = None

        for station in stations:
            distance = station.distance
            if distance < min_distance:
                min_distance = distance
                min_station = station

        return min_station
    
    def begin_allowing_cremates(self, my_ship, actions):
        occupiedTurretCount = 0
        occupiedShieldCount = 0
        for crewmate in my_ship.crew:
            if occupiedTurretCount < 2:
                station_to_move_to = self.get_min_distance_turret_type(crewmate.distanceFromStations.turrets, my_ship, [TurretType.Normal, TurretType.EMP])
                actions.append(self.get_to_station(crewmate, station_to_move_to))
                occupiedTurretCount += 1
            elif occupiedShieldCount < 2:
                station_to_move_to = self.get_min_distance_station(crewmate.distanceFromStations.shields)
                actions.append(self.get_to_station(crewmate, station_to_move_to))
                occupiedShieldCount += 1

=======
>>>>>>> 12acb5c01c6a2d9f0760f02f03b793311537ac21

    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        actions = []

        team_id = game_message.currentTeamId
        my_ship = game_message.ships.get(team_id)
        other_ships_ids = [shipId for shipId in game_message.shipsPositions.keys() if shipId != team_id]
        # print(other_ships_ids)
        # print(game_message.shipsPositions[other_ships_ids[self.enemy_ship_scan_index]])

        # Find who's not doing anything and try to give them a job?
        idle_crewmates = [crewmate for crewmate in my_ship.crew if
                          crewmate.currentStation is None and crewmate.destination is None]

        if len(idle_crewmates) == len(my_ship.crew):
            self.begin_allowing_cremates(my_ship, actions)

        # Now crew members at stations should do something!
        operatedTurretStations = [station for station in my_ship.stations.turrets if station.operator is not None]
        for turret_station in operatedTurretStations:
            if turret_station.turretType == "NORMAL":
                # Charge the turret.
                actions.append(TurretChargeAction(turret_station.id))
                # Aim the turret itself.
                actions.append(TurretLookAtAction(turret_station.id,self.get_debris_interception_point(self.get_debris_id(game_message),turret_station, game_message)))
                # Shoot!
                actions.append(TurretShootAction(turret_station.id))
            elif turret_station.turretType == "EMP":

                # Charge the turret.
                actions.append(TurretChargeAction(turret_station.id))
                    # Aim the turret itself.
                actions.append(TurretLookAtAction(turret_station.id, game_message.shipsPositions[other_ships_ids[self.enemy_ship_scan_index]]))
                    # Shoot!
                actions.append(TurretShootAction(turret_station.id))


        # operatedHelmStation = [station for station in my_ship.stations.helms if station.operator is not None]
        # if operatedHelmStation:
        #     actions.append(ShipRotateAction(random.uniform(0, 360)))

        operatedRadarStation = [station for station in my_ship.stations.radars if station.operator is not None]
        for radar_station in operatedRadarStation:
            actions.append(RadarScanAction(radar_station.id, other_ships_ids[self.enemy_ship_scan_index]))

        self.enemy_ship_scan_index += 1
        if self.enemy_ship_scan_index >= len(other_ships_ids):
            self.enemy_ship_scan_index = 0
        return actions

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

    def begin_allowing_cremates(self, my_ship, actions):
        for crewmate in my_ship.crew:
            visitable_stations = crewmate.distanceFromStations.shields + crewmate.distanceFromStations.turrets + crewmate.distanceFromStations.helms + crewmate.distanceFromStations.radars

            station_to_move_to = self.get_min_distance_station(crewmate.distanceFromStations.turrets)
            actions.append(self.get_to_station(crewmate, station_to_move_to))

    def get_debris_id(self, game_message: GameMessage):
        debris = [debris for debris in game_message.debris]
        if len(debris) == 0:
            return None
        return random.choice(debris)

    def smallestWhichIsntNegativeOrNan(self, numbers):
        smallest = math.inf
        for number in numbers:
            if not math.isnan(number) and 0 <= number < smallest:
                smallest = number
        if smallest == math.inf:
            return 0
        return smallest

    def get_debris_interception_point(self, target: Debris, turret: TurretStation, game_message: GameMessage):
        if target is None:
            return Vector(0, 0)
        P0 = target.position
        # P0 = Vector(meteor.position.x + meteor.velocity.x, meteor.position.y + meteor.velocity.y)
        V0 = target.velocity
        s0 = math.sqrt(abs(V0.x) + abs(V0.y))
        P1 = turret.worldPosition
        s1 = game_message.constants.ship.stations.turretInfos[turret.turretType].rocketSpeed

        return self.get_interception_point(P0, V0, s0, P1, s1)

    def get_interception_point(self, p0, v0, s0, p1, s1):
        a = (v0.x * v0.x) + (v0.y * v0.y) - (s1 * s1)
        b = 2 * ((p0.x * v0.x) + (p0.y * v0.y) -
                 (p1.x * v0.x) - (p1.y * v0.y))
        c = (p0.x * p0.x) + (p0.y * p0.y) + (p1.x * p1.x) + \
            (p1.y * p1.y) - (2 * p1.x * p0.x) - (2 * p1.y * p0.y)

        t1 = (-b + math.sqrt((b * b) - (4 * a * c))) / (2 * a)
        t2 = (-b - math.sqrt((b * b) - (4 * a * c))) / (2 * a)

        t = self.smallestWhichIsntNegativeOrNan([t1, t2])

        interception_point = Vector(p0.x + (t * v0.x), p0.y + (t * v0.y))

        return interception_point

    def get_to_station(self, crewmate, station_to_move_to):
        return CrewMoveAction(crewmate.id, station_to_move_to.stationPosition)
