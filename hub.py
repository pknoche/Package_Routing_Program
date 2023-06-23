from datetime import time

import routing
from address import AddressCollection
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
        self.packages_ready_for_dispatch = set()
        self.hub_address = self.addresses.get_hub_address()
        for i in range(num_trucks):
            truck = Truck((i + 1), package_capacity_per_truck, truck_speed, self)
            self.trucks.add_truck(truck)

    def check_in_package(self, time_scanned: time, package_id: int, status_override: int = None):
        package = self.packages.search(package_id)
        if status_override:
            package.set_status(status_override)
        elif self.addresses.address_is_valid(package.get_address()):
            package.set_status(1)
            self.packages_ready_for_dispatch.add(package)
        else:
            package.set_status(4)
        package.mark_package_checked_in(time_scanned)

    def correct_package_address(self, package_id: int, street: str, city: str, state: str, zipcode: str):
        package = self.packages.search(package_id)
        package.update_address(street, city, state, zipcode)
        package.set_status(1)
        self.packages_ready_for_dispatch.add(package)

    def load_trucks(self):
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.is_ready_for_dispatch and truck.get_remaining_capacity() > 0:
                delivery_group_list = routing.generate_delivery_group_list(self.packages_ready_for_dispatch)
                self.load_priority_packages(truck, delivery_group_list, priority_num=1)
                if truck.get_remaining_capacity() > 0:
                    self.load_priority_packages(truck, delivery_group_list, priority_num=2)
                if truck.get_remaining_capacity() > 0:
                    self.load_group_packages(truck, self.packages_ready_for_dispatch, delivery_group_list)
                if truck.get_remaining_capacity() > 0:
                    self.load_bound_packages(truck)
                if truck.get_remaining_capacity() > 0:
                    self.load_single_packages(truck)

                packages_on_truck = truck.get_packages().copy()
                priority_manifest = routing.generate_priority_list(packages_on_truck)
                for address, packages in priority_manifest.items():
                    for package in packages:
                        packages_on_truck.remove(package)
                standard_manifest = routing.generate_address_list(packages_on_truck)
                truck.set_priority_manifest(priority_manifest)
                truck.set_standard_manifest(standard_manifest)

    def load_priority_packages(self, truck: Truck, delivery_group_list: dict[str, list[Package]], priority_num: int):
        priority_package_list = None
        if priority_num == 1:
            priority_package_list = self.packages.get_priority_1_packages()
        elif priority_num == 2:
            priority_package_list = self.packages.get_priority_2_packages()
        if priority_package_list:
            packages_loaded = self.load_group_packages(truck, priority_package_list, delivery_group_list)
            for package in packages_loaded:
                if package in priority_package_list:
                    priority_package_list.remove(package)

    #  "group" in the context of this function name refers to any type of package group,
    #  whether that be priority 1 packages, priority 2 packages, or packages assigned to a delivery group, which is
    #  defined in terms of an address when a package shares this address with one or more other packages.
    def load_group_packages(self, truck: Truck, package_group: set[Package],
                            delivery_group_list: dict[str, list[Package]]):
        packages_loaded = set()
        bound_packages_loaded_addresses = {}
        sorted_package_group_keys_by_size = sorted(delivery_group_list, key=lambda x: len(delivery_group_list[x]))
        for package_group_key in sorted_package_group_keys_by_size:
            for package in delivery_group_list[package_group_key]:
                if package not in package_group:
                    continue
                if package.truck_restriction and package.truck_restriction != truck.truck_id:
                    continue
                if package in self.packages.get_bound_packages():
                    bound_packages = self.packages.get_bound_packages()
                    if len(bound_packages) <= truck.get_remaining_capacity():
                        for bound_package in bound_packages:
                            truck.load_package(bound_package)
                            packages_loaded.add(bound_package)
                            package_address = bound_package.get_address()
                            if package_address in delivery_group_list:
                                if package_address not in bound_packages_loaded_addresses:
                                    bound_packages_loaded_addresses[package_address] = []
                                    bound_packages_loaded_addresses[package_address].append(bound_package)
                                else:
                                    bound_packages_loaded_addresses[package_address].append(bound_package)
                    if bound_packages_loaded_addresses:
                        for address in bound_packages_loaded_addresses:
                            num_packages = len(bound_packages_loaded_addresses[address])
                            if len(delivery_group_list.get(address)) - num_packages <= truck.get_remaining_capacity():
                                for grouped_package in delivery_group_list.get(address):
                                    truck.load_package(grouped_package)
                                    packages_loaded.add(package)
                else:
                    if package.delivery_group and len(
                            delivery_group_list[package.get_address()]) <= truck.get_remaining_capacity():
                        delivery_group = delivery_group_list.get(package.get_address())
                        for grouped_package in delivery_group:
                            truck.load_package(grouped_package)
                            packages_loaded.add(grouped_package)
                    elif not package.delivery_group and package.priority:
                        truck.load_package(package)
                        packages_loaded.add(package)
        if bound_packages_loaded_addresses:
            bound_packages = self.packages.get_bound_packages()
            for package in bound_packages:
                address = package.get_address()
                if address in delivery_group_list:
                    delivery_group_package_list = delivery_group_list[address]
                    delivery_group_package_list.remove(package)
        self.remove_from_dispatch_list(packages_loaded, delivery_group_list)
        return packages_loaded

    def load_bound_packages(self, truck: Truck):
        bound_packages = self.packages.get_bound_packages()
        if len(bound_packages) > truck.get_remaining_capacity():
            return
        for package in bound_packages:
            if package.truck_restriction and package.truck_restriction != truck.truck_id or \
                    package not in self.packages_ready_for_dispatch:
                return
        for package in bound_packages:
            truck.load_package(package)
            self.packages_ready_for_dispatch.remove(package)

    def load_single_packages(self, truck: Truck):
        single_package_list = routing.generate_single_package_delivery_list(self.packages_ready_for_dispatch)
        packages_loaded = set()
        while truck.get_remaining_capacity() > 0 and len(single_package_list) > 0:
            package = next(iter(single_package_list))
            if package.truck_restriction:
                if package.truck_restriction != truck.truck_id:
                    single_package_list.remove(package)
                    continue
            truck.load_package(package)
            packages_loaded.add(package)
            single_package_list.remove(package)
        self.remove_from_dispatch_list(packages_loaded)

    def remove_from_dispatch_list(self, packages: set[Package], delivery_group_list: dict[str, list[Package]] = None):
        for package in packages:
            self.packages_ready_for_dispatch.remove(package)
            address = package.get_address()
            if not delivery_group_list:
                continue
            if address in delivery_group_list:
                package_list = delivery_group_list.get(address)
                if package in package_list:
                    package_list.remove(package)

    def calculate_routes(self):
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.is_ready_for_dispatch:
                routing.calculate_route(self, truck)

    def dispatch_trucks(self):
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.is_ready_for_dispatch:
                truck.begin_route()

    def get_hub_address(self):
        return self.hub_address

    def print_end_of_day_report(self):
        print('Truck Report:\n')
        total_miles_traveled = 0
        for truck in self.trucks.all_trucks:
            print(f'Truck {truck.get_truck_id()}:')
            for entry in truck.travel_log:
                print(entry)
            total_miles_traveled += truck.get_miles_traveled()
            print(f'Total distance traveled by truck {truck.get_truck_id()} today: '
                  f'{truck.get_miles_traveled():.1f} miles.\n')
        print(f'\nTotal distance traveled by all trucks today: {total_miles_traveled:.1f} miles.\n\n')

        print('Package Report:\n')
        not_delivered = []
        late_deliveries = []
        for package in self.packages.get_all_packages():
            print(package)
            if package.get_status_code() != 4:
                not_delivered.append(package)
                continue
            if package.get_on_time_delivery_status() is False:
                late_deliveries.append(package)
        print()
        if not_delivered:
            all_delivered = False
        if late_deliveries:
            all_on_time = False
        if not not_delivered and not late_deliveries:
            print('All packages were delivered on time!')
        else:
            print('The following packages were not delivered on time:\n')
        if not_delivered:
            print('Not Delivered:')
            for package in not_delivered:
                print(package)
            print()
        if late_deliveries:
            print('Late Deliveries:')
            for package in late_deliveries:
                print(package)
