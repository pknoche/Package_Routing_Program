import routing
from hub import Hub

# configuration settings
package_list = 'data/WGUPS Package File.csv'
address_list = 'data/WGUPS Address Table.csv'
distance_list = 'data/WGUPS Distance Table.csv'
num_operational_trucks = 2
package_capacity_per_truck = 16

# create delivery hub
hub = Hub(package_list, address_list, distance_list, num_operational_trucks, package_capacity_per_truck)


# Check in packages that have arrived at start of day
for i in range(1, 41):
    if i not in (6, 9, 25, 28, 32):
        hub.check_in_package(i)
    hub.check_in_package(9, 4)

# Set restriction for packages that can only go on truck 2
for i in (3, 5, 6, 35, 38):
    hub.packages.package_table.search(i).set_truck_restriction(2)




# first truck load-out
hub.load_trucks()


for i in range(len(hub.trucks.all_trucks)):
    print(f'The number of packages on truck {i + 1} is {hub.trucks.all_trucks[i].get_num_packages_loaded()}.')
print('\n\n')

for truck in hub.trucks.all_trucks:
    print(f'Truck number {truck.truck_id}:')
    print('Priority List:')
    for address, packages in truck.priority_package_manifest.items():
        print(f'Address: {address}')
        for package in packages:
            print(package)
        print('\n')
    print('\n')
    print('Standard List:')
    for address, packages in truck.package_manifest.items():
        print(f'Address: {address}')
        for package in packages:
            print(package)
    print('\n\n')

# print status of all packages
hub.packages.package_table.print_all_packages()




'''
for street in hub.addresses.all_addresses:
    print(street)

print(hub.addresses.distance_between(hub.addresses.get_hub_address(), '2010 W 500 S 84104'))

for distance_list in hub.addresses.adjacency_matrix:
    print(distance_list)
    
# test delivery:
hub.trucks.all_trucks[1].address_list = hub.addresses.all_addresses
hub.trucks.all_trucks[1].load_package(hub.packages.package_table.search(1))
hub.trucks.all_trucks[1].deliver_package(hub.packages.package_table.search(1))



for i in range(1, 41):
    if i not in (3, 6, 9, 14, 16, 18, 20, 25, 28, 32, 36, 37):
        if len(hub.trucks.all_trucks[0].package_manifest) <= 16:
            package = hub.packages.package_table.search(i)
            street = package.get_address()
            hub.trucks.all_trucks[0].load_package(package)
            
# print status of all packages
hub.packages.package_table.print_all_packages()
'''
