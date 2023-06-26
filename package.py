"""A module for managing packages.

This module contains classes for representing packages, storing them in a hashtable, and keeping track of a collection
of packages. This includes functionality for importing packages from a CSV file.
"""

import csv
import datetime
import copy
from typing import Optional, TYPE_CHECKING

import routing

if TYPE_CHECKING:
    from truck import Truck
    from datetime import time


class Package:
    """A class used to represent a package.

    Contains methods for tracking a package's status and modifying its attributes.

    Attributes:
        status_codes: (class attribute) Maps status codes to their corresponding descriptions.
        package_id: A unique identifier for a package.
        street: A street name and number.
        city: The city contained in the package's address.
        state: The state abbreviation contained in the package's address.
        zipcode: The zipcode contained in the package's address.
        deadline: The delivery deadline of the package.
        mass: The mass of the package in kilograms.
        notes: Notes concerning the package.
        truck_restriction: The ID of the truck the package must be loaded on.
        delivery_group: A number indicating that other packages with the same delivery group number are destined for
          the same address.
        priority: A number corresponding to the priority level of the package.
        status_code: A number representing the status of the package.
        status: A string stating the status of the package.
        ready_for_delivery: Indicates whether the package is ready for delivery.
        truck: Indicates the truck the package is loaded on.
        delivered_on_time: Indicates whether the package was delivered on time.
        time_checked_in: The time the package was checked in at the hub.
        time_loaded_on_truck: The time the package was loaded on the truck.
        time_out_for_delivery: The time the package was sent out for delivery.
        time_delivered: The time the package was delivered.
    """

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
        """Initializes Package.

        Args:
            package_id: A unique identifier for a package.
            address: A street number and name.
            city: The city contained in the package's address.
            state: The state abbreviation contained in the package's address.
            zipcode: The zipcode contained in the package's address.
            deadline: The delivery deadline of the package.
            mass: The mass of the package in kilograms.
            notes: Notes concerning the package.
            status_code: A number representing the status of the package.
        """

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
        self.delivered_on_time: Optional[bool] = None
        self.time_checked_in = None
        self.time_loaded_on_truck = None
        self.time_out_for_delivery = None
        self.time_delivered = None

    def __str__(self):
        """Returns a string with various attributes of the package.

        Returns: A string containing the package ID, city, state, zipcode, mass, notes, delivery deadline, and status.

        """

        return (f'ID: {self.package_id}, Address: {self.street}, City: {self.city}, State: {self.state}, '
                f'Zip: {self.zipcode}, Mass(kg): {self.mass}, Notes: {self.notes}, '
                f'Delivery Deadline: {self.deadline}, Status: {self.status}')

    @property
    def address(self):
        """Combines the street and zipcode of the package.

        Returns: A string containing the street number and name along with the zipcode.
        """

        return f'{self.street} {self.zipcode}'

    def update_address(self, street: str, city: str, state: str, zipcode: str):
        """Updates the address of the package.

        Args:
            street: The updated street number and name.
            city: The updated city.
            state: The abbreviation of the updated state.
            zipcode: The updated zipcode.
        """

        self.street = street.upper()
        self.city = city.upper()
        self.state = state.upper()
        self.zipcode = zipcode

    def set_truck_restriction(self, truck_id: int):
        """Sets the truck restriction attribute to the ID of the truck the package must be loaded on.

        Args:
            truck_id: The ID of the truck the package must be loaded on.
        """

        self.truck_restriction = truck_id

    def set_status(self, status_code: int, status: str = None):
        """Sets the status code and status description of the package.

        Args:
            status_code: A number representing the status of the package.
            status: A custom string that can replace the default status code description.
        """

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
        """Sets the delivery group of a package.

        Args:
            delivery_group: A number corresponding to a group that contains packages sharing the same address.
        """

        self.delivery_group = delivery_group

    def mark_package_checked_in(self, time_scanned: 'time'):
        """Sets the time the package was checked in.

        Args:
            time_scanned: The time the package was scanned at the hub.
        """

        self.time_checked_in = time_scanned

    def mark_package_loaded(self, truck: 'Truck'):
        """Sets the truck number the package was loaded on, the time it was loaded, and updates the package status.

        Args:
            truck: The truck the package was loaded on.
        """

        self.truck = truck.truck_id
        self.time_loaded_on_truck = truck.current_time
        self.set_status(2, f'Loaded on truck {truck.truck_id} at {self.time_loaded_on_truck}')

    def mark_package_out_for_delivery(self, truck: 'Truck'):
        """Sets the time the package was sent out for delivery and updates the status.

        Args:
            truck: The truck the package is out for delivery on.
        """

        self.time_out_for_delivery = truck.current_time
        self.set_status(3, f'Out for delivery on truck {truck.truck_id} at {self.time_out_for_delivery}')

    def mark_package_delivered(self, truck: 'Truck'):
        """Sets the time the package was delivered and updates the status.

        Args:
            truck: The truck that delivered the package.
        """

        self.time_delivered = truck.current_time
        if self.deadline != 'EOD':
            if self.time_delivered > self.deadline:
                self.delivered_on_time = False
            else:
                self.delivered_on_time = True
        else:
            self.delivered_on_time = True

        self.set_status(4, f'Delivered by truck {truck.truck_id} at {self.time_delivered}')


