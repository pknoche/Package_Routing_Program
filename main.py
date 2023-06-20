from datetime import time

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
package_9_address_update_time = time(hour=10, minute=20)

# Create delivery hub
hub = Hub(package_data, address_data, distance_data, num_operational_trucks, package_capacity_per_truck,
          truck_speed_MPH)

# ----------------------------------------------------------------------------------------------------------------------
# Package Configuration
# Check in packages that have arrived at start of day
for i in range(1, 41):
    if i not in (6, 9, 25, 28, 32):
        hub.check_in_package(i)
    hub.check_in_package(9, 5)

# Set restriction for packages that can only go on truck 2
for i in (3, 18, 36, 38):
    hub.packages.package_table.search(i).set_truck_restriction(2)

# Group of packages that must be delivered on same truck
hub.packages.delivery_binding = [13, 14, 15, 16, 19, 20]
# ----------------------------------------------------------------------------------------------------------------------
# Run Program
# Get trucks being used
truck1 = hub.trucks.all_trucks[0]
truck2 = hub.trucks.all_trucks[1]

# Dispatch first truck
truck1.set_route_start_time(hour=8, minute=0)
truck1.set_ready_for_dispatch(True)
hub.load_trucks()
hub.calculate_routes()
hub.dispatch_trucks()

# Dispatch truck 2 for priority 1 deliveries if there are any.
if hub.packages.priority_1_packages:
    truck2.set_route_start_time(hour=8, minute=0)
    truck2.set_ready_for_dispatch(True)
    hub.load_trucks()
    hub.calculate_routes()
    hub.dispatch_trucks()

# Check in late packages
for i in (6, 25, 28, 32):
    hub.check_in_package(i)
# Dispatch Truck 2 and set route start time if it did not deliver priority 1 packages earlier.
if not truck2.route_start_time:
    truck2.set_route_start_time(hour=9, minute=5)
truck2.set_ready_for_dispatch(True)
hub.load_trucks()
hub.calculate_routes()
hub.dispatch_trucks()

# Dispatch final truck after package 9 address is updated
# Set time of truck to package update time if truck returned to hub before update time.
if truck1.is_at_hub and truck1.get_time() < package_9_address_update_time:
    truck1.set_current_time(package_9_address_update_time)

# Update package 9 address and status.
hub.correct_package_address(9, '410 S STATE ST', 'SALT LAKE CITY', 'UT', '84111')
truck2.set_ready_for_dispatch(True)
hub.load_trucks()
hub.calculate_routes()
hub.dispatch_trucks()

# TESTS

tests.calculate_on_time_delivery(hub)
tests.print_all_packages(hub)

total_distance_traveled = 0
for truck in hub.trucks.all_trucks:
    total_distance_traveled += truck.total_miles_traveled

print(f'Total distance traveled by all trucks: {total_distance_traveled:.1f} miles')

# print number of packages per truck
# tests.print_package_manifests(hub)

# print status of all packages
# tests.print_all_packages(hub)

# tests.print_adjacency_matrix(hub)

# tests.print_hash_table(hub)
