import packages
import routing
# TODO - add addresses to dictionary instead of list

all_packages = packages.PackageCollection()
all_packages.import_packages('data/WGUPS Package File.csv')

all_addresses = routing.AddressCollection()
all_addresses.import_addresses('data/WGUPS Address Table.csv')

all_distances = routing.DistanceCollection()
all_distances.import_distances('data/WGUPS Distance Table.csv')









'''
i = 1
while i <= 40:
    print(all_packages.all_packages.search(i))
    i += 1

for address in all_addresses.all_addresses:
    print(address)

for distance_list in all_distances.all_distances:
    print(distance_list)

print(all_distances.distance_between(all_addresses, (all_addresses.hub_address.street + ' ' + all_addresses.hub_address.zipcode), '2010 W 500 S 84104'))
print(f'Hub address: {all_addresses.hub_address}')
'''
