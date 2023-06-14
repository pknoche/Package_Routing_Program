from address import Address
from helper import get_time
from package import Package


class Truck:
    def __init__(self, truck_id: int, package_capacity: int):
        self.truck_id = truck_id
        self.priority_package_manifest: dict[Address, list[Package]] = {}
        self.package_manifest: dict[Address, list[Package]] = {}
        self.package_capacity = package_capacity
        self.num_packages_loaded = 0
        self.is_at_hub = True

    def load_package(self, package: Package, priority: bool = False):
        address = package.get_address()
        if priority:
            if address in self.priority_package_manifest:
                self.priority_package_manifest[address].append(package)
            else:
                self.priority_package_manifest[address] = [package]
        else:
            if address in self.package_manifest:
                self.package_manifest[address].append(package)
            else:
                self.package_manifest[address] = [package]
        package.mark_package_loaded(self)
        self.num_packages_loaded += 1

    def deliver_packages(self, address: Address):
        if address in self.package_manifest:
            for package in self.package_manifest.get(address):
                package.status = f'Delivered by truck {self.truck_id}'
        del self.package_manifest[address]

    def get_num_packages_loaded(self):
        return self.num_packages_loaded

    def get_remaining_capacity(self):
        return self.package_capacity - self.num_packages_loaded



class TruckCollection:
    def __init__(self):
        self.all_trucks: list[Truck] = []

    def add_truck(self, truck: Truck):
        self.all_trucks.append(truck)
