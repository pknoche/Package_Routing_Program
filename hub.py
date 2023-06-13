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
        package = self.packages.all_packages.search(package_id)
        if status_override:
            package.status_code = status_override
            package.status = package.status_codes.get(status_override)
        elif self.addresses.address_is_valid(package.get_address()):
            package.status_code = 1
            package.status = package.status_codes.get(1)
            self.addresses.add_delivery_address(package.get_address())
            self.packages_ready_for_dispatch.append(package)
        else:
            package.status_code = 4
            package.status = package.status_codes.get(4)

    def calculate_load_size(self, num_trucks: int):
        load_size = len(self.addresses.delivery_addresses) // num_trucks  # this calculation could yield a
        # lower number than the actual number of packages if there are multiple packages ready to dispatch for one
        # address. Still, the logic is desired because it results in an even distribution of stops per truck.
        # There is an opportunity to optimize this in the future. FIXME - review
        if load_size > self.trucks.all_trucks[0].package_capacity:  # This code will need to be modified
            # if functionality is added to have different capacity trucks per collection in the future.
            load_size = self.trucks.all_trucks[0].package_capacity
        return load_size

    def load_trucks(self, load_size: int, truck_number: int):
        truck_index = truck_number - 1  # Convert truck number to index
        if truck_index < len(self.trucks.all_trucks):
            for i in range(0, load_size):
                if self.packages_ready_for_dispatch and self.trucks.all_trucks[truck_index].is_ready_to_load:
                    package = self.packages_ready_for_dispatch.pop(0)
                    self.trucks.all_trucks[truck_index].load_package(package)
            self.load_trucks(load_size, truck_number + 1)


