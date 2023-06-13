from hub import Hub

package_list = 'data/WGUPS Package File.csv'
address_list = 'data/WGUPS Address Table.csv'
distance_list = 'data/WGUPS Distance Table.csv'
num_operational_trucks = 2
package_capacity_per_truck = 16

hub = Hub(package_list, address_list, distance_list, num_operational_trucks, package_capacity_per_truck)

for i in range(1, 41):
    if i not in (6, 9, 25, 28, 32):
        hub.check_in_package(i)
    hub.check_in_package(9, 4)
print(hub.addresses.delivery_addresses)

hub.trucks.all_trucks[0].is_ready_to_load = False




hub.load_trucks(hub.calculate_load_size(num_operational_trucks), 1)

for i in range(1, 41):
    print(hub.packages.all_packages.search(i))

print('test')





'''
for i in range(1, 41):
    print(hub.packages.all_packages.search(i))

for address in hub.addresses.all_addresses:
    print(address)

print(hub.addresses.distance_between(hub.addresses.get_hub_address(), '2010 W 500 S 84104'))

for distance_list in hub.addresses.adjacency_matrix:
    print(distance_list)
    
# test delivery:
hub.trucks.all_trucks[1].address_list = hub.addresses.all_addresses
hub.trucks.all_trucks[1].load_package(hub.packages.all_packages.search(1))
hub.trucks.all_trucks[1].deliver_package(hub.packages.all_packages.search(1))



for i in range(1, 41):
    if i not in (3, 6, 9, 14, 16, 18, 20, 25, 28, 32, 36, 37):
        if len(hub.trucks.all_trucks[0].package_manifest) <= 16:
            package = hub.packages.all_packages.search(i)
            address = package.get_address()
            hub.trucks.all_trucks[0].load_package(package)
'''
