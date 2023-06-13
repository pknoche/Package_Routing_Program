import csv
from typing import Optional


class Package:
    status_codes = {
        0: 'Not Yet Arrived',
        1: 'Ready For Dispatch',
        2: 'Out For Delivery',
        3: 'Delivered',
        4: 'Incorrect Address'
    }

    def __init__(self, package_id: int, address: str, city: str, state: str, zipcode: str, deadline: str,
                 mass: float, notes: str, status_code: int = 0):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.deadline = deadline
        self.mass = mass
        self.notes = notes
        self.status_code = status_code
        self.status = self.status_codes.get(self.status_code)

    def __str__(self) -> str:
        return (f'ID: {self.package_id}, Address: {self.address}, City: {self.city}, State: {self.state}, '
                f'Zip: {self.zipcode}, Delivery Deadline: {self.deadline}, Mass(kg): {self.mass}, Notes: {self.notes}, '
                f'Status: {self.status}')

    def get_address(self):
        return f'{self.address} {self.zipcode}'


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


class PackageCollection:
    def __init__(self):
        self.all_packages = Hashtable()
        self.num_packages = 0

    def import_packages(self, file: str):
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
                self.all_packages.insert(new_package)
                self.num_packages += 1
