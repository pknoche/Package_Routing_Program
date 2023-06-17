from address import Address
from package import Package
from typing import TYPE_CHECKING

from truck import Truck

if TYPE_CHECKING:
    from hub import Hub


def generate_address_list(package_list: list[Package]) -> dict[Address, list[Package]]:
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


def calculate_priority_list(package_list: list[Package]) -> dict[Address, list[Package]]:
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


def calculate_initial_route(hub: 'Hub', truck: Truck) -> tuple[list[Address], float]:
    priority_addresses = list(truck.priority_package_manifest.keys())
    route = []
    standard_addresses = list(truck.standard_package_manifest.keys())
    current_address = truck.current_address
    nearest_address = None
    min_distance = float('inf')
    total_distance = 0
    while priority_addresses:
        for address in priority_addresses:
            distance = hub.addresses.distance_between(current_address, address)
            if distance < min_distance:
                min_distance = distance
                nearest_address = address
        route.append(nearest_address)
        total_distance += min_distance
        current_address = nearest_address
        priority_addresses.remove(current_address)
        min_distance = float('inf')
    while standard_addresses:
        for address in standard_addresses:
            distance = hub.addresses.distance_between(current_address, address)
            if distance < min_distance:
                min_distance = distance
                nearest_address = address
        route.append(nearest_address)
        total_distance += min_distance
        current_address = nearest_address
        standard_addresses.remove(current_address)
        min_distance = float('inf')
    return route, total_distance
