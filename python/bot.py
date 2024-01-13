from game_message import *
from actions import *
import random
import math


class Bot:
    enemy_ship_scan_index = 0
    ship_helms = []  # helm, radar
    ship_radars = []
    ship_shield_station = []  # shield
    ship_weapons = []  # turret
    ship_weapons_type = []
    radarInterval = 100

    turret_priority = [TurretType.Cannon, TurretType.EMP, TurretType.Normal, TurretType.Sniper, TurretType.Fast]
    EMP_occupied = False

    current_game_message = None
    current_my_ship = None

    fixed_crewmates = []
    available_crewmates = []
    idle_crewmates = []

    crewMateStations = {}

    angleLastTick = 999

    first_run = True
    crewmate_at_shield = False
    activated_radar_last_tick = False

    def __init__(self):
        print("Initializing your super mega duper bot")

    def focus_enemy(self):
        return self.get_crewmate_to_station(self.ship_helms[0], 2, 2)

    def go_back_to_work(self, crewmate, my_ship):
        print(self.crewMateStations)
        return CrewMoveAction(crewmate, self.crewMateStations.get(crewmate).gridPosition)

    def get_station(self, id):
        for station in self.current_my_ship.stations.turrets + self.current_my_ship.stations.turrets:
            if station.id == id:
                return station
        return None


    def get_to_station(self, crewmate, station):
        return CrewMoveAction(crewmate.id, station.gridPosition)

    def get_next_turret_to_assign(self, my_ship, occupiedStationIds, stations_no_crewmate):
        for turret_type in self.turret_priority:
            for station in my_ship.stations.turrets:
                if turret_type == station.turretType and occupiedStationIds.count(station.id) == 0 and stations_no_crewmate.count(station) == 0:
                    if turret_type == TurretType.EMP and self.EMP_occupied == False:
                        self.EMP_occupied = True
                        return station
                    elif turret_type != TurretType.EMP:
                        return station
        return None

    def begin_allowing_crewmates(self, my_ship, actions):
        occupiedStationIds = []
        occupiedTurretCount = 0
        occupiedShieldCount = 0
        stations_no_crewmate = []

        while self.idle_crewmates:
            if occupiedTurretCount < 4:
                station_to_move_to = self.get_next_turret_to_assign(my_ship, occupiedStationIds, stations_no_crewmate)
                print(station_to_move_to)
                # actions.append(self.get_to_station(crewmate, station_to_move_to))
                crewmate_move_action = self.get_crewmate_to_station(station_to_move_to, 0, 1)
                if crewmate_move_action is not None:
                    actions.append(crewmate_move_action)
                    occupiedStationIds.append(station_to_move_to.id)
                    occupiedTurretCount += 1
                else:
                    stations_no_crewmate.append(station_to_move_to)

    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """

        self.current_game_message = game_message
        actions = []

        team_id = game_message.currentTeamId
        my_ship = game_message.ships.get(team_id)
        self.current_my_ship = my_ship
        other_ships_ids = [shipId for shipId in game_message.shipsPositions.keys() if shipId != team_id]

        if self.first_run:
            self.get_ship_blueprint(my_ship)
            self.get_ship_weapons_type(my_ship)
            # Find who's not doing anything and try to give them a job?
            self.idle_crewmates = [crewmate for crewmate in my_ship.crew if
                                   crewmate.currentStation is None and crewmate.destination is None]
            self.begin_allowing_crewmates(my_ship, actions)
            self.first_run = False

        # Check radar if someone is available every x ticks
        if (game_message.currentTickNumber % self.radarInterval == 0):
            actions.append(self.get_crewmate_to_station(self.ship_radars[0], 2, 2))

        if self.shield_critical(my_ship) and not self.crewmate_at_shield:
            print(self.fixed_crewmates)
            print(self.available_crewmates)
            print(self.idle_crewmates)
            actions.append(self.get_crewmate_to_station(self.ship_shield_station[0], 2, 1))
            self.crewmate_at_shield = True
        #
        if my_ship.currentShield == 150 and self.crewmate_at_shield:
            actions.append

        operatedTurretStations = [station for station in my_ship.stations.turrets if station.operator is not None]
        for turret_station in operatedTurretStations:
            if turret_station.turretType == "NORMAL":
                if turret_station.charge < 0:
                    pass
                else:
                    # Aim the turret
                    actions.append(TurretLookAtAction(turret_station.id, self.get_debris_interception_point(
                        self.get_debris_id(game_message, my_ship), turret_station, game_message, other_ships_ids)))
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

        operatedRadarStation = [station for station in my_ship.stations.radars if station.operator is not None]
        isGoingBackToWork = False
        if(self.activated_radar_last_tick):
            for radar_station in operatedRadarStation:
                while game_message.ships[other_ships_ids[self.enemy_ship_scan_index][
                                         5: len(other_ships_ids[self.enemy_ship_scan_index]) - 2]].currentHealth <= 0:
                    self.enemy_ship_scan_index = self.enemy_ship_scan_index + 1 % len(game_message.other_ships_ids)
                self.focus_enemy()
                print("gobacktowork")
                actions.append(self.go_back_to_work(radar_station.operator, my_ship))
                self.activated_radar_last_tick = False
                isGoingBackToWork = True

        if(not isGoingBackToWork):
            for radar_station in operatedRadarStation:
                print("radar")
                actions.append(RadarScanAction(radar_station.id, other_ships_ids[self.enemy_ship_scan_index]))
                self.activated_radar_last_tick = True

        operatedHelmStation = [station for station in my_ship.stations.helms if station.operator is not None]
        for helm_station in operatedHelmStation:
            actions.append(ShipLookAtAction(helm_station.id,
                                            game_message.shipsPositions[other_ships_ids[self.enemy_ship_scan_index]]))
            if (self.angleLastTick == 999):
                self.angleLastTick = my_ship.orientationDegrees
            elif (self.angleLastTick != my_ship.orientationDegrees):
                self.angleLastTick = my_ship.orientationDegrees
            else:
                self.go_back_to_work(helm_station.operator, my_ship)
                self.angleLastTick = 999
        return actions

    # Logique de tir des débris
    def get_debris_id(self, game_message: GameMessage, my_ship):
        debris = [debris for debris in game_message.debris if debris.debrisType != DebrisType.Small]
        rockets = [rockets for rockets in game_message.rockets]
        if len(debris) == 0:
            return None

        # TODO: Besoin de 2 balles, donc faire attention
        for rocket in rockets:
            for t in range(300):
                distance = ((rocket.position.x + rocket.velocity.x * t - my_ship.worldPosition.x) ** 2 + (
                        rocket.position.y + rocket.velocity.y * t - my_ship.worldPosition.y) ** 2) ** 0.5

                if distance <= rocket.radius + game_message.constants.ship.stations.shield.shieldRadius:
                    return rocket

        for debri in debris:
            for t in range(300):
                distance = ((debri.position.x + debri.velocity.x * t - my_ship.worldPosition.x) ** 2 + (
                        debri.position.y + debri.velocity.y * t - my_ship.worldPosition.y) ** 2) ** 0.5

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

    def get_debris_interception_point(self, target: Debris, turret: TurretStation, game_message: GameMessage,
                                      other_ships_ids):
        if target is None:
            return game_message.shipsPositions[other_ships_ids[self.enemy_ship_scan_index]]

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
        self.ship_helms = my_ship.stations.helms
        self.ship_radars = my_ship.stations.radars

        self.ship_shield_station = my_ship.stations.shields

        self.ship_weapons = my_ship.stations.turrets

    def get_ship_weapons_type(self, my_ship: Ship):
        types = []
        for weapon in my_ship.stations.turrets:
            types.append(weapon.turretType)

        self.ship_weapons_type = set(types)

    def do_we_have_that_weapon(self, turretType):
        return turretType in self.ship_weapons_type

    def shield_critical(self, my_ship: Ship):
        return my_ship.currentShield <= 0

    def get_idle_crewmate(self, station):
        if self.idle_crewmates:
            for crewmate in self.idle_crewmates:
                if self.can_crewmate_go_to_station(crewmate, station):
                    self.idle_crewmates.remove(crewmate)
                    return crewmate
        print("No idle crewmate can go to that station")
        return False

    def get_available_crewmate(self, station):
        idle_crewmate = self.get_idle_crewmate(station)
        if idle_crewmate:
            return idle_crewmate
        elif self.available_crewmates:
            for crewmate in self.available_crewmates:
                if self.can_crewmate_go_to_station(crewmate, station):
                    self.available_crewmates.remove(crewmate)
                    return crewmate
            print("No available crewmate can go to that station")
            return False

    def get_fixed_crewmate(self, station):
        available_crewmate = self.get_available_crewmate(station)
        if available_crewmate:
            return available_crewmate

        elif self.fixed_crewmates:
            for crewmate in self.fixed_crewmates:
                if self.can_crewmate_go_to_station(crewmate, station):
                    self.fixed_crewmates.remove(crewmate)
                    return crewmate
        else:
            print("No fixed crewmate can go to that station")
            return False

    def can_crewmate_go_to_station(self, crewmate, station):
        for turret in crewmate.distanceFromStations.turrets:
            if turret.stationId == station.id and turret.distance < 50:
                return True
        for radar in crewmate.distanceFromStations.radars:
            if radar.stationId == station.id and radar.distance < 50:
                return True
        for shield in crewmate.distanceFromStations.shields:
            if shield.stationId == station.id and shield.distance < 50:
                return True
        for helm in crewmate.distanceFromStations.helms:
            if helm.stationId == station.id and helm.distance < 50:
                return True
        return False

    def get_crewmate_to_station(self, station, priority, station_priority):
        if priority == 0:
            crewmate = self.get_idle_crewmate(station)
            if not crewmate: return None
            self.adjust_priority(crewmate, station_priority)
            if self.first_run:
                self.crewMateStations[crewmate.id] = station
            return self.get_to_station(crewmate, station)
        elif priority == 1:
            crewmate = self.get_available_crewmate(station)
            if not crewmate: return None
            self.adjust_priority(crewmate, station_priority)
            if self.first_run:
                self.crewMateStations[crewmate.id] = station
            return self.get_to_station(crewmate, station)

        elif priority == 2:
            crewmate = self.get_fixed_crewmate(station)
            if not crewmate: return None
            self.adjust_priority(crewmate, station_priority)
            if self.first_run:
                self.crewMateStations[crewmate.id] = station
            return self.get_to_station(crewmate, station)

    def adjust_priority(self, crewmate, station_priority):
        if station_priority == 0:
            self.idle_crewmates.append(crewmate)

        elif station_priority == 1:
            self.available_crewmates.append(crewmate)

        elif station_priority == 2:
            self.fixed_crewmates.append(crewmate)
