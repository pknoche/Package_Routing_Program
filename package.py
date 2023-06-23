import copy
import csv
from datetime import time, datetime
from typing import Optional, TYPE_CHECKING, Union

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
        self.truck = None
        self.delivered_on_time: Union[bool, None] = None
        self.time_checked_in = None
        self.time_loaded_on_truck = None
        self.time_out_for_delivery = None
        self.time_delivered = None

    def __str__(self) -> str:
        return (f'ID: {self.package_id}, Address: {self.street}, City: {self.city}, State: {self.state}, '
                f'Zip: {self.zipcode}, Mass(kg): {self.mass}, Notes: {self.notes}, '
                f'Delivery Deadline: {self.deadline}, Status: {self.status}')

    def get_address(self) -> str:
        return f'{self.street} {self.zipcode}'

    def update_address(self, street: str, city: str, state: str, zipcode: str):
        self.street = street.upper()
        self.city = city.upper()
        self.state = state.upper()
        self.zipcode = zipcode

    def set_truck_restriction(self, truck_id: int):
        self.truck_restriction = truck_id

    def set_status(self, status_code: int, status: str = None):
        self.status_code = status_code
        if self.status_code == 1:
            self.ready_for_delivery = True
        if status:
            self.status = status
        else:
            self.status = self.status_codes.get(status_code)
        if status_code == 5:
            self.ready_for_delivery = False

    def set_delivery_group(self, delivery_group: int):
        self.delivery_group = delivery_group

    def get_status_code(self):
        return self.status_code

    def get_on_time_delivery_status(self):
        return self.delivered_on_time

    def mark_package_checked_in(self, time_scanned: time):
        self.time_checked_in = time_scanned

    def mark_package_loaded(self, truck: 'Truck'):
        self.truck = truck.get_truck_id()
        self.time_loaded_on_truck = truck.get_time()
        self.set_status(2, f'Loaded on truck {truck.truck_id} at {self.time_loaded_on_truck}')

    def mark_package_out_for_delivery(self, truck: 'Truck'):
        self.time_out_for_delivery = truck.get_time()
        self.set_status(3, f'Out for delivery on truck {truck.truck_id} at {self.time_out_for_delivery}')

    def mark_package_delivered(self, truck: 'Truck'):
        self.time_delivered = truck.get_time()
        if self.deadline != 'EOD':
            if self.time_delivered > self.deadline:
                self.delivered_on_time = False
            else:
                self.delivered_on_time = True
        else:
            self.delivered_on_time = True

        self.set_status(4, f'Delivered by truck {truck.truck_id} at {self.time_delivered}')


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

    def search(self, package_id: int) -> Optional[Package]:
        key = self.hash(package_id)
        for i in range(len(self.table[key])):
            package = self.table[key][i]
            if package.package_id == package_id:
                return package
        return None


class PackageCollection:
    def __init__(self):
        self.package_table = Hashtable()
        self.num_packages = 0
        self.bound_packages = set()
        self.priority_1_packages = set()
        self.priority_2_packages = set()

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
                if deadline != 'EOD':
                    deadline = datetime.strptime(deadline, '%I:%M %p').time()
                mass = float(package[6].strip())
                notes = package[7].strip()
                address = address.replace('NORTH', 'N')
                address = address.replace('EAST', 'E')
                address = address.replace('SOUTH', 'S')
                address = address.replace('WEST', 'W')
                new_package = Package(package_id, address, city, state, zipcode, deadline, mass, notes)
                self.package_table.insert(new_package)
                self.num_packages += 1
            packages = set(self.get_all_packages())
            calculate_delivery_groups(packages)
            calculate_delivery_priority(self, packages)

    def search(self, package_id: int):
        return self.package_table.search(package_id)

    def add_priority_1_package(self, package: Package):
        self.priority_1_packages.add(package)

    def remove_priority_1_package(self, package: Package):
        self.priority_1_packages.remove(package)

    def get_priority_1_packages(self) -> set[Package]:
        return self.priority_1_packages

    def add_priority_2_package(self, package: Package):
        self.priority_2_packages.add(package)

    def remove_priority_2_package(self, package: Package):
        self.priority_2_packages.remove(package)

    def get_priority_2_packages(self) -> set[Package]:
        return self.priority_2_packages

    def set_package_binding(self, package_ids: set[int]):
        for i in package_ids:
            package = self.search(i)
            self.bound_packages.add(package)

    def get_bound_packages(self) -> set[Package]:
        return self.bound_packages

    def get_num_packages(self):
        return self.num_packages

    def get_all_packages(self) -> list[Package]:
        all_packages = []
        for bucket in self.package_table.table:
            for package in bucket:
                all_packages.append(package)
        all_packages.sort(key=lambda p: p.package_id)
        return all_packages

    def print_all_packages(self):
        for package in self.get_all_packages():
            print(package)

    def print_all_packages_at_time(self, time_input: time):
        # Make copy of packages so status can be modified for printing at snapshot in time without losing original data.
        all_packages = copy.deepcopy(self.get_all_packages())
        not_yet_arrived = []
        at_hub = []
        loaded_on_truck = []
        out_for_delivery = []
        delivered = []
        for package in all_packages:
            if package.time_checked_in > time_input:
                package.set_status(0)
                not_yet_arrived.append(package)
            elif package.time_loaded_on_truck > time_input:
                package.set_status(1, f'Arrived at hub at {package.time_checked_in}')
                at_hub.append(package)
            elif package.time_out_for_delivery > time_input:  # TODO - consider deleting loaded on truck status
                package.set_status(2, f'Loaded on truck {package.truck} at {package.time_loaded_on_truck}')
                loaded_on_truck.append(package)
            elif package.time_delivered > time_input:
                package.set_status(2, f'Out for delivery on truck {package.truck} at '
                                      f'{package.time_out_for_delivery}')
                out_for_delivery.append(package)
            else:
                package.set_status(2, f'Delivered by truck {package.truck} at {package.time_delivered}')
                delivered.append(package)
        print(f'Status Of All Packages As Of {time_input.strftime("%H:%M")}:')
        print('Not Yet Arrived At Hub:')
        if not_yet_arrived:
            for package in not_yet_arrived:
                print(package)
            print()
        else:
            print('None\n')
        print('At Hub:')
        if at_hub:
            for package in at_hub:
                print(package)
            print()
        else:
            print('None\n')
        print('Loaded On Truck At Hub:')
        if loaded_on_truck:
            for package in loaded_on_truck:
                print(package)
            print()
        else:
            print('None\n')
        print('Out For Delivery:')
        if out_for_delivery:
            for package in out_for_delivery:
                print(package)
            print()
        else:
            print('None\n')
        print('Delivered:')
        if delivered:
            for package in delivered:
                print(package)
            print()
        else:
            print('None\n')

    def print_single_package_at_time(self, package_id: int, time_input: time):
        package = self.search(package_id)
        if package.time_checked_in > time_input:
            package.set_status(0)
        elif package.time_loaded_on_truck > time_input:
            package.set_status(1, f'Arrived at hub at {package.time_checked_in}')
        elif package.time_out_for_delivery > time_input:
            package.set_status(2, f'Loaded on truck {package.truck} at {package.time_loaded_on_truck}')
        elif package.time_delivered > time_input:
            package.set_status(2, f'Out for delivery on truck {package.truck} at '
                                  f'{package.time_out_for_delivery}')
        else:
            package.set_status(2, f'Delivered by truck {package.truck} at {package.time_delivered}')
        print(f'Status Of Package {package.package_id} As Of {time_input.strftime("%H:%M")}:')
        print(package)
