"""A module for managing trucks.

This module contains the Truck and TruckCollection classes, which are used for representing trucks and associating
a group of trucks with their delivery hub.
"""

import datetime
from typing import TYPE_CHECKING, Union

import routing

if TYPE_CHECKING:
    from datetime import time, datetime
    from hub import Hub
    from package import Package


class Truck:
    """Represents a truck and is used to perform operations related to delivery of packages.

    Attributes:
        truck_id: A unique identifier for a truck.
        priority_package_manifest: A dictionary containing addresses that have priority packages assigned to them
          as well as all packages associated with these addresses.
        standard_package_manifest: A dictionary containing addresses that have only standard packages assigned to them
          as well as all packages associated with these addresses.
        packages_on_truck: All packages currently loaded on the truck.
        priority_route: A list of priority addresses in order of the route.
        standard_route: A list of standard addresses in order of the route.
        package_capacity: The maximum number of packages a truck is capable of holding.
        num_packages_loaded: The number of packages currently loaded on a truck.
        is_at_hub: Indicates whether a truck is currently at the hub or not.
        is_ready_for_dispatch: Indicates whether a truck is currently reading for dispatch or not.
        current_address: The address a truck is currently at.
        total_miles_traveled: The total number of miles a truck has traveled throughout the day.
        hub: The delivery hub a truck is associated with.
        speed: The average speed of a truck, including loading time and delivery time.
        route_start_time: The time a truck is dispatched on its first route of the day.
        date_time: The current time of a truck.
        priority_1_addresses: The addresses of any priority 1 packages loaded on a truck.
        all_priority_addresses: The addresses of all priority packages loaded on a truck.
        travel_log: A log of the truck's activities throughout the day.
    """

    def __init__(self, truck_id: int, package_capacity: int, speed: float, hub: 'Hub'):
        """Initializes Truck.

        Args:
            truck_id: A unique identifier for the truck.
            package_capacity: The maximum number of packages the truck is capable of holding.
            speed: The average speed of the truck, including loading time and delivery time.
            hub: The delivery hub the truck is associated with.
        """

        self.truck_id = truck_id
        self.priority_package_manifest: dict[str, set['Package']] = {}
        self.standard_package_manifest: dict[str, set['Package']] = {}
        self.packages_on_truck: set[Package] = set()
        self.priority_route: list[str] = []
        self.standard_route: list[str] = []
        self.package_capacity = package_capacity
        self.num_packages_loaded = 0
        self.is_at_hub = True
        self.is_ready_for_dispatch = False
        self.current_address = hub.addresses.hub_address
        self.total_miles_traveled = 0.0
        self.hub = hub
        self.speed = speed
        self.route_start_time: Union[datetime, None] = None
        self.date_time: Union[datetime, None] = None
        self.priority_1_addresses: set[str] = set()
        self.all_priority_addresses: set[str] = set()
        self.travel_log: list[str] = []

    @property
    def remaining_capacity(self):
        """Calculates the remaining number of packages that can be loaded on a truck before it is full.

        Returns: The number of packages left before the truck reaches capacity.
        """

        return self.package_capacity - self.num_packages_loaded

    @property
    def current_time(self):
        """The current time of the truck.

        Returns: The time component of the truck's date_time attribute if it is set, none otherwise.
        """

        if self.date_time:
            return self.date_time.time()

    def load_package(self, package: 'Package'):
        """Loads a package on the truck.

        Args:
            package: The package to be loaded.
        """

        if self.remaining_capacity > 0:
            self.packages_on_truck.add(package)
            package.mark_package_loaded(self)
            self.num_packages_loaded = len(self.packages_on_truck)
        else:
            print('WARNING: truck reached capacity while loading package groups and routes may not be optimal.')

    def deliver_packages(self, address: str):
        """Delivers all packages for the truck's current address.

        Args:
            address: The address to deliver packages to.

        Time complexity: O(n), where n is the number of packages assigned to the address.
        """

        if address in self.priority_package_manifest:
            for package in self.priority_package_manifest.get(address):
                if package.ready_for_delivery:
                    package.mark_package_delivered(self)
                    self.packages_on_truck.remove(package)
                    self.num_packages_loaded -= 1
            del self.priority_package_manifest[address]
        elif address in self.standard_package_manifest:
            for package in self.standard_package_manifest.get(address):
                if package.ready_for_delivery:
                    package.mark_package_delivered(self)
                    self.packages_on_truck.remove(package)
                    self.num_packages_loaded -= 1
            del self.standard_package_manifest[address]

    def begin_route(self):
        """Dispatches the truck to visit each address on its route and deliver all packages on the truck.

        Time complexity: O(n), where n is the number of packages on the truck.
        """

        route_distance = routing.calculate_route_distance(self.hub, (self.priority_route + self.standard_route))
        # Because the route starts with the hub's address, a truck with no packages will still have a route. If this
        # is the case, reset the ready_for_dispatch flag and do nothing.
        if route_distance == 0:
            self.is_ready_for_dispatch = False
            return

        self.is_at_hub = False
        self.is_ready_for_dispatch = False

        self.travel_log.append(f'Left the hub at {self.current_time}')

        # Mark packages out for delivery
        for package in self.packages_on_truck:
            package.mark_package_out_for_delivery(self)

        # Visit each address on the priority route and deliver all packages to each address.
        for address in self.priority_route:
            starting_address = self.current_address
            miles_traveled = self.hub.addresses.distance_between(self.current_address, address)
            self.total_miles_traveled += miles_traveled
            time_traveling = (miles_traveled / self.speed)
            self.add_time(time_traveling)
            self.current_address = address
            self.deliver_packages(address)
            # As mentioned above, because the starting address is the hub, the first "stop" in the route will
            # have a travel distance of 0 and should be excluded from the log.
            if miles_traveled > 0:
                self.travel_log.append(f'Navigated from {starting_address} to {address} ({miles_traveled:.1f} miles).')

        # Visit each address on the standard route and deliver all packages to each address.
        for address in self.standard_route:
            starting_address = self.current_address
            miles_traveled = self.hub.addresses.distance_between(self.current_address, address)
            self.total_miles_traveled += miles_traveled
            time_traveling = (miles_traveled / self.speed)
            self.add_time(time_traveling)
            self.current_address = address
            self.deliver_packages(address)
            if miles_traveled > 0:
                self.travel_log.append(f'Navigated from {starting_address} to {address} ({miles_traveled:.1f} miles).')

        self.return_to_hub()
        self.travel_log.append(f'Traveled a total distance of {route_distance:.1f} miles on this route.\n')

    def return_to_hub(self):
        """Calls the truck back to the hub, clears the routes, and logs the time."""

        hub_address = self.hub.addresses.hub_address
        if self.current_address != hub_address:
            self.total_miles_traveled += self.hub.addresses.distance_between(self.current_address, hub_address)
            self.current_address = hub_address
        self.priority_route.clear()
        self.standard_route.clear()
        self.priority_1_addresses.clear()
        self.is_at_hub = True
        self.is_ready_for_dispatch = False
        self.travel_log.append(f'Returned to the hub at {self.current_time}')

    def set_route_start_time(self, hour: int, minute: int):
        """Sets the time that the truck is dispatched on its first route.

        Args:
            hour: The hour of the day.
            minute: The minute of the day.
        """

        date = datetime.datetime.today()
        start_time = datetime.time(hour, minute)
        self.route_start_time = datetime.datetime.combine(date, start_time)
        if not self.date_time:
            self.date_time = self.route_start_time

    def set_current_time(self, current_time: 'time'):
        """Sets the current time of the truck.

        Args:
            current_time: The current time of the truck.
        """

        date = datetime.today()
        self.date_time = datetime.datetime.combine(date, current_time)

    def add_time(self, hours: float):
        """Adds travel time to the truck's current time.

        Args:
            hours: The number of hours the truck spent traveling.
        """

        time_delta = datetime.timedelta(hours=hours)
        self.date_time += time_delta


class TruckCollection:
    """Represents a collection of trucks that is assigned to a hub.

    Attributes:
        all_trucks: All the trucks assigned to the hub.
    """

    def __init__(self):
        """Initiates TruckCollection."""

        self.all_trucks: list[Truck] = []

    def add_truck(self, truck: Truck):
        """Adds a truck to the collection.

        Args:
            truck: The truck to be added.
        """

        self.all_trucks.append(truck)
