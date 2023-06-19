import datetime

from dev import tests
from hub import Hub


# ----------------------------------------------------------------------------------------------------------------------
# configuration settings
package_data = 'data/WGUPS Package File.csv'
address_data = 'data/WGUPS Address Table.csv'
distance_data = 'data/WGUPS Distance Table.csv'
num_operational_trucks = 2
truck_speed_MPH = 18
package_capacity_per_truck = 16
route_start_time = datetime.time(hour=8, minute=0)

# Create delivery hub
hub = Hub(package_data, address_data, distance_data, num_operational_trucks, package_capacity_per_truck,
          truck_speed_MPH, route_start_time)

# ----------------------------------------------------------------------------------------------------------------------
# Package Configuration
# Check in packages that have arrived at start of day
for i in range(1, 41):
    if i not in (6, 9, 25, 28, 32):
        hub.check_in_package(i)
    hub.check_in_package(9, 4)

# Set restriction for packages that can only go on truck 2
for i in (3, 18, 36, 38):
    hub.packages.package_table.search(i).set_truck_restriction(2)

# Group of packages that must be delivered on same truck
hub.packages.delivery_binding = (13, 14, 15, 16, 19, 20)

# ----------------------------------------------------------------------------------------------------------------------
# Run Program

# first truck load-out
hub.trucks.all_trucks[0].set_ready_for_dispatch(True)
hub.load_trucks()
hub.calculate_routes()
hub.dispatch_trucks()
for package in hub.packages.package_table.get_all_packages():
    if package.status_code == 4:
        print(package)


# print number of packages per truck
#tests.print_package_manifests(hub)

# print status of all packages
#tests.print_all_packages(hub)

#tests.print_adjacency_matrix(hub)

#tests.print_hash_table(hub)


