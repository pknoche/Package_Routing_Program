from datetime import time

import helper
import routing
from address import AddressCollection
from dev import tests
from package import PackageCollection, Package
from truck import TruckCollection, Truck


class Hub:
    def __init__(self, package_file: str, address_file: str, distance_file: str, num_trucks: int,
                 package_capacity_per_truck: int, truck_speed: float):
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

    def check_in_package(self, package_id: int, status_override: int = None):
        package = self.packages.package_table.search(package_id)
        if status_override:
            package.set_package_status(status_override)
        elif self.addresses.address_is_valid(package.get_address()):
            package.set_package_status(1)
            self.packages_ready_for_dispatch.append(package)
        else:
            package.set_package_status(4)

    def correct_package_address(self, package_id: int, street: str, city: str, state: str, zipcode: str):
        package = self.packages.package_table.search(package_id)
        package.update_address(street, city, state, zipcode)
        package.set_package_status(1)
        self.packages_ready_for_dispatch.append(package)

    def load_trucks(self):
        priority_list = routing.calculate_priority_list(self.packages_ready_for_dispatch)
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.is_ready_for_dispatch and truck.get_remaining_capacity() > 0:
                for address in priority_list:
                    skip_address = False
                    if len(priority_list.get(address)) < truck.get_remaining_capacity():
                        for package in priority_list.get(address):
                            number_priority_packages = sum(len(packages) for packages in priority_list.values())
                            number_bound_packages = len(self.packages.delivery_binding)
                            if package.package_id in self.packages.delivery_binding and \
                                    number_priority_packages + number_bound_packages > truck.get_remaining_capacity() \
                                    and truck.truck_id == 1 and truck.total_miles_traveled == 0:
                                skip_address = True  # Don't load packages
                                # bound together on first truck of day in order to maximize number of priority packages
                                # loaded on first truck if priority packages + bound packages is > truck capacity.
                            if package.truck_restriction and not skip_address:
                                if package.truck_restriction != truck.truck_id:
                                    skip_address = True
                        while priority_list.get(address) and not skip_address:
                            package = priority_list.get(address).pop()
                            truck.load_package(package, True)
                            self.packages_ready_for_dispatch.remove(package)
        delivery_group_list = routing.generate_delivery_group_list(self.packages_ready_for_dispatch)
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.is_ready_for_dispatch and truck.get_remaining_capacity() > 0:
                for address in delivery_group_list:
                    skip_address = False
                    if len(delivery_group_list.get(address)) < truck.get_remaining_capacity():
                        for package in delivery_group_list.get(address):  # FIXME - review logic for bound packages
                            if package.package_id in self.packages.delivery_binding and truck.truck_id == 1 and \
                                    truck.total_miles_traveled == 0:
                                skip_address = True
                            if package.truck_restriction:
                                if package.truck_restriction != truck.truck_id:
                                    skip_address = True
                        while delivery_group_list.get(address) and not skip_address:
                            package = delivery_group_list.get(address).pop()
                            truck.load_package(package)
                            self.packages_ready_for_dispatch.remove(package)
        single_address_list = routing.generate_single_package_delivery_list(self.packages_ready_for_dispatch)
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.is_ready_for_dispatch and truck.get_remaining_capacity() > 0:
                for package in single_address_list:
                    if package.package_id in self.packages.delivery_binding and truck.truck_id == 1 and \
                            truck.total_miles_traveled == 0:  # FIXME - review logic for bound packages
                        continue
                    if package.truck_restriction:
                        if package.truck_restriction != truck.truck_id:
                            continue
                    if truck.get_remaining_capacity() > 0:
                        truck.load_package(package)
                        self.packages_ready_for_dispatch.remove(package)

    def load_priority_1_packages(self, truck: Truck):
        for package in self.packages.priority_1_packages:
            truck.load_package(package)
            self.packages_ready_for_dispatch.remove(package)

    def calculate_routes(self):  # TODO - remove print statements
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.is_ready_for_dispatch:
                routing.calculate_route(self, truck)
                tests.print_routes(self)

    def dispatch_trucks(self):
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.is_ready_for_dispatch:
                truck.begin_route()

    def get_hub_address(self):
        return self.hub_address
