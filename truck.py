from datetime import time, datetime, timedelta
from typing import TYPE_CHECKING, Union

import routing
from package import Package

if TYPE_CHECKING:
    from hub import Hub


class Truck:
    def __init__(self, truck_id: int, package_capacity: int, speed: float, hub: 'Hub'):
        self.truck_id = truck_id
        self.priority_package_manifest: dict[str, list[Package]] = {}
        self.standard_package_manifest: dict[str, list[Package]] = {}
        self.packages_on_truck = set()
        self.priority_route = []
        self.standard_route = []
        self.package_capacity = package_capacity
        self.num_packages_loaded = 0
        self.is_at_hub = True
        self.is_ready_for_dispatch = False
        self.current_address = hub.get_hub_address()
        self.total_miles_traveled = 0.0
        self.hub = hub
        self.speed = speed
        self.route_start_time: Union[datetime, None] = None
        self.date_time: Union[datetime, None] = None
        self.priority_1_addresses = set()
        self.priority_address_list = set()
        self.travel_log = []

    def load_package(self, package: Package):
        if self.get_remaining_capacity() > 0:
            self.packages_on_truck.add(package)
            package.mark_package_loaded(self)
            self.num_packages_loaded = len(self.packages_on_truck)
        else:
            print('WARNING: truck reached capacity while loading package groups and routes may not be optimal.')

    def deliver_packages(self, address: str):
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

    def get_num_packages_loaded(self):
        return self.num_packages_loaded

    def get_remaining_capacity(self):
        return self.package_capacity - self.num_packages_loaded

    def get_packages(self) -> set[Package]:
        return self.packages_on_truck

    def set_priority_route(self, route: list[str]):
        self.priority_route = route

    def set_standard_route(self, route: list[str]):
        self.standard_route = route

    def set_ready_for_dispatch(self, value: bool):
        self.is_ready_for_dispatch = value

    def begin_route(self):
        route_distance = routing.calculate_route_distance(self.hub, (self.priority_route + self.standard_route))
        if route_distance == 0:
            self.is_ready_for_dispatch = False
            return
        self.is_at_hub = False
        self.is_ready_for_dispatch = False
        self.travel_log.append(f'Left the hub at {self.get_time()}')
        for package in self.packages_on_truck:
            package.mark_package_out_for_delivery(self)
        for address in self.priority_route:
            starting_address = self.current_address
            miles_traveled = self.hub.addresses.distance_between(self.current_address, address)
            self.total_miles_traveled += miles_traveled
            time_traveling = (miles_traveled / self.speed)
            self.add_time(time_traveling)
            self.current_address = address
            self.deliver_packages(address)
            if miles_traveled > 0:
                self.travel_log.append(f'Navigated from {starting_address} to {address} ({miles_traveled:.1f} miles).')
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
        self.travel_log.append(f'Traveled a total distance of {route_distance:.1f} on this route.\n')

    def return_to_hub(self):
        hub_address = self.hub.get_hub_address()
        if self.current_address != hub_address:
            self.total_miles_traveled += self.hub.addresses.distance_between(self.current_address, hub_address)
            self.current_address = hub_address
        self.priority_route.clear()
        self.standard_route.clear()
        self.priority_1_addresses.clear()
        self.is_at_hub = True
        self.is_ready_for_dispatch = False
        self.travel_log.append(f'Returned to the hub at {self.get_time()}')

    def set_route_start_time(self, hour: int, minute: int):
        date = datetime.today()
        start_time = time(hour, minute)
        self.route_start_time = datetime.combine(date, start_time)
        if not self.date_time:
            self.date_time = self.route_start_time

    def set_current_time(self, current_time: time):
        date = datetime.today()
        self.date_time = datetime.combine(date, current_time)

    def add_time(self, hours: float):
        time_delta = timedelta(hours=hours)
        self.date_time += time_delta

    def get_time(self):
        if self.date_time:
            return self.date_time.time()

    def get_truck_id(self):
        return self.truck_id

    def get_miles_traveled(self):
        return self.total_miles_traveled

    def get_route_start_time(self):
        return self.route_start_time.time()

    def add_priority_address(self, address: str):
        self.priority_address_list.add(address)

    def get_priority_address_list(self) -> set[str]:
        return self.priority_address_list

    def set_priority_manifest(self, manifest: dict[str, set[Package]]):
        self.priority_package_manifest = manifest

    def set_standard_manifest(self, manifest: dict[str, set[Package]]):
        self.standard_package_manifest = manifest


class TruckCollection:
    def __init__(self):
        self.all_trucks: list[Truck] = []

    def add_truck(self, truck: Truck):
        self.all_trucks.append(truck)
