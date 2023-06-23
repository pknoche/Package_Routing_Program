from datetime import time, datetime

import ui
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
time_scanned = datetime.strptime('7:00', '%H:%M').time()
for i in range(1, 41):
    if i not in (6, 9, 25, 28, 32):
        hub.check_in_package(time_scanned, i)
    hub.check_in_package(time_scanned, 9, 5)

# Set restriction for packages that can only go on truck 2
for i in (3, 18, 36, 38):
    hub.packages.search(i).set_truck_restriction(2)

# Group of packages that must be delivered on same truck
packages_to_bind = {13, 14, 15, 16, 19, 20}
hub.packages.set_package_binding(packages_to_bind)
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

# Check in late packages
time_scanned = datetime.strptime('9:05', '%H:%M').time()
for i in (6, 25, 28, 32):
    hub.check_in_package(time_scanned, i)

# Dispatch second truck
truck2.set_route_start_time(hour=9, minute=5)
truck2.set_ready_for_dispatch(True)
hub.load_trucks()
hub.calculate_routes()
hub.dispatch_trucks()

# Dispatch final truck after package 9 address is updated
# Set time of truck to package update time if truck returned to hub before update time.
if truck2.is_at_hub and truck2.get_time() < package_9_address_update_time:
    truck2.set_current_time(package_9_address_update_time)

# Update package 9 address and status and dispatch final truck
hub.correct_package_address(package_id=9, street='410 S STATE ST', city='SALT LAKE CITY', state='UT', zipcode='84111')
truck2.set_ready_for_dispatch(True)
hub.load_trucks()
hub.calculate_routes()
hub.dispatch_trucks()

# Tests
tests.print_bound_packages(hub)
print()
tests.print_packages_by_delivery_groups(hub)

# Launch UI
ui.main_menu(hub)
