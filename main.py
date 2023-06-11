import packages
import routing
# TODO - add addresses to dictionary instead of list

all_packages = packages.import_packages('data/WGUPS Package File.csv')

all_addresses = routing.Addresses()
all_addresses.import_addresses('data/WGUPS Address Table.csv')

all_distances = routing.Distances()
all_distances.import_distances('data/WGUPS Distance Table.csv')


print(all_distances.distance_between(all_addresses, all_addresses.hub_address, '2010 W 500 S'))





'''
i = 1
while i <= 40:
    print(packages.all_packages.search(i))
    i += 1

'''
