from datetime import time

import helper
import routing
from address import AddressCollection
from dev import tests
from package import PackageCollection, Package
from truck import TruckCollection, Truck


class Hub:
    def __init__(self, package_file: str, address_file: str, distance_file: str, num_trucks: int,
                 package_capacity_per_truck: int, truck_speed: float, route_start_time: time):
        self.packages = PackageCollection()
        self.packages.import_packages(package_file)
        self.addresses = AddressCollection()
        self.addresses.import_addresses(address_file)
        self.addresses.import_distances(distance_file)
        self.trucks = TruckCollection()
        self.packages_ready_for_dispatch: list[Package] = []
        self.hub_address = self.addresses.get_hub_address()
        for i in range(num_trucks):
            truck = Truck((i + 1), package_capacity_per_truck, truck_speed, self)
            self.trucks.add_truck(truck)
        self.route_start_time = route_start_time
        self.time_tracking = helper.TimeTracking(route_start_time)

    def check_in_package(self, package_id: int, status_override: int = None):
        package = self.packages.package_table.search(package_id)
        if status_override:
            package.set_package_status(status_override)
        elif self.addresses.address_is_valid(package.get_address()):
            package.set_package_status(1)
            self.packages_ready_for_dispatch.append(package)
        else:
            package.set_package_status(4)

    def load_trucks(self):
        priority_list = routing.calculate_priority_list(self.packages_ready_for_dispatch)
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.is_ready_for_dispatch and truck.get_remaining_capacity() > 0:
                for address in priority_list:
                    skip_address = False
                    if len(priority_list.get(address)) < truck.get_remaining_capacity():
                        for package in priority_list.get(address):
                            if self.time_tracking.get_time().time() <= self.route_start_time and truck.truck_id == 1 \
                                    and package.package_id in self.packages.delivery_binding:  # don't load packages
                                # bound together on first truck of day
                                skip_address = True
                            if package.truck_restriction and not skip_address:
                                if package.truck_restriction != truck.truck_id:
                                    skip_address = True
                        while priority_list.get(address) and not skip_address:
                            package = priority_list.get(address).pop()
                            truck.load_package(package, True)
                            self.packages_ready_for_dispatch.remove(package)
        delivery_group_list = routing.calculate_delivery_group_list(self.packages_ready_for_dispatch)
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.is_ready_for_dispatch and truck.get_remaining_capacity() > 0:
                for address in delivery_group_list:
                    skip_address = False
                    if len(delivery_group_list.get(address)) < truck.get_remaining_capacity():
                        for package in delivery_group_list.get(address):
                            if self.time_tracking.get_time().time() <= self.route_start_time and \
                                    truck.truck_id == 1 and package.package_id in self.packages.delivery_binding:
                                skip_address = True
                            if package.truck_restriction:
                                if package.truck_restriction != truck.truck_id:
                                    skip_address = True
                        while delivery_group_list.get(address) and not skip_address:
                            package = delivery_group_list.get(address).pop()
                            truck.load_package(package)
                            self.packages_ready_for_dispatch.remove(package)
        single_address_list = routing.generate_address_list(self.packages_ready_for_dispatch)
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub:
                for address, packages in single_address_list.items():
                    for package in packages:
                        if self.time_tracking.get_time().time() <= self.route_start_time and truck.truck_id == 1 and \
                                package.package_id in self.packages.delivery_binding:
                            continue
                        if package.truck_restriction:
                            if package.truck_restriction != truck.truck_id:
                                continue
                        if truck.get_remaining_capacity() > 0:
                            package = single_address_list.get(address).pop()
                            truck.load_package(package)
                            self.packages_ready_for_dispatch.remove(package)

    def calculate_routes(self):  # TODO - remove print statements
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.is_ready_for_dispatch:
                priority_route = list(truck.priority_package_manifest.keys())
                standard_route = list(truck.standard_package_manifest.keys())
                route = priority_route + standard_route + [self.addresses.get_hub_address()]
                routing.calculate_route(self, truck)
                tests.print_initial_routes(self)

    def dispatch_trucks(self):
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.is_ready_for_dispatch:
                truck.begin_route()

    def get_hub_address(self):
        return self.hub_address
