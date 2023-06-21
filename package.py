import csv
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from truck import Truck


class Package:
    status_codes = {
        0: 'Not Yet Arrived',
        1: 'Ready For Dispatch',
        2: 'Loaded on Truck',
        3: 'Out For Delivery',
        4: 'Delivered',
        5: 'Incorrect Address'
    }

    def __init__(self, package_id: int, address: str, city: str, state: str, zipcode: str, deadline: str,
                 mass: float, notes: str, status_code: int = 0):
        self.package_id = package_id
        self.street = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.deadline = deadline
        self.mass = mass
        self.notes = notes
        self.truck_restriction = None
        self.delivery_group = None
        self.priority = None
        self.status_code = status_code
        self.status = self.status_codes.get(self.status_code)
        self.ready_for_delivery = False
        self.delivery_time = None
        self.delivered_on_time = None
        self.time_checked_in = None
        self.time_loaded_on_truck = None
        self.time_delivered = None

    def __str__(self) -> str:
        return (f'ID: {self.package_id}, Address: {self.street}, City: {self.city}, State: {self.state}, '
                f'Zip: {self.zipcode}, Mass(kg): {self.mass}, Notes: {self.notes}, '
                f'Status: {self.status}, Delivery Deadline: {self.deadline}, Delivery Time: {self.delivery_time}, '
                f'Delivered On Time: {self.delivered_on_time}')

    def get_address(self) -> str:
        return f'{self.street} {self.zipcode}'

    def update_address(self, street: str, city: str, state: str, zipcode: str):
        self.street = street.upper()
        self.city = city.upper()
        self.state = state.upper()
        self.zipcode = zipcode

    def set_truck_restriction(self, truck_id: int):
        self.truck_restriction = truck_id

    def set_package_status(self, status_code: int, status: str = None):
        self.status_code = status_code
        if self.status_code == 1:
            self.ready_for_delivery = True
        if status:
            self.status = status
        else:
            self.status = self.status_codes.get(status_code)
        if status_code == 5:
            self.ready_for_delivery = False

    def mark_package_loaded(self, truck: 'Truck'):
        self.time_loaded_on_truck = truck.get_time()
        self.set_package_status(2, f'Loaded on truck {truck.truck_id} at {self.time_loaded_on_truck()}')

    def mark_package_out_for_delivery(self, truck: 'Truck'):
        self.set_package_status(3, f'Out for delivery on truck {truck.truck_id} at '
                                   f'{truck.get_time()}')

    def mark_package_delivered(self, truck: 'Truck'):
        self.set_package_status(4, f'Delivered by truck {truck.truck_id} at '
                                   f'{truck.get_time()}')
        self.delivery_time = truck.get_time()


class Hashtable:
    def __init__(self, num_buckets: int = 10):
        self.num_buckets = num_buckets
        self.table: list[list[Optional[Package]]] = []
        for i in range(num_buckets):
            self.table.append([])

    def hash(self, package_id: int):
        return package_id % self.num_buckets

    def insert(self, package: Package):
        key = self.hash(package.package_id)
        i = 0
        while i < len(self.table[key]):
            if package.package_id == self.table[key][i].package_id:
                self.update(key, i, package)
                return
            i += 1
        self.table[key].append(package)

    def update(self, key: int, index: int, package: Package):
        self.table[key][index] = package
        print(f'Updated package is: {package}')  # TODO - remove

    def search(self, package_id: int) -> Optional[Package]:
        key = self.hash(package_id)
        for i in range(len(self.table[key])):
            package = self.table[key][i]
            if package.package_id == package_id:
                return package
        return None

    def get_all_packages(self) -> list[Package]:
        all_packages = []
        for bucket in self.table:
            for package in bucket:
                all_packages.append(package)
        all_packages.sort(key=lambda p: p.package_id)
        return all_packages

    def print_all_packages(self):
        for package in self.get_all_packages():
            print(package)


class PackageCollection:
    def __init__(self):
        self.package_table = Hashtable()
        self.num_packages = 0
        self.delivery_binding = []
        self.priority_1_packages = []

    def import_packages(self, file: str):
        from routing import calculate_delivery_groups, calculate_delivery_priority
        with open(file, newline='') as packages:
            package_data = csv.reader(packages)
            next(package_data)
            for package in package_data:
                package_id = int(package[0])
                address = package[1].strip().upper()
                city = package[2].strip().upper()
                state = package[3].strip().upper()
                zipcode = package[4].strip()
                deadline = package[5].strip()
                mass = float(package[6].strip())
                notes = package[7].strip()
                address = address.replace('NORTH', 'N')
                address = address.replace('EAST', 'E')
                address = address.replace('SOUTH', 'S')
                address = address.replace('WEST', 'W')
                new_package = Package(package_id, address, city, state, zipcode, deadline, mass, notes)
                self.package_table.insert(new_package)
                self.num_packages += 1
            package_list = self.package_table.get_all_packages()
            calculate_delivery_groups(package_list)
            calculate_delivery_priority(self, package_list)

    def add_priority_1_package(self, package: Package):
        self.priority_1_packages.append(package)

    def remove_priority_1_package(self, package: Package):
        self.priority_1_packages.remove(package)

    def get_num_packages(self):
        return self.num_packages
