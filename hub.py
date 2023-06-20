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
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.is_ready_for_dispatch and truck.get_remaining_capacity() > 0:
                delivery_group_list = routing.generate_delivery_group_list(self.packages_ready_for_dispatch)
                self.load_priority_1_packages(truck, delivery_group_list)
                self.load_priority_2_packages(truck, delivery_group_list)
                self.load_delivery_group_packages(truck, delivery_group_list)
                self.load_bound_packages(truck, delivery_group_list)
                self.load_single_packages(truck)
                packages_on_truck = list(truck.packages_on_truck)[:]
                priority_manifest = routing.generate_priority_list(packages_on_truck)
                for address, packages in priority_manifest.items():
                    for package in packages:
                        packages_on_truck.remove(package)
                standard_manifest = routing.generate_address_list(packages_on_truck)
                truck.set_priority_manifest(priority_manifest)
                truck.set_standard_manifest(standard_manifest)

    def load_priority_1_packages(self, truck: Truck, delivery_group_list: dict[str, list[Package]]):
        if self.packages.priority_1_packages:
            i = 0
            while i < len(self.packages.priority_1_packages) and truck.get_remaining_capacity() > 0:
                package = self.packages.priority_1_packages[i]
                if package.truck_restriction != truck.truck_id:
                    i += 1
                    continue
                if package.delivery_group:
                    delivery_group_address = package.get_address()
                    self.load_delivery_group_packages(truck, delivery_group_list, delivery_group_address)
                elif package.package_id in self.packages.delivery_binding:
                    self.load_bound_packages(truck, delivery_group_list)
                else:
                    truck.load_package(package)
                    self.packages.priority_1_packages.pop(i)
                i += 1

    def load_priority_2_packages(self, truck: Truck, delivery_group_list: dict[str, list[Package]]):
        delivery_groups_loaded = set()
        priority_list = routing.generate_priority_list(self.packages_ready_for_dispatch)
        for address in priority_list:
            skip_address = False
            if len(priority_list.get(address)) <= truck.get_remaining_capacity():
                for package in priority_list.get(address):
                    if package.truck_restriction and not skip_address:
                        if package.truck_restriction != truck.truck_id:
                            skip_address = True
                            break
                    if package.package_id in self.packages.delivery_binding and \
                            len(self.packages.delivery_binding) <= truck.get_remaining_capacity():
                        skip_address = True
                        self.load_bound_packages(truck, delivery_group_list)
                while priority_list.get(address) and not skip_address:
                    package_list = priority_list.get(address)
                    i = 0
                    while i < len(package_list):
                        package = package_list.pop()
                        truck.load_package(package)
                        if package in self.packages_ready_for_dispatch:
                            self.packages_ready_for_dispatch.remove(package)
                        delivery_groups_loaded.add(package.get_address())

    def load_bound_packages(self, truck: Truck, delivery_group_list: dict[str, list[Package]]):
        if len(self.packages.delivery_binding) <= truck.get_remaining_capacity():
            for package in self.packages_ready_for_dispatch:
                if package.package_id in self.packages.delivery_binding:
                    if package.truck_restriction:
                        if package.truck_restriction != truck.truck_id:
                            return  # Do not load bound packages on this truck if any are restricted from current truck.
            i = 0
            while i < len(self.packages_ready_for_dispatch):
                package = self.packages_ready_for_dispatch[i]
                if delivery_group_list.get(package.get_address()):
                    self.load_delivery_group_packages(truck, delivery_group_list, package.get_address())
                if package.package_id in self.packages.delivery_binding:
                    truck.load_package(self.packages_ready_for_dispatch.pop(i))
                else:
                    i += 1

    def load_delivery_group_packages(self, truck: Truck, delivery_group_list: dict[str, list[Package]],
                                     delivery_group_address: str = None):
        if delivery_group_address:
            packages = delivery_group_list.get(delivery_group_address)
            if len(packages) <= truck.get_remaining_capacity():
                i = 0
                while i < len(packages):
                    package = packages.pop()
                    truck.load_package(package)
                    self.packages_ready_for_dispatch.remove(package)
                    if package in self.packages.priority_1_packages:
                        self.packages.priority_1_packages.remove(package)
                delivery_group_list.pop(delivery_group_address)
        else:
            delivery_group_list = routing.generate_delivery_group_list(self.packages_ready_for_dispatch)
            for address in delivery_group_list:
                skip_address = False
                if len(delivery_group_list.get(address)) <= truck.get_remaining_capacity():
                    for package in delivery_group_list.get(address):
                        if package.truck_restriction and not skip_address:
                            if package.truck_restriction != truck.truck_id:
                                skip_address = True
                                break
                        if package.package_id in self.packages.delivery_binding and \
                                len(self.packages.delivery_binding) <= truck.get_remaining_capacity():
                            skip_address = True
                            self.load_bound_packages(truck, delivery_group_list)
                    while delivery_group_list.get(address) and not skip_address:
                        package_list = delivery_group_list.get(address)
                        i = 0
                        while i < len(package_list):
                            package = package_list.pop()
                            truck.load_package(package)
                            if package in self.packages_ready_for_dispatch:
                                self.packages_ready_for_dispatch.remove(package)


    def load_single_packages(self, truck: Truck):
        single_address_list = routing.generate_single_package_delivery_list(self.packages_ready_for_dispatch)
        while truck.get_remaining_capacity() > 0 and single_address_list:
            package = single_address_list.pop()
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
