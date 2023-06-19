import itertools

from address import Address
from package import Package
from typing import TYPE_CHECKING

from truck import Truck

if TYPE_CHECKING:
    from hub import Hub


def generate_address_list(package_list: list[Package]) -> dict[str, list[Package]]:
    packages_by_address = {}
    for package in package_list:
        address = package.get_address()
        if address in packages_by_address:
            packages_by_address[address].append(package)
        else:
            packages_by_address[address] = [package]
    return packages_by_address


def calculate_delivery_groups(package_list: list[Package]):
    delivery_group = 0
    packages_by_address = generate_address_list(package_list)
    for address, packages in packages_by_address.items():
        if len(packages) > 1:
            delivery_group += 1
            for package in packages:
                package.delivery_group = delivery_group


def calculate_delivery_priority(package_list: list[Package]):
    for package in package_list:
        if package.deadline == '9:00 AM':
            package.priority = 1
        elif package.deadline == '10:30 AM':
            package.priority = 2


def calculate_priority_list(package_list: list[Package]) -> dict[str, list[Package]]:
    priority_list = []
    delivery_groups = []
    for package in package_list:
        if package.priority:
            priority_list.append(package)
        if package.delivery_group and package.delivery_group not in delivery_groups:
            delivery_groups.append(package.delivery_group)
    for package in package_list:
        if package.delivery_group in delivery_groups and package not in priority_list:
            priority_list.append(package)
    return generate_address_list(priority_list)


def calculate_delivery_group_list(package_list: list[Package]) -> dict[Address, list[Package]]:
    all_address_list = generate_address_list(package_list)
    delivery_group_list = {address: packages for address, packages in all_address_list.items() if len(packages) > 1}
    return delivery_group_list


def nearest_neighbor(hub: 'Hub', truck: Truck):
    priority_addresses = list(truck.priority_package_manifest.keys())
    current_address = truck.current_address
    priority_route = [current_address]
    standard_addresses = list(truck.standard_package_manifest.keys())
    standard_route = None
    nearest_address = None
    min_distance = float('inf')
    while priority_addresses:
        for address in priority_addresses:
            distance = hub.addresses.distance_between(current_address, address)
            if distance < min_distance:
                min_distance = distance
                nearest_address = address
        priority_route.append(nearest_address)
        current_address = nearest_address
        priority_addresses.remove(current_address)
        min_distance = float('inf')
    standard_route = [current_address]
    while standard_addresses:
        for address in standard_addresses:
            distance = hub.addresses.distance_between(current_address, address)
            if distance < min_distance:
                min_distance = distance
                nearest_address = address
        standard_route.append(nearest_address)
        current_address = nearest_address
        standard_addresses.remove(current_address)
        min_distance = float('inf')
    standard_route.append(hub.addresses.get_hub_address())
    truck.set_priority_route(priority_route)
    truck.set_standard_route(standard_route)


def two_opt_priority(hub: 'Hub', truck: Truck):
    num_swaps = 0
    route = truck.priority_route[:]
    lowest_distance = calculate_route_distance(hub, route)
    improvement = True
    while improvement:
        improvement = False
        for swap_first in range(1, len(route)):  # This range prevents swapping of first element of route,
            # which is the truck's current address.
            for swap_last in range(swap_first + 1, len(route)):
                new_route = route[:]
                new_route[swap_first:swap_last + 1] = reversed(route[swap_first:swap_last + 1])  # + 1 is used so
                # that the reversed call is inclusive of the swap_last element.
                new_distance = calculate_route_distance(hub, new_route)
                num_swaps += 1
                if new_distance < lowest_distance:
                    route = new_route
                    lowest_distance = new_distance
                    improvement = True
    print(f'Number of swaps performed: {num_swaps}')  # TODO - remove print statement
    truck.set_priority_route(route)


def two_opt_standard(hub: 'Hub', truck: Truck):
    num_swaps = 0
    route = truck.standard_route[:]
    lowest_distance = calculate_route_distance(hub, route)
    improvement = True
    while improvement:
        improvement = False
        for swap_first in range(1, len(route) - 1):  # This range prevents swapping of first and last elements of
            # route, which are current address and shipping hub.
            for swap_last in range(swap_first + 1, len(route) - 1):
                new_route = route[:]
                new_route[swap_first:swap_last + 1] = reversed(route[swap_first:swap_last + 1])  # + 1 is used so
                # that the reversed call is inclusive of the swap_last element.
                new_distance = calculate_route_distance(hub, new_route)
                num_swaps += 1
                if new_distance < lowest_distance:
                    route = new_route
                    lowest_distance = new_distance
                    improvement = True
    print(f'Number of swaps performed: {num_swaps}')  # TODO - remove print statement
    truck.set_standard_route(route)


def calculate_route_distance(hub: 'Hub', route: list[str]) -> float:
    distance = sum(hub.addresses.distance_between(route[i], route[i + 1])
                   for i in range(len(route) - 1))
    return distance


def calculate_route(hub: 'Hub', truck: Truck):
    nearest_neighbor(hub, truck)
    two_opt_priority(hub, truck)
    two_opt_standard(hub, truck)