class Hashtable:
    """Implements a hashtable for storing package objects.

    The hashtable uses a chaining strategy to handle collisions. It provides lookup time of O(1) if there are no
    collisions. Collisions can be eliminated by correctly specifying the number of packages in the PackageCollection
    constructor if package IDs are contiguous. If no number is provided, the hashtable defaults to 40 buckets.

    Attributes:
        num_buckets: The number of buckets in the hashtable.
        table: The table that stores the packages.
    """

    def __init__(self, num_buckets: int = 40):
        """ Initializes the Hashtable.

        Args:
            num_buckets: The number of buckets to create in the hashtable. To optimize performance, package ID's should
              be contiguous and num_buckets should be set to the number of packages being imported.
        """

        self.num_buckets = num_buckets
        self.table: list[list[Optional[Package]]] = []
        for i in range(num_buckets):
            self.table.append([])

    def hash(self, package_id: int):
        """Calculates the hash value of a package ID.

        Args:
            package_id: The ID of the package being hashed.

        Returns: The hash value of the package ID.
        """

        return package_id % self.num_buckets

    def insert(self, package: Package):
        """Inserts a package into the hashtable.

        Args:
            package: The package to be inserted.

        Time complexity: O(n), where n is the number of packages in the hashtable. In the vast majority of instances,
        the actual time complexity will be O(1). O(n) is the worst case scenario where every package has the same hash
        value, which would only happen in instances where every package evaluated to the same hash value, which is
        unlikely to occur.

        Space complexity: O(1)
        """

        key = self.hash(package.package_id)
        i = 0
        while i < len(self.table[key]):
            # If a package already exists in the table with the same ID, call the update() method.
            if package.package_id == self.table[key][i].package_id:
                self.update(key, i, package)
                return
            i += 1
        self.table[key].append(package)

    def update(self, key: int, index: int, package: Package):
        """Replaces an existing package in the table if two package IDs are the same.

        Args:
            key: The hash value of the package.
            index: The index of the package in the bucket.
            package: The package to replace the existing package with.

        Time complexity: O(1)
        """

        self.table[key][index] = package

    def search(self, package_id: int) -> Optional[Package]:
        """Looks up a package in the hashtable by package ID.

        Args:
            package_id: The ID of the package to be found.

        Returns: The package corresponding to the package ID if it is in the table, None otherwise.

        Time complexity: O(n), where n is the number of packages in the hashtable. In the vast majority of instances,
        the actual time complexity will be O(1). O(n) is the worst case scenario where every package has the same hash
        value, which would only happen in instances where every package evaluated to the same hash value, which is
        unlikely to occur.
        """

        key = self.hash(package_id)
        for i in range(len(self.table[key])):
            package = self.table[key][i]
            if package.package_id == package_id:
                return package
        return None


