from address import Address
from package import Package


class Truck:
    def __init__(self, truck_id: int, package_capacity: int, hub_address: str):
        self.truck_id = truck_id
        self.priority_package_manifest: dict[Address, list[Package]] = {}
        self.standard_package_manifest: dict[Address, list[Package]] = {}
        self.route = []
        self.initial_route_distance = None
        self.package_capacity = package_capacity
        self.num_packages_loaded = 0
        self.is_at_hub = True
        self.current_address = hub_address

    def load_package(self, package: Package, is_priority: bool = False):
        address = package.get_address()
        if is_priority:
            if address in self.priority_package_manifest:
                self.priority_package_manifest[address].append(package)
            else:
                self.priority_package_manifest[address] = [package]
        else:
            if address in self.standard_package_manifest:
                self.standard_package_manifest[address].append(package)
            else:
                self.standard_package_manifest[address] = [package]
        package.mark_package_loaded(self)
        self.num_packages_loaded += 1

    def deliver_packages(self, address: Address):
        if address in self.standard_package_manifest:
            for package in self.standard_package_manifest.get(address):
                package.status = f'Delivered by truck {self.truck_id}'
        del self.standard_package_manifest[address]

    def get_num_packages_loaded(self):
        return self.num_packages_loaded

    def get_remaining_capacity(self):
        return self.package_capacity - self.num_packages_loaded

    def set_route(self, route: list[Address]):
        self.route = route

    def set_route_distance(self, distance: int):
        self.initial_route_distance = distance


class TruckCollection:
    def __init__(self):
        self.all_trucks: list[Truck] = []

    def add_truck(self, truck: Truck):
        self.all_trucks.append(truck)
