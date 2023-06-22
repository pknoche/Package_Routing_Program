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
        self.packages_ready_for_dispatch: list[Package] = []
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
            self.packages_ready_for_dispatch.append(package)
        else:
            package.set_status(4)
        package.mark_package_checked_in(time_scanned)

    def correct_package_address(self, package_id: int, street: str, city: str, state: str, zipcode: str):
        package = self.packages.search(package_id)
        package.update_address(street, city, state, zipcode)
        package.set_status(1)
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
            packages_loaded = set()
            delivery_groups_loaded = set()
            i = 0
            while i < len(self.packages.priority_1_packages) and truck.get_remaining_capacity() > 0:
                package = self.packages.priority_1_packages[i]
                if package.truck_restriction != truck.truck_id:
                    i += 1
                    continue
                if package in self.packages.get_bound_packages():
                    bound_packages = self.packages.get_bound_packages()
                    if len(bound_packages) <= truck.get_remaining_capacity():
                        bound_packages_deliver_groups = set()
                        for package in bound_packages:
                            truck.load_package(package)
                            packages_loaded.add(package)
                            if package.delivery_group:
                                bound_packages_deliver_groups.add(package.delivery_group)
                        truck_restriction = False
                        sorted_delivery_groups_by_size = sorted(delivery_group_list,
                                                                key=lambda x: len(delivery_group_list[x]))
                        for delivery_group in sorted_delivery_groups_by_size:
                            truck_restriction = False
                            packages = delivery_group_list.get(delivery_group)
                            for package in packages:
                                if package.truck_restriction and package.truck_restriction != truck.truck_id:
                                    truck_restriction = True
                                    break
                            delivery_group_size = len(delivery_group_list.get(delivery_group))
                            if delivery_group_size <= truck.get_remaining_capacity() and not truck_restriction:
                                delivery_groups_loaded.add(delivery_group)
                                for package in packages:
                                    truck.load_package(package)
                                    packages_loaded.add(package)
            for package in packages_loaded:
                self.packages_ready_for_dispatch.remove(package)
            if delivery_groups_loaded:
                for delivery_group in delivery_groups_loaded:
                    delivery_group_list.pop(delivery_group)






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
                    if package.package_id in self.packages.bound_packages and \
                            len(self.packages.bound_packages) <= truck.get_remaining_capacity():
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
        if len(self.packages.bound_packages) <= truck.get_remaining_capacity():
            for package in self.packages_ready_for_dispatch:
                if package.package_id in self.packages.bound_packages:
                    if package.truck_restriction:
                        if package.truck_restriction != truck.truck_id:
                            return  # Do not load bound packages on this truck if any are restricted from current truck.
            priority_1_package_removed = False
            i = 0
            while i < len(self.packages_ready_for_dispatch):
                package = self.packages_ready_for_dispatch[i]
                if delivery_group_list.get(package.get_address()):
                    priority_1_package_removed = \
                        self.load_delivery_group_packages(truck, delivery_group_list, package.get_address())
                if package.package_id in self.packages.bound_packages:
                    if package.package_id in self.packages.priority_1_packages:
                        priority_1_package_removed = True
                    truck.load_package(self.packages_ready_for_dispatch.pop(i))
                else:
                    i += 1
            return priority_1_package_removed

    def load_delivery_group_packages(self, truck: Truck, delivery_group_list: dict[str, list[Package]],
                                     delivery_group_address: str = None):
        if delivery_group_address:
            priority_1_package_removed = False
            packages = delivery_group_list.get(delivery_group_address)
            if len(packages) <= truck.get_remaining_capacity():
                i = 0
                while i < len(packages):
                    package = packages.pop()
                    truck.load_package(package)
                    self.packages_ready_for_dispatch.remove(package)
                    if package in self.packages.priority_1_packages:
                        self.packages.priority_1_packages.remove(package)
                        priority_1_package_removed = True
                delivery_group_list.pop(delivery_group_address)
                return priority_1_package_removed
        else:
            delivery_groups_loaded = set()
            for address in delivery_group_list:
                skip_address = False
                if len(delivery_group_list.get(address)) <= truck.get_remaining_capacity():
                    for package in delivery_group_list.get(address):
                        if package.truck_restriction and not skip_address:
                            if package.truck_restriction != truck.truck_id:
                                skip_address = True
                                break
                        if package.package_id in self.packages.bound_packages and \
                                len(self.packages.bound_packages) <= truck.get_remaining_capacity():
                            skip_address = True
                            self.load_bound_packages(truck, delivery_group_list)
                    while delivery_group_list.get(address) and not skip_address:
                        package_list = delivery_group_list.get(address)
                        delivery_groups_loaded.add(address)
                        i = 0
                        while i < len(package_list):
                            package = package_list.pop()
                            truck.load_package(package)
                            if package in self.packages_ready_for_dispatch:
                                self.packages_ready_for_dispatch.remove(package)
            for delivery_group in delivery_groups_loaded:
                delivery_group_list.pop(delivery_group)

    def load_single_packages(self, truck: Truck):
        single_address_list = routing.generate_single_package_delivery_list(self.packages_ready_for_dispatch)
        while truck.get_remaining_capacity() > 0 and single_address_list:
            package = single_address_list.pop()
            truck.load_package(package)
            self.packages_ready_for_dispatch.remove(package)

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