class PackageCollection:
    """Class to manage a collection of packages.

    This class manages a collection of packages associated with a delivery hub.

    Attributes:
        package_table: A Hashtable object containing the packages associated with the collection.
        bound_packages: A set containing packages that are bound and must be loaded on the same truck at the same time.
        priority_1_packages: A set containing priority 1 packages, which are packages with a delivery deadline of 9:00.
        priority_2_packages: A set containing priority 2 packages, which are packages with a delivery deadline of 10:30.
    """

    def __init__(self, num_packages: Optional[int]):
        """Initializes a PackageCollection.

        Args:
            num_packages: The number of packages intended to be imported into the collection. Defaults to 40 if no
              argument is provided.
        """

        if num_packages:
            self.package_table = Hashtable(num_packages)
        else:
            self.package_table = Hashtable()
        self.bound_packages = set()
        self.priority_1_packages = set()
        self.priority_2_packages = set()

    def import_packages(self, file: str):
        """Imports packages from a given CSV file, creates Package objects, and stores them in a hashtable.

        Args:
            file: The path to the CSV file containing the package data.

        Time complexity: O(n log n), where n is the number of packages in the CSV file, due to the get_all_packages()
        method being called, which sorts the packages by package ID.

        Space complexity: O(n), where n is the number of packages in the CSV file.
        """

        with open(file, newline='') as packages:
            package_data = csv.reader(packages)
            next(package_data)
            for package in package_data:
                # Normalize package data.
                package_id = int(package[0])
                address = package[1].strip().upper()
                city = package[2].strip().upper()
                state = package[3].strip().upper()
                zipcode = package[4].strip()
                deadline = package[5].strip()
                if deadline != 'EOD':
                    deadline = datetime.datetime.strptime(deadline, '%I:%M %p').time()
                mass = float(package[6].strip())
                notes = package[7].strip()
                address = address.replace('NORTH', 'N')
                address = address.replace('EAST', 'E')
                address = address.replace('SOUTH', 'S')
                address = address.replace('WEST', 'W')
                new_package = Package(package_id, address, city, state, zipcode, deadline, mass, notes)
                self.package_table.insert(new_package)

            # Get all packages that were imported and calculate their delivery groups and priorities.
            packages = set(self.get_all_packages())
            routing.calculate_delivery_groups(packages)
            routing.calculate_delivery_priority(self, packages)

    def search(self, package_id: int):
        """Looks up a package in the table by package ID.

        Encapsulates the search function in the Hashtable class.

        Args:
            package_id: The ID of the package to be found.

        Returns: The package corresponding to the package ID if it is in the table, None otherwise.

        Time complexity: O(1) if the table is used as intended with num_buckets set to the number of packages imported
        and contiguous package ID's. O(n) otherwise, with n representing the number of packages in the table.
        """

        return self.package_table.search(package_id)

    def set_package_binding(self, package_ids: set[int]):
        """Adds packages corresponding to the provided package ID's to the package_binding set.

        This is used to specify packages that must be loaded and sent out for delivery on the same truck at the same
        time.

        Args:
            package_ids: The package IDs to be bound.
        """

        for i in package_ids:
            package = self.search(i)
            self.bound_packages.add(package)

    def get_all_packages(self) -> list[Package]:
        """Retrieves all packages from the collection and sorts them.

        Returns: A sorted list of all packages in the collection.

        Time complexity: O(n log n) where n is the number of packages in the collection, due to the implementation of
        the sort function.

        Space complexity: O(n), where n is the number of packages in the collection.
        """

        all_packages = []
        for bucket in self.package_table.table:
            for package in bucket:
                all_packages.append(package)

        # Sort the list in ascending order by package ID.
        all_packages.sort(key=lambda p: p.package_id)
        return all_packages

    def print_all_packages(self):
        """Prints all packages in the collection."""

        for package in self.get_all_packages():
            print(package)

    def print_all_packages_at_time(self, time_input: 'time'):
        """Prints all packages at a specific snapshot in time.

        Args:
            time_input: The time to use for creating the snapshot.

        Time complexity: O(n log n), where n is the number of packages in the collection, due to the get_all_packages
        method call, which sorts all packages by package ID.

        Space complexity: O(n), where n is the number of packages in the collection.
        """

        # Make a deep copy of the list the get_all_packages function returns. A deep copy is made to prevent the
        # original package data from being overwritten.
        all_packages = copy.deepcopy(self.get_all_packages())
        not_yet_arrived = []
        at_hub = []
        loaded_on_truck = []
        out_for_delivery = []
        delivered = []

        # Compare the time_input to the package's time attributes to determine what the package status was at
        # the time of time_input and update the status accordingly.
        for package in all_packages:
            if package.time_checked_in > time_input:
                package.set_status(0)
                not_yet_arrived.append(package)
            elif package.time_loaded_on_truck > time_input:
                package.set_status(1, f'Arrived at hub at {package.time_checked_in}')
                at_hub.append(package)
            elif package.time_out_for_delivery > time_input:
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

    def print_single_package_at_time(self, package_id: int, time_input: 'time'):
        """Prints the status of a single package at the specified time_input.

        Args:
            package_id: The ID of the package to be printed.
            time_input: The time to use for creating the snapshot.

        Time complexity: O(1)
        """

        package = copy.copy(self.search(package_id))  # Make a copy so the original object is not modified.
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
