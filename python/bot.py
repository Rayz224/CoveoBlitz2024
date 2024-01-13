from game_message import *
from actions import *
import random
import math


class Bot:
    enemy_ship_scan_index = 0
    ship_utility = []           #helm, radar
    ship_shield_station = []    #shield
    ship_weapons = []           #turret
    ship_weapons_type = []

    turret_priority = [TurretType.EMP, TurretType.Cannon, TurretType.Sniper, TurretType.Fast, TurretType.Normal]
    EMP_occupied = False

    fixed_crewmates = []
    available_crewmates = []
    idle_crewmates = []

    first_run = True

    def __init__(self):
        print("Initializing your super mega duper bot")

    def get_to_station(self, crewmate, station_to_move_to):
        return CrewMoveAction(crewmate.id, station_to_move_to.stationPosition)

    def get_station(self, id, stations):
        for station in stations:
            if(station.id == id):
                return station
        return None

    def get_min_distance_turret_type(self, stationDistances, my_ship, occupiedStationIds):
        min_distance = float('inf')
        min_station = None

        for turret_type in self.turret_priority:
            print("yo")
            print(turret_type)
            for stationDistance in stationDistances:
                distance = stationDistance.distance
                print(self.get_station(stationDistance.stationId, my_ship.stations.turrets).turretType)
                if distance < min_distance and turret_type == self.get_station(stationDistance.stationId, my_ship.stations.turrets).turretType and occupiedStationIds.count(stationDistance.stationId) == 0:
                    if turret_type == TurretType.EMP and self.EMP_occupied == False:
                        min_station = stationDistance
                        self.EMP_occupied = True
                        return min_station
                    elif turret_type != TurretType.EMP:
                        min_station = stationDistance
                        return min_station
        return None

    def get_min_distance_station(self, stationDistances, occupiedStationIds):
        min_distance = float('inf')
        min_station = None

        for stationDistance in stationDistances:
            distance = stationDistance.distance
            if distance < min_distance and occupiedStationIds.count(stationDistance.stationId) == 0:
                min_distance = distance
                min_station = stationDistance

        return min_station

    def begin_allowing_crewmates(self, my_ship, actions):
        occupiedStationIds = []
        occupiedTurretCount = 0
        occupiedShieldCount = 0



        for crewmate in my_ship.crew:
            if occupiedTurretCount < 3:
                station_to_move_to = self.get_min_distance_turret_type(crewmate.distanceFromStations.turrets, my_ship, occupiedStationIds)
               # actions.append(self.get_to_station(crewmate, station_to_move_to))
                actions.append(self.get_crewmate_to_station(station_to_move_to,0,2))
                occupiedStationIds.append(station_to_move_to.stationId)
                occupiedTurretCount += 1
            elif occupiedShieldCount < 1:
                station_to_move_to = self.get_min_distance_station(crewmate.distanceFromStations.shields, occupiedStationIds)
                actions.append(self.get_crewmate_to_station(station_to_move_to, 0, 2))
                #actions.append(self.get_to_station(crewmate, station_to_move_to))
                occupiedStationIds.append(station_to_move_to.stationId)
                occupiedShieldCount += 1
            print(occupiedTurretCount)


    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """

        actions = []

        team_id = game_message.currentTeamId
        my_ship = game_message.ships.get(team_id)
        other_ships_ids = [shipId for shipId in game_message.shipsPositions.keys() if shipId != team_id]

        if self.first_run:
            self.get_ship_blueprint(my_ship)
            self.get_ship_weapons_type(my_ship)
            self.first_run = False

        # Find who's not doing anything and try to give them a job?
        self.idle_crewmates = [crewmate for crewmate in my_ship.crew if
                          crewmate.currentStation is None and crewmate.destination is None]


        if len(self.idle_crewmates) == len(my_ship.crew):
            self.begin_allowing_crewmates(my_ship, actions)



        # Now crew members at stations should do something!
        operatedTurretStations = [station for station in my_ship.stations.turrets if station.operator is not None]
        for turret_station in operatedTurretStations:
            if turret_station.turretType == "NORMAL":
                if turret_station.charge < 0:
                    pass
                else:
                    # Aim the turret
                    # actions.append(TurretLookAtAction(turret_station.id, self.get_debris_interception_point(self.get_debris_id(game_message), turret_station, game_message)))
                    actions.append(TurretLookAtAction(turret_station.id, game_message.shipsPositions[
                        other_ships_ids[self.enemy_ship_scan_index]]))
                    # Shoot!
                    actions.append(TurretShootAction(turret_station.id))

            elif turret_station.turretType == "EMP":

                if turret_station.charge < 0:
                    pass
                elif turret_station.charge == 0:
                    # Aim the turret
                    actions.append(TurretLookAtAction(turret_station.id, game_message.shipsPositions[
                        other_ships_ids[self.enemy_ship_scan_index]]))
                    # Charge the turret.
                    actions.append(TurretChargeAction(turret_station.id))
                elif 0 < turret_station.charge < 50:
                    # Charge the turret.
                    actions.append(TurretChargeAction(turret_station.id))
                else:
                    # Shoot!
                    actions.append(TurretShootAction(turret_station.id))
            elif turret_station.turretType == "FAST":

                if turret_station.charge < 0:
                    pass
                else:
                    # Shoot!
                    actions.append(TurretShootAction(turret_station.id))
            elif turret_station.turretType == "SNIPER":
                if turret_station.charge < 0:
                    pass
                elif turret_station.charge == 0:
                    # Aim the turret
                    actions.append(TurretLookAtAction(turret_station.id, game_message.shipsPositions[
                        other_ships_ids[self.enemy_ship_scan_index]]))
                    # Charge the turret.
                    actions.append(TurretChargeAction(turret_station.id))
                elif 0 < turret_station.charge < 75:
                    # Charge the turret.
                    actions.append(TurretChargeAction(turret_station.id))
                else:
                    # Shoot!
                    actions.append(TurretShootAction(turret_station.id))
            elif turret_station.turretType == "CANNON":
                if turret_station.charge < 0:
                    pass
                elif turret_station.charge == 0:
                    # Aim the turret
                    actions.append(TurretLookAtAction(turret_station.id, game_message.shipsPositions[
                        other_ships_ids[self.enemy_ship_scan_index]]))
                    # Charge the turret.
                    actions.append(TurretChargeAction(turret_station.id))
                elif 0 < turret_station.charge < 20:
                    # Charge the turret.
                    actions.append(TurretChargeAction(turret_station.id))
                else:
                    # Shoot!
                    actions.append(TurretShootAction(turret_station.id))

        # operatedHelmStation = [station for station in my_ship.stations.helms if station.operator is not None]
        # if operatedHelmStation:
        #     actions.append(ShipRotateAction(random.uniform(0, 360)))

        operatedRadarStation = [station for station in my_ship.stations.radars if station.operator is not None]
        for radar_station in operatedRadarStation:
            actions.append(RadarScanAction(radar_station.id, other_ships_ids[self.enemy_ship_scan_index]))

        # self.enemy_ship_scan_index += 1
        # if self.enemy_ship_scan_index >= len(other_ships_ids):
        #     self.enemy_ship_scan_index = 0
        return actions

# Logique de tir des débris
    def get_debris_id(self, game_message: GameMessage, my_ship):
        debris = [debris for debris in game_message.debris if debris.debrisType != DebrisType.Small]
        if len(debris) == 0:
            return None

        for debri in debris:
            for t in range(300):
                distance = ((debri.position.x + debri.velocity.x * t - my_ship.worldPosition.x) ** 2 + (debri.position.y + debri.velocity.y * t - my_ship.worldPosition.y) ** 2) ** 0.5

                if distance <= debri.radius + game_message.constants.ship.stations.shield.shieldRadius:
                    return debri

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

    def get_ship_blueprint(self, my_ship: Ship):
        self.ship_utility = my_ship.stations.helms
        self.ship_utility.append(my_ship.stations.radars)

        self.ship_shield_station = my_ship.stations.shields

        self.ship_weapons = my_ship.stations.turrets

    def get_ship_weapons_type(self, my_ship: Ship):
        types = []
        for weapon in my_ship.stations.turrets:
            types.append(weapon.turretType)

        self.ship_weapons_type = set(types)


    def do_we_have_that_weapon(self, turretType):
        return turretType in self.ship_weapons_type


    # def shield_critical(self, my_ship: Ship):
    #     return my_ship.currentShield <= 0
    #
    # # def shield_gestion(self, my_ship: Ship):
    # #     if self.shield_critical(my_ship):
    # #         self.get_to_station(self.)

    def get_to_station(self, crewmate, station_to_move_to):
        return CrewMoveAction(crewmate.id, station_to_move_to.stationPosition)


    def get_idle_crewmate(self):
        if self.idle_crewmates:
            return self.idle_crewmates.pop(0)
        else:
            return False

    def get_available_crewmate(self):
        idle_crewmate = self.get_idle_crewmate()
        if idle_crewmate:
            return idle_crewmate


        elif self.available_crewmates:
          return self.available_crewmates.pop(0)

        else:
            return False

    def get_fixed_crewmate(self):
        available_crewmate = self.get_available_crewmate()
        if available_crewmate:
            return available_crewmate

        else:
            return self.fixed_crewmates.pop(0)

    def get_crewmate_to_station(self, station, priority, station_priority):
        if priority == 0:
            crewmate = self.get_idle_crewmate()

            self.adjust_priority(crewmate, station_priority)
            return self.get_to_station(crewmate, station)

        elif priority == 1:

            crewmate = self.get_available_crewmate()

            self.adjust_priority(crewmate, station_priority)
            return self.get_to_station(crewmate, station)

        elif priority == 2:
            crewmate = self.get_fixed_crewmate()

            self.adjust_priority(crewmate, station_priority)
            return self.get_to_station(crewmate, station)

    #def send_crewmate_to_station(self,crewmate, station, station_priority):



    def adjust_priority(self, crewmate, station_priority):
        if station_priority == 0:
            self.idle_crewmates.append(crewmate)

        elif station_priority == 1:
            self.available_crewmates.append(crewmate)

        elif station_priority == 2:
            self.fixed_crewmates.append(crewmate)
