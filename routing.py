import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hub import Hub
    from package import Package, PackageCollection
    from truck import Truck


def generate_address_dict(packages: set['Package']) -> dict[str, set['Package']]:
    """Generates a dictionary containing addresses and their associated packages.

    Groups packages by delivery address into sets.

    Args:
        packages: The packages to generate the dictionary for.

    Returns: A dictionary containing strings of addresses as keys and their associated packages as values.

    Time complexity: O(n), where n is the number of packages being passed in.

    Space complexity: O(n), where n is the number of packages being passed in.
    """

    packages_by_address = {}
    for package in packages:
        address = package.address
        if address in packages_by_address:
            packages_by_address[address].add(package)
        else:
            packages_by_address[address] = {package}
    return packages_by_address


def calculate_delivery_groups(packages: set['Package']):
    """Assign group numbers to packages that share an address with one or more other packages.

    Args:
        packages: The packages to evaluate.

    Time complexity: O(n), where n is the number of packages being evaluated.
    """

    delivery_group = 0
    packages_by_address = generate_address_dict(packages)
    for address, packages in packages_by_address.items():
        if len(packages) > 1:
            delivery_group += 1
            for package in packages:
                package.set_delivery_group(delivery_group)


def calculate_delivery_priority(package_collection: 'PackageCollection', packages: set['Package']):
    """Calculates the priority number for packages with a deadline and adds them to a set in the package collection.

    Args:
        package_collection: The package collection that the packages are contained in.
        packages: The packages to evaluate.

    Time complexity: O(n), where n is the number of packages being evaluated.

    Space complexity: O(n), where n is the number of packages being evaluated.
    """

    for package in packages:
        if package.deadline == datetime.time(hour=9, minute=0):
            package.priority = 1
            package_collection.priority_1_packages.add(package)
        elif package.deadline == datetime.time(hour=10, minute=30):
            package.priority = 2
            package_collection.priority_2_packages.add(package)


def generate_priority_dict(packages: set['Package']) -> dict[str, set['Package']]:
    """Generates a dictionary with addresses that have priority packages as strings and lists of packages as keys.

    Adds all packages with priority numbers to the dictionary and also adds non-priority packages sharing the same
    address.

    Args:
        packages: The packages to evaluate.

    Returns:
        A dictionary with address strings that have assigned priority packages as keys, and sets of packages as values.

    Time complexity: O(n), where n is the number of packages being evaluated.

    Space complexity: O(n), where n is the number of packages being evaluated.
    """

    priority_packages = set()
    delivery_groups = set()
    for package in packages:
        if package.priority:
            priority_packages.add(package)
        if package.delivery_group and package.delivery_group not in delivery_groups:
            delivery_groups.add(package.delivery_group)

    # Determine if any non-priority packages share the same address with priority packages, and if so, add them to the
    # dictionary.
    for package in packages:
        if priority_packages and package.delivery_group in delivery_groups and package not in priority_packages:
            priority_packages.add(package)

    return generate_address_dict(priority_packages)


def generate_delivery_group_dict(packages: set['Package']) -> dict[str, set['Package']]:
    """Generates a dictionary containing all delivery groups and their associated packages.

    Args:
        packages: The packages to be evaluated.

    Returns: A dictionary with address strings containing one or more packages as keys and sets of packages
      associated with those addresses as values.

    Time complexity: O(n), where n is the number of packages being evaluated.

    Space complexity: O(n), where n is the number of packages being evaluated.
    """

    all_address_dict = generate_address_dict(packages)
    delivery_group_dict = {address: packages for address, packages in all_address_dict.items() if len(packages) > 1}
    return delivery_group_dict


def generate_single_package_delivery_set(packages: set['Package']) -> set['Package']:
    """Generates a set of packages for addresses that have only one package assigned to them.

    Args:
        packages: The packages to be evaluated.

    Returns: A set containing packages that are destined for addresses that only have one package assigned to them.

    Time complexity: O(n), where n is the number of packages being evaluated.

    Space complexity: O(n), where n is the number of packages being evaluated.
    """

    all_address_dict = generate_address_dict(packages)
    single_addresses = set()
    for packages in all_address_dict.values():
        if len(packages) == 1:
            single_addresses.add(next(iter(packages)))
    return single_addresses


