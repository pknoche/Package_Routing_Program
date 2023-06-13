from address import Address
from helper import get_time
from package import Package


class Truck:
    def __init__(self, truck_id: int, package_capacity: int, address_list: dict[Address] = None):
        if address_list is None:
            address_list = {}
        self.truck_id = truck_id
        self.package_manifest = []
        self.address_list = address_list
        self.package_capacity = package_capacity
        self.is_at_hub = True

    def load_package(self, package: Package) -> bool:
        if len(self.package_manifest) < self.package_capacity and package.status_code == 1:
            self.package_manifest.append(package)
            package.status = f'Loaded on truck {self.truck_id} at {get_time()}'
            return True
        return False

    def deliver_package(self, package: Package) -> bool:
        if package in self.package_manifest:
            package.status_code = 3
            package.status = f'Delivered by truck {self.truck_id} at {get_time()}'
            self.package_manifest.remove(package)
            self.address_list.pop(package.get_address())
            return True
        return False


class TruckCollection:
    def __init__(self):
        self.all_trucks: list[Truck] = []

    def add_truck(self, truck: Truck):
        self.all_trucks.append(truck)
