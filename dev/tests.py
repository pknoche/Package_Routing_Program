"""This module contains functions used to test the internal workings of the program and is used only in development."""

from typing import TYPE_CHECKING

import routing

if TYPE_CHECKING:
    from hub import Hub


def print_package_manifests(hub: 'Hub'):
    """Prints the package manifest for each truck after it is loaded.

    To use this function, it can be called after calculate_routes is called in main.

    Args:
        hub: The hub to print the manifests for.
    """

    # print number of packages on each truck
    print('Package Manifests:')
    for i in range(len(hub.trucks.all_trucks)):
        truck = hub.trucks.all_trucks[i]
        print(f'The number of packages on truck {truck.truck_id} is {truck.num_packages_loaded}.')
    print()

    # print manifests for each truck
    for truck in hub.trucks.all_trucks:
        print(f'Truck number {truck.truck_id}:')
        print('Priority Manifest:')
        for address, packages in truck.priority_package_manifest.items():
            print(f'Address: {address}')
            for package in packages:
                print(package)
            print()
        print()
        print('Standard Manifest:')
        for address, packages in truck.standard_package_manifest.items():
            print(f'Address: {address}')
            for package in packages:
                print(package)
        print('\n\n')


def print_all_addresses(hub: 'Hub'):
    """Prints all addresses associated with the hub.

    Args:
        hub: The hub to print the addresses for.
    """

    print('All Streets:')
    for street in hub.addresses.all_addresses:
        print(street)
    print('\n')


def print_distance_matrix(hub: 'Hub'):
    """Prints the distance matrix associated with the hub.

    Args:
        hub: The hub to print the distance matrix for.
    """

    print('Distance Matrix:')
    for distance_list in hub.addresses.distance_matrix:
        rounded_list = [round(distance, 1) for distance in distance_list]
        print(rounded_list)
    print('\n')


def print_all_packages(hub: 'Hub'):
    """Prints all packages associated with the hub.

    Args:
        hub: The hub to print the packages for.
    """

    print('Status of all packages:')
    hub.packages.print_all_packages()
    print('\n')


def print_hashtable(hub: 'Hub'):
    """Prints the package hashtable for the hub.

    Args:
        hub: The hub to print the hashtable for.
    """

    print('Package Hashtable:')
    i = 0
    for table in hub.packages.package_table.table:
        print(f'{i} ', end='')
        print(table)
        i += 1
    print('\n')


def print_packages_by_delivery_groups(hub: 'Hub'):
    """Prints all delivery group addresses and their associated packages.

    Args:
        hub: The hub to print the delivery groups for.
    """

    delivery_groups = {}
    for package in hub.packages.get_all_packages():
        group_number = package.delivery_group
        if group_number in delivery_groups:
            delivery_groups[group_number].append(package)
        else:
            delivery_groups[group_number] = [package]

    for delivery_group, packages in delivery_groups.items():
        print(f'Delivery Group {delivery_group}:')
        for package in packages:
            print(package)
        print()
    print('\n')


def print_routes(hub: 'Hub'):
    """Prints routes for all trucks.

    To use this function, it should be called after the for loop from calculate_routes method in the hub file
    ("tests.print_routes(self)")

    Args:
        hub: The hub to print routes for.
    """

    for truck in hub.trucks.all_trucks:
        print(
            f'Truck {truck.truck_id} priority route: {truck.priority_route}\n'
            f'Distance: {routing.calculate_route_distance(hub, truck.priority_route):.1f} miles')
        j = 0
        for i in range(len(truck.priority_route) - 1):
            print(
                f'The distance between {str(truck.priority_route[j])} and {str(truck.priority_route[j + 1])} is '
                f'{hub.addresses.distance_between(truck.priority_route[j], truck.priority_route[j + 1])}')
            j += 1
        j = 0
        print(f'Truck {truck.truck_id} standard route: {truck.standard_route}\n'
              f'Distance: {routing.calculate_route_distance(hub, truck.standard_route):.1f} miles')
        for i in range(len(truck.standard_route) - 1):
            print(
                f'The distance between {str(truck.standard_route[j])} and {str(truck.standard_route[j + 1])} is '
                f'{hub.addresses.distance_between(truck.standard_route[j], truck.standard_route[j + 1]):.1f}')
            j += 1
        print('\n')


def calculate_on_time_delivery(hub: 'Hub'):
    """Prints whether all packages were delivered on time or if some were late.

    Args:
        hub: The hub to make the calculation for.
    """

    for package in hub.packages.get_all_packages():
        if package.deadline == 'EOD':
            if package.status_code == 4:
                package.delivered_on_time = True
        else:
            deadline = package.deadline
            if package.time_delivered:
                if deadline < package.time_delivered:
                    package.delivered_on_time = False
                else:
                    package.delivered_on_time = True
    all_on_time = True
    for package in hub.packages.get_all_packages():
        if not package.delivered_on_time:
            all_on_time = False
            break
    if all_on_time:
        print('All packages were delivered on time!')
    elif not all_on_time:
        print('Some packages were delivered late.')
    print('\n')


def print_bound_packages(hub: 'Hub'):
    """Prints the status of all bound packages.

    Used to easily see if bound packages were delivered by the same truck on the same route.

    Args:
        hub: The hub to print the packages for.
    """

    print('Bound Packages:')
    for package in hub.packages.bound_packages:
        print(package)
    print('\n')


def print_all_tests(hub: 'Hub'):
    """Prints all tests except print_package_manifests and print_routes, which must be called from elsewhere.

    Args:
        hub: The hub to print the tests for.
    """

    print_hashtable(hub)
    print_distance_matrix(hub)
    print_all_addresses(hub)
    print_bound_packages(hub)
    print_packages_by_delivery_groups(hub)
    print_all_packages(hub)
    calculate_on_time_delivery(hub)
    print('\n')
