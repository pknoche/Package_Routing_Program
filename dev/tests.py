from datetime import datetime

import routing


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
    hub.packages.print_all_packages()
    print('\n\n')


def print_hash_table(hub):
    print('Package Hashtable:')
    i = 0
    for table in hub.packages.package_table.table:
        print(f'{i} ', end='')
        print(table)
        i += 1
    print()


def print_packages_by_delivery_groups(hub):
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


def print_routes(hub):  # Call from calculate_routes method in hub file
    for truck in hub.trucks.all_trucks:
        print(
            f'Truck {truck.truck_id} priority route: {truck.priority_route}\n'
            f'Distance: {routing.calculate_route_distance(hub, truck.priority_route):.1f} miles')
        j = 0
        for i in range(len(truck.priority_route) - 1):
            print(
                f'The distance between {str(truck.priority_route[j])} and {str(truck.priority_route[j + 1])} is '
                f'{hub.addresses.distance_between(truck.priority_route[j], truck.priority_route[j + 1])}')
            i += 1
            j += 1
        j = 0
        print(f'Truck {truck.truck_id} standard route: {truck.standard_route}\n'
              f'Distance: {routing.calculate_route_distance(hub, truck.standard_route):.1f} miles')
        for i in range(len(truck.standard_route) - 1):
            print(
                f'The distance between {str(truck.standard_route[j])} and {str(truck.standard_route[j + 1])} is '
                f'{hub.addresses.distance_between(truck.standard_route[j], truck.standard_route[j + 1]):.1f}')
            i += 1
            j += 1
        print()


def calculate_on_time_delivery(hub):
    time_format = '%I:%M %p'
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


def print_bound_packages(hub):
    for package in hub.packages.get_bound_packages():
        print(package)


def print_all_tests(hub):
    print_package_manifests(hub)
    print_all_streets(hub)
    print_adjacency_matrix(hub)
    test_distance_function(hub)
    print_hash_table(hub)


# Replace the function by the same name in hub.py to print the route after each round of optimization
'''
    def calculate_routes(self):
        # print route with no optimization
        for truck in self.trucks.all_trucks:
            priority_route = list(truck.priority_package_manifest.keys())
            standard_route = list(truck.standard_package_manifest.keys())
            route = priority_route + standard_route + [self.addresses.get_hub_address()]
            distance = 0.0
            if truck.is_at_hub:
                for i in range(len(route) - 1):
                    distance += self.addresses.distance_between(route[i], route[i + 1])
            truck.set_route(route)
        print('No Optimization:')
        tests.print_initial_routes(self)

        # perform initial optimization with nearest neighbor
        for truck in self.trucks.all_trucks:
            if truck.is_at_hub:
                routing.nearest_neighbor(self, truck)
        print('After Initial Optimization:')
        tests.print_initial_routes(self)

        # perform additional optimization with 2-opt
        for truck in self.trucks.all_trucks:
            routing.two_opt(self, truck)
        print('After 2-Opt:')
        tests.print_initial_routes(self)
'''
