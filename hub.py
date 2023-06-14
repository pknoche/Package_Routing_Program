import routing
from address import AddressCollection
from package import PackageCollection, Package
from truck import TruckCollection, Truck


class Hub:
    def __init__(self, package_file: str, address_file: str, distance_file: str, num_trucks: int,
                 package_capacity_per_truck: int):
        self.packages = PackageCollection()
        self.packages.import_packages(package_file)
        self.addresses = AddressCollection()
        self.addresses.import_addresses(address_file)
        self.addresses.import_distances(distance_file)
        self.trucks = TruckCollection()
        self.packages_ready_for_dispatch: list[Package] = []
        for i in range(num_trucks):
            truck = Truck((i + 1), package_capacity_per_truck)
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

    def load_trucks(self):
        priority_list = routing.calculate_priority_list(self.packages_ready_for_dispatch)
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.get_remaining_capacity() > 0:
                for address in priority_list:
                    skip_address = False
                    if len(priority_list.get(address)) < truck.get_remaining_capacity():
                        for package in priority_list.get(address):
                            if package.truck_restriction:
                                if package.truck_restriction != truck.truck_id:
                                    skip_address = True
                        while priority_list.get(address) and not skip_address:
                            package = priority_list.get(address).pop()
                            truck.load_package(package, True)
                            self.packages_ready_for_dispatch.remove(package)
        delivery_group_list = routing.calculate_delivery_group_list(self.packages_ready_for_dispatch)
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.get_remaining_capacity() > 0:
                for address in delivery_group_list:
                    skip_address = False
                    if len(delivery_group_list.get(address)) < truck.get_remaining_capacity():
                        for package in delivery_group_list.get(address):
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
                    skip_address = False
                    for package in packages:
                        if package.truck_restriction:
                            if package.truck_restriction != truck.truck_id:
                                skip_address = True
                        while truck.get_remaining_capacity() > 0 and not skip_address:
                            truck.load_package(package)










        ''' TODO - remove
        truck_index = truck_id - 1  # Convert truck number to index
        if truck_index < len(self.trucks.all_trucks):
            while len(self.trucks.all_trucks[truck_index].package_manifest) < load_size:
                truck = self.trucks.all_trucks[truck_index]
                if self.packages_ready_for_dispatch and truck.is_at_hub:
                    package = self.packages_ready_for_dispatch[0]
                    if package.truck_restriction and package.truck_restriction != truck.truck_id:
                        self.trucks.all_trucks[package.truck_restriction - 1].load_package(package)
                        self.packages_ready_for_dispatch.pop(0)
                    else:
                        self.trucks.all_trucks[truck_index].load_package(package)
                        self.packages_ready_for_dispatch.pop(0)
            self.load_trucks(load_size, truck_id + 1)
            '''


