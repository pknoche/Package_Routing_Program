from address import Address
from package import Package


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
