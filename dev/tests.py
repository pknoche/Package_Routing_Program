def print_package_manifests(hub):
    # print number of packages on each truck
    print('Package Manifests:')
    for i in range(len(hub.trucks.all_trucks)):
        truck = hub.trucks.all_trucks[i]
        print(f'The number of packages on truck {truck.truck_id} is {truck.get_num_packages_loaded()}.')
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


def print_all_streets(hub):
    print('All Streets:')
    for street in hub.addresses.all_addresses:
        print(street)
    print('\n\n')


def test_distance_function(hub):
    print('Distance test - should be 10.9:')
    print(hub.addresses.distance_between(hub.addresses.get_hub_address(), '2010 W 500 S 84104'))
    print('\n\n')


def print_adjacency_matrix(hub):
    print('Adjacency Matrix:')
    for distance_list in hub.addresses.adjacency_matrix:
        print(distance_list)
    print('\n\n')


def print_all_packages(hub):
    print('Status of all packages:')
    hub.packages.package_table.print_all_packages()
    print('\n\n')


def print_hash_table(hub):
    print('Package Hashtable:')
    i = 0
    for table in hub.packages.package_table.table:
        print(f'{i} ', end='')
        print(table)
        i += 1
    print()


def print_initial_routes(hub):
    for truck in hub.trucks.all_trucks:
        print(f'Truck {truck.truck_id} route: {truck.route}\nDistance: {truck.initial_route_distance}')
        print(f'The distance between {hub.addresses.get_hub_address()} and {str(truck.route[0])} is '
              f'{hub.addresses.distance_between(hub.addresses.get_hub_address(), str(truck.route[0]))}')
        j = 0
        for i in range(len(truck.route) - 1):
            print(
                f'The distance between {str(truck.route[j])} and {str(truck.route[j + 1])} is '
                f'{hub.addresses.distance_between(str(truck.route[j]), str(truck.route[j + 1]))}')
            i += 1
            j += 1
        print()


def print_all_tests(hub):
    print_package_manifests(hub)
    print_all_streets(hub)
    print_adjacency_matrix(hub)
    test_distance_function(hub)
    print_hash_table(hub)