def floyd_warshall(distance_matrix: list[list[float]]):
    """Calculates the distance of the shortest possible path between two addresses.

    Optimizes the distance matrix by replacing the direct distance between two addresses with the shortest possible
    path distance that may travel through other addresses.

    Args:
        distance_matrix: The distance matrix to be optimized.

    Returns: The optimized distance matrix.


    Time complexity: O(n^3), where n is the number of vertices contained in the distance matrix, due to the nested
      for loop structure, each of which runs through all the vertices three times.

    Space complexity: O(n^2), where n is the number of vertices contained in the distance matrix, since the
      returned matrix is of size n x n.
    """

    num_vertices = len(distance_matrix)
    for k in range(num_vertices):
        for i in range(num_vertices):
            for j in range(num_vertices):
                # Determine if the distance from i to j, or i to k to j, is shorter and replace the original distance
                # in the matrix with this value.
                distance_matrix[i][j] = min(distance_matrix[i][j], distance_matrix[i][k] + distance_matrix[k][j])
    return distance_matrix


def nearest_neighbor(truck: 'Truck'):
    """Optimizes the distance of a route by continuously finding the next closest address and appending it to a list.

    This implementation of the nearest neighbor algorithm considers addresses containing priority addresses first,
    separately optimizes the route containing non-priority addresses, and then appends these routes together. This
    ensures that priority packages are delivered first in the route, even though it may not provide as short a route
    as if all the addresses were considered as one group.

    Args:
        truck: The truck that the route is being calculated for.

    Time complexity: O(n), where n is the number of addresses in the route.

    Space complexity: O(n), where n is the number of addresses in the route.
    """

    priority_addresses = list(truck.priority_package_manifest.keys())
    current_address = truck.current_address
    priority_route = [current_address]
    standard_addresses = list(truck.standard_package_manifest.keys())
    nearest_address = None
    min_distance = float('inf')  # Initialize min_distance with infinity.

    # If the truck has priority 1 packages, add their addresses to the route first and do not consider these
    # addresses for optimization.
    if truck.priority_1_addresses:
        for address in truck.priority_1_addresses:
            priority_route.append(address)
            priority_addresses.remove(address)

    # Calculate the address closest to the truck's current address and append it to the route.
    while priority_addresses:
        for address in priority_addresses:
            distance = truck.hub.addresses.distance_between(current_address, address)
            if distance < min_distance:
                min_distance = distance
                nearest_address = address
        priority_route.append(nearest_address)
        current_address = nearest_address
        priority_addresses.remove(current_address)
        min_distance = float('inf')

    # Repeat the step from above with addresses that do not have priority packages.
    standard_route = [current_address]
    while standard_addresses:
        for address in standard_addresses:
            distance = truck.hub.addresses.distance_between(current_address, address)
            if distance < min_distance:
                min_distance = distance
                nearest_address = address
        standard_route.append(nearest_address)
        current_address = nearest_address
        standard_addresses.remove(current_address)
        min_distance = float('inf')

    # Add the hub's address to the end of the route and assign the routes to the truck.
    standard_route.append(truck.hub.addresses.hub_address)
    truck.priority_route = priority_route
    truck.standard_route = standard_route


