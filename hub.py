from address import AddressCollection
from package import PackageCollection
from truck import TruckCollection, Truck


class Hub:
    def __init__(self, package_file: str, address_file: str, distance_file: str, num_trucks: int):
        self.packages = PackageCollection()
        self.packages.import_packages(package_file)
        self.addresses = AddressCollection()
        self.addresses.import_addresses(address_file)
        self.addresses.import_distances(distance_file)
        self.trucks = TruckCollection()
        for i in range(num_trucks):
            truck = Truck(i + 1)
            self.trucks.add_truck(truck)

    def check_in_package(self, package_id: int, status_override: int = None):
        package = self.packages.all_packages.search(package_id)
        if status_override:
            package.status_code = status_override
            package.status = package.status_codes.get(status_override)
        elif self.addresses.address_is_valid(package.address + ' ' + package.zipcode):
            package.status_code = 1
            package.status = package.status_codes.get(1)
        else:
            package.status_code = 4
            package.status = package.status_codes.get(4)
