from hub import Hub

package_list = 'data/WGUPS Package File.csv'
address_list = 'data/WGUPS Address Table.csv'
distance_list = 'data/WGUPS Distance Table.csv'
num_operational_trucks = 2

hub = Hub(package_list, address_list, distance_list, num_operational_trucks)

for i in range(1, 41):
    if i not in (6, 9, 25, 28, 32):
        hub.check_in_package(i)
    hub.check_in_package(9, 4)
    i += 1

for i in range(1, 41):
    print(hub.packages.all_packages.search(i))







'''
for i in range(1, 41):
    print(hub.packages.all_packages.search(i))

for address in hub.addresses.all_addresses:
    print(address)

print(hub.addresses.distance_between(hub.addresses.get_hub_address(), '2010 W 500 S 84104'))

for distance_list in hub.addresses.adjacency_matrix:
    print(distance_list)
'''