def two_opt_priority(truck: 'Truck'):
    """Optimizes the distance of a route by iterating through pairs of addresses in a route and swapping them.

    After swapping a pair of edges, the algorithm calculates the new distance and keeps the new route if it is shorter.
    It continues this process until it is unable to find a shorter route after an iteration. This implementation of the
    two opt algorithm considers only the priority addresses in a truck's route, and ensures that addresses that have
    priority 1 addresses are placed first in the route.

    Args:
        truck: The truck that the route is being optimized for.

    Time complexity: O(n^3), where n is the number of addresses in the route. This is because even though the
    nested for loop performs n^2 operations in each iteration, it may iterate x times as long as it finds improvement.
    With this said, the algorithm will often complete in closer to O(n^2), since it stops as soon as it does not find
    an improved route after an iteration.

    Space complexity: O(n), where n is the number of addresses in the route.
    """

    num_priority_1_addresses = len(truck.priority_1_addresses)
    route = truck.priority_route[:]
    lowest_distance = calculate_route_distance(truck.hub, route)
    improvement = True
    while improvement:
        improvement = False
        # Only swap addresses that do not contain the hub address, which is the first address in the route, or the
        # priority 1 addresses, which are the addresses immediately following the hub address.
        for swap_first in range(1 + num_priority_1_addresses, len(route)):
            for swap_last in range(swap_first + 1, len(route)):
                new_route = route[:]
                # swap_last + 1 is used so that the reversed call is inclusive of the swap_last element.
                new_route[swap_first:swap_last + 1] = reversed(route[swap_first:swap_last + 1])
                new_distance = calculate_route_distance(truck.hub, new_route)
                if new_distance < lowest_distance:
                    route = new_route
                    lowest_distance = new_distance
                    improvement = True
    truck.priority_route = route


def two_opt_standard(truck: 'Truck'):
    """Optimizes the distance of a route by iterating through pairs of addresses in a route and swapping them.

    After swapping a pair of edges, the algorithm calculates the new distance and keeps the new route if it is shorter.
    It continues this process until it is unable to find a shorter route after an iteration. This implementation of the
    two opt algorithm considers only the non-priority addresses in a truck's route.

    Args:
        truck: The truck that the route is being optimized for.

    Time complexity: O(n^3), where n is the number of addresses in the route. This is because even though the
    nested for loop performs n^2 operations in each iteration, it may iterate x times as long as it finds improvement.
    With this said, the algorithm will often complete in closer to O(n^2), since it stops as soon as it does not find
    an improved route after an iteration.

    Space complexity: O(n), where n is the number of addresses in the route.
    """

    route = truck.standard_route[:]
    lowest_distance = calculate_route_distance(truck.hub, route)
    improvement = True
    while improvement:
        improvement = False
        # This range prevents swapping of first and last elements of the route, which are current address and
        # shipping hub.
        for swap_first in range(1, len(route) - 1):
            for swap_last in range(swap_first + 1, len(route) - 1):
                new_route = route[:]
                # swap_last + 1 is used so that the reversed call is inclusive of the swap_last element.
                new_route[swap_first:swap_last + 1] = reversed(route[swap_first:swap_last + 1])
                new_distance = calculate_route_distance(truck.hub, new_route)
                if new_distance < lowest_distance:
                    route = new_route
                    lowest_distance = new_distance
                    improvement = True
    truck.standard_route = route


def calculate_route_distance(hub: 'Hub', route: list[str]) -> float:
    """Calculates the total route distance by looking up and summing the distance between each address.

    Args:
        hub: The hub that the addresses are assigned to.
        route: The route being calculated.

    Returns: The distance of the entire route.

    Time complexity: O(n), where n is the number of addresses in the route.
    """

    distance = sum(hub.addresses.distance_between(route[i], route[i + 1]) for i in range(len(route) - 1))
    return distance


def calculate_route(truck: 'Truck'):
    """Uses the nearest_neighbor and two-opt algorithms to optimize the distance of the route.

    Args:
        truck: The truck the route is being calculated for.

    Time complexity: O(n^3), where n is the number of addresses in the route. This is due to the two-opt algorithm
    having a worst-case time complexity of O(n^3). This said, the average time complexity is much closer to O(n^2),
    since the two-opt algorithm stops looping once an improvement is not found after an iteration. Since nearest
    neighbor is used to optimize the route before passing it in to two opt, the starting route that two opt receives
    is closer to optimal than a random route, meaning it is more likely to reach its loop termination condition sooner.

    Space complexity: O(n), where n is the number of addresses in the route.
    """

    nearest_neighbor(truck)
    two_opt_priority(truck)
    two_opt_standard(truck)
