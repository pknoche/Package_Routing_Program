"""A module for managing hub operations.

This module includes the Hub class, which represents a delivery hub. It is used to associate packages, addresses, and
trucks with a delivery hub and contains methods for hub-related operations, including checking in packages, loading
trucks, and generating reports.

Typical usage example:

    hub = Hub(package_file, address_file, distance_file, num_trucks, package_capacity_per_truck, average_truck_speed)
    hub.check_in_package(time_scanned, package_id)
    hub.load_trucks()
    hub.calculate_routes()
    hub.dispatch_trucks()
"""


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from package import Package
    from truck import Truck
    from datetime import time

import routing
import address as address_module
import package as package_module
import truck as truck_module


class Hub:
    """A delivery hub for managing packages, addresses, and trucks assigned to the hub."""
    def __init__(self, package_file: str, address_file: str, distance_file: str, num_packages: int, num_trucks: int,
                 package_capacity_per_truck: int, average_truck_speed: float):
        """Initializes Hub.
        Args:
            package_file: The path to the CSV file containing packages.
            address_file: The path to the CSV file containing addresses.
            distance_file: The path to the CSV file containing distances.
            num_packages: The number of packages in the package file.
            num_trucks: The number of operational trucks assigned to hub.
            package_capacity_per_truck: The number of packages each truck can hold.
            average_truck_speed: The average speed of the truck, including loading time and delivery time.

        Time complexity: O(n^3), where n is the number of items in the address file, due to the operations required
        to optimize the distance matrix.

        Space complexity: O(n^2), where n is the number of items in the address file, due to the space required to
        store the distance matrix, which is an n x n list.
        """

        #  Import data and assign to hub.
        self.packages = package_module.PackageCollection(num_packages)
        self.packages.import_packages(package_file)
        self.addresses = address_module.AddressCollection()
        self.addresses.import_addresses(address_file)
        self.addresses.import_distances(distance_file)
        self.trucks = truck_module.TruckCollection()
        self.packages_ready_for_dispatch = set()
        self.hub_address = self.addresses.hub_address

        #  Create number of Truck objects specified in constructor.
        for i in range(num_trucks):
            truck = truck_module.Truck((i + 1), package_capacity_per_truck, average_truck_speed, self)
            self.trucks.add_truck(truck)

    def check_in_package(self, time_scanned: 'time', package_id: int, status_override: int = None):
        """Checks in packages as they are scanned at the hub and updates their status.

        Args:
            time_scanned: The time the package was scanned.
            package_id: The ID of the package.
            status_override: Optional - overrides the default status code of the package.


        Time complexity: O(1) since a hashtable is used in the search function.

        Space complexity: O(1) since at most a single package can be added to the dispatch list.
        """

        package = self.packages.search(package_id)
        if status_override:
            package.set_status(status_override)
        elif self.addresses.address_is_valid(package.address):
            package.set_status(1)
            self.packages_ready_for_dispatch.add(package)
        else:
            package.set_status(5)
        package.mark_package_checked_in(time_scanned)

    def correct_package_address(self, package_id: int, street: str, city: str, state: str, zipcode: str):
        """Corrects a package's address and updates its status.

        Args:
            package_id: The package ID to be updated.
            street: The street number and name.
            city: The city name.
            state: The state abbreviation.
            zipcode: Zipcode.

        Time complexity: O(1) since a hashtable is used in the search function.
        """

        package = self.packages.search(package_id)
        package.update_address(street, city, state, zipcode)
        package.set_status(1)
        self.packages_ready_for_dispatch.add(package)

    def load_trucks(self):
        """Determines packages to be loaded onto trucks based on delivery priority and package constraints.


        Time complexity: O(n^2), where n is the number of packages being considered for loading, since nested for loops
        are utilized in the loading logic.

        Space complexity: O(n), where n is the number of packages to be loaded onto the truck.
        """

        for truck in self.trucks.all_trucks:
            # Call each method that determines packages to be loaded as long as the truck is ready for dispatch and
            # has capacity.
            if truck.is_at_hub and truck.is_ready_for_dispatch and truck.get_remaining_capacity() > 0:
                delivery_group_dict = routing.generate_delivery_group_dict(self.packages_ready_for_dispatch)
                self.load_priority_packages(truck, delivery_group_dict, priority_num=1)
                if truck.get_remaining_capacity() > 0:
                    self.load_priority_packages(truck, delivery_group_dict, priority_num=2)
                if truck.get_remaining_capacity() > 0:
                    self.load_group_packages(truck, self.packages_ready_for_dispatch, delivery_group_dict)
                if truck.get_remaining_capacity() > 0:
                    self.load_bound_packages(truck)
                if truck.get_remaining_capacity() > 0:
                    self.load_single_packages(truck)

                # Make a copy of the packages_on_truck set and use it to generate priority and standard manifests. A
                # copy is made so that it can be modified without affecting the set that is attached to the truck.
                packages_on_truck = truck.get_packages().copy()
                priority_manifest = routing.generate_priority_dict(packages_on_truck)
                # Remove packages that were added to the priority manifest so the remaining packages can be added to
                # the standard manifest.
                for address, packages in priority_manifest.items():
                    for package in packages:
                        packages_on_truck.remove(package)
                standard_manifest = routing.generate_address_dict(packages_on_truck)

                truck.set_priority_manifest(priority_manifest)
                truck.set_standard_manifest(standard_manifest)

    def load_priority_packages(self, truck: 'Truck', delivery_group_dict: dict[str, set['Package']], priority_num: int):
        """Considers packages with a delivery deadline for loading onto the truck.

        Args:
            truck: The truck being loaded.
            delivery_group_dict: A dictionary containing each address that has multiple packages destined for it.
            priority_num: 1 for packages with a deadline of 9:00, 2 for packages with a deadline of 10:30.

        Time complexity: O(n^2), where n is the number of packages being considered for loading, since nested for loops
        are used in the loading logic.

        Space complexity: O(n), where n is the number of packages to be loaded onto the truck.
        """

        # Determine which package group to pass into the load_group_packages method then remove any packages
        # loaded by that method from the priority packages set. If there are no priority packages, do nothing.
        priority_packages = None
        if priority_num == 1:
            priority_packages = self.packages.priority_1_packages
        elif priority_num == 2:
            priority_packages = self.packages.priority_2_packages
        if priority_packages:
            packages_loaded = self.load_group_packages(truck, priority_packages, delivery_group_dict)
            for package in packages_loaded:
                if package in priority_packages:
                    priority_packages.remove(package)

    #  "group" in the context of this function name refers to any type of package group,
    #  whether that be priority 1 packages, priority 2 packages, or packages assigned to a delivery group, which is
    #  defined in terms of an address when a package shares this address with one or more other packages.
    def load_group_packages(self, truck: 'Truck', package_group: set['Package'],
                            delivery_group_dict: dict[str, set['Package']]):
        """Considers a group of packages for loading onto the truck.

        "Group" in the context of this function name refers to any type of package group,
         whether that be priority 1 packages, priority 2 packages, or packages assigned to a delivery group, which
         indicates that an address has multiple packages destined for it.

        Args:
            truck: The truck being loaded.
            package_group: A set of packages to be considered for loading.
            delivery_group_dict: A dictionary containing each address that has multiple packages destined for it.

        Returns:
            A set containing the packages that were loaded.

        Time complexity: O(n^2), where n is the number of packages being considered for loading, since nested for loops
        are used in the loading logic.

        Space complexity: O(n), where n is the number of packages being loaded onto the truck.
        """

        # Initialize a set to keep track of all packages that were loaded in this iteration.
        packages_loaded = set()

        # Initialize a dictionary to keep track of addresses of bound packages that were loaded.
        bound_packages_loaded_addresses = {}

        # Determine if any packages in the group that was passed in are priority packages that are not part of a
        # delivery group and not bound to other packages. If this is the case, load those packages unless they do not
        # have a ready for delivery status code or are restricted to a truck that is not the current truck being loaded.
        for package in package_group:
            if package.priority and package.status_code == 1 and not package.delivery_group and \
                    package not in self.packages.bound_packages:
                if package.truck_restriction and package.truck_restriction != truck.truck_id:
                    continue
                truck.load_package(package)
                packages_loaded.add(package)

        # Sort the addresses in the delivery groups from smallest to largest according to the number of packages
        # assigned to each one. This is done to maximize the chance that there is room on a truck for the entire
        # delivery group.
        sorted_delivery_group_keys_by_size = sorted(delivery_group_dict, key=lambda x: len(delivery_group_dict[x]))

        # Determine if any package in the delivery group is restricted from loading on the current truck, or if none of
        # the packages in the delivery group are in the package group that was passed in.
        # If either of these conditions are true, skip the entire delivery group in this iteration.
        for delivery_group_key in sorted_delivery_group_keys_by_size:
            if any(package.truck_restriction and package.truck_restriction != truck.truck_id for package in
                   delivery_group_dict[delivery_group_key]):
                continue
            if all(package not in package_group for package in delivery_group_dict[delivery_group_key]):
                continue

            for package in delivery_group_dict[delivery_group_key]:
                # If a package is bound, check to see if there is room on the truck for all the bound packages.
                # If there is, load all bound packages onto the truck. While doing this, check the address of each
                # of the bound packages to see if the address has a delivery group associated with it. If it is,
                # add the address and the package to a dictionary.
                if package in self.packages.bound_packages:
                    bound_packages = self.packages.bound_packages
                    if len(bound_packages) <= truck.get_remaining_capacity():
                        for bound_package in bound_packages:
                            truck.load_package(bound_package)
                            packages_loaded.add(bound_package)
                            package_address = bound_package.address
                            if package_address in delivery_group_dict:
                                if package_address not in bound_packages_loaded_addresses:
                                    bound_packages_loaded_addresses[package_address] = []
                                    bound_packages_loaded_addresses[package_address].append(bound_package)
                                else:
                                    bound_packages_loaded_addresses[package_address].append(bound_package)

                    # If there are items in the dictionary from the steps above, check each address in the dictionary
                    # to see if there is room left on the truck for all the remaining packages in that delivery group.
                    # If there is, load those onto the truck.
                    if bound_packages_loaded_addresses:
                        for address in bound_packages_loaded_addresses:
                            num_packages = len(bound_packages_loaded_addresses[address])
                            if len(delivery_group_dict.get(address)) - num_packages <= truck.get_remaining_capacity():
                                for grouped_package in delivery_group_dict.get(address):
                                    truck.load_package(grouped_package)
                                    packages_loaded.add(grouped_package)

                # If the package is not bound, check to see if there is room for all other packages in its delivery
                # group on the truck. If there is, load each package from that delivery group.
                else:
                    if package.delivery_group and len(
                            delivery_group_dict[package.address]) <= truck.get_remaining_capacity():
                        delivery_group = delivery_group_dict.get(package.address)
                        for grouped_package in delivery_group:
                            truck.load_package(grouped_package)
                            packages_loaded.add(grouped_package)

        # Call the function that removes loaded packages from the dispatch list and delivery group dictionary.
        self.remove_from_dispatch_list(packages_loaded, delivery_group_dict)

        return packages_loaded

    def load_bound_packages(self, truck: 'Truck'):
        """Considers bound packages for loading.

        Bound packages are packages which must be loaded on the same truck at the same time.

        Args:
            truck: The truck being loaded.

        Time complexity: O(n), where n is the number of packages being considered for loading.

        Space complexity: O(n), where n is the number of packages being loaded onto the truck.
        """
        bound_packages_loaded = set()
        bound_packages = self.packages.bound_packages
        if len(bound_packages) > truck.get_remaining_capacity():
            return
        for package in bound_packages:
            if package.truck_restriction and package.truck_restriction != truck.truck_id or \
                    package not in self.packages_ready_for_dispatch:
                return
        for package in bound_packages:
            truck.load_package(package)
            bound_packages_loaded.add(package)
        self.remove_from_dispatch_list(bound_packages_loaded)

    def load_single_packages(self, truck: 'Truck'):
        """ Considers single packages for loading.

        Single packages are packages whose address only has one package destined for it.

        Args:
            truck: The truck being loaded.

        Time complexity: O(n), where n is the number of packages being considered for loading.

        Space complexity: O(n), where n is the number of packages being loaded onto the truck.
        """

        single_packages = routing.generate_single_package_delivery_set(self.packages_ready_for_dispatch)
        packages_loaded = set()
        while truck.get_remaining_capacity() > 0 and len(single_packages) > 0:
            package = next(iter(single_packages))
            if package.truck_restriction:
                if package.truck_restriction != truck.truck_id:
                    single_packages.remove(package)
                    continue
            truck.load_package(package)
            packages_loaded.add(package)
            single_packages.remove(package)
        self.remove_from_dispatch_list(packages_loaded)

    def remove_from_dispatch_list(self, packages: set['Package'],
                                  delivery_group_dict: dict[str, set['Package']] = None):
        """ Removes packages from the data structures that track packages that are eligible for loading.

        Args:
            packages: A set of packages to be removed from data structures.
            delivery_group_dict: A dictionary containing addresses that have multiple packages destined for them.

        Time complexity: O(n), where n is the number of packages to be removed.
        """

        # Remove packages from the ready for dispatch set and from the delivery group dictionary if present.
        for package in packages:
            self.packages_ready_for_dispatch.remove(package)
            address = package.address
            if not delivery_group_dict:
                continue
            if address in delivery_group_dict:
                packages = delivery_group_dict.get(address)
                if package in packages:
                    packages.remove(package)

    def calculate_routes(self):
        """Calculates routes for all trucks that have been loaded. Uses heuristic methods for optimizing routes.

        Time complexity: O(n^2), where n is the number of unique addresses of the packages loaded on the truck. This is
        due to the use of the two-opt algorithm.

        Space complexity: O(n), where n is the number of unique addresses of the packages loaded on the truck.
        """
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.is_ready_for_dispatch:
                routing.calculate_route(self, truck)

    def dispatch_trucks(self):
        """Dispatches trucks to deliver packages.

        Time complexity: O(n), where n is the number of packages on the truck.
        """
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub and truck.is_ready_for_dispatch:
                truck.begin_route()

    def print_end_of_day_report(self):
        """Prints a report showing the history of all trucks and the status of all packages at the end of the day.

        Time complexity: O(n), where n is the number of packages that have been imported.

        Space complexity: O(n), where n is the number of packages that have been imported, since any packages that
        were delivered late or not delivered will be added to a new list.
        """
        print('Truck Report:\n')
        total_miles_traveled = 0
        for truck in self.trucks.all_trucks:
            print(f'Truck {truck.get_truck_id()}:')
            for entry in truck.travel_log:
                print(entry)
            total_miles_traveled += truck.get_miles_traveled()
            print(f'Total distance traveled by truck {truck.get_truck_id()} today: '
                  f'{truck.get_miles_traveled():.1f} miles.\n')
        print(f'\nTotal distance traveled by all trucks today: {total_miles_traveled:.1f} miles.\n\n')

        print('Package Report:\n')
        not_delivered = []
        late_deliveries = []
        for package in self.packages.get_all_packages():
            print(package)
            if package.status_code != 4:
                not_delivered.append(package)
                continue
            if not package.delivered_on_time:
                late_deliveries.append(package)
        print()
        if not not_delivered and not late_deliveries:
            print('All packages were delivered on time!')
        else:
            print('The following packages were not delivered on time:\n')
        if not_delivered:
            print('Not Delivered:')
            for package in not_delivered:
                print(package)
            print()
        if late_deliveries:
            print('Late Deliveries:')
            for package in late_deliveries:
                print(package)
