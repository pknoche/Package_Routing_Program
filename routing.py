from package import Package


def calculate_delivery_groups(package_list: list[Package]):
    for package in package_list:
        package.delivery_group = None  # Reset delivery groups in case they have been calculated previously.
    packages_by_address = {}
    delivery_group = 0
    for package in package_list:
        address = package.address
        if address in packages_by_address:
            packages_by_address[address].append(package)
        else:
            packages_by_address[address] = [package]
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
