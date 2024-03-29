import datetime

import ui
import hub
from dev import tests

# ----------------------------------------------------------------------------------------------------------------------
# Configuration Settings:

# Data:
package_data = 'data/WGUPS Package File.csv'
address_data = 'data/WGUPS Address Table.csv'
distance_data = 'data/WGUPS Distance Table.csv'
num_packages = 40

# Trucks:
num_operational_trucks = 2
truck_speed_MPH = 18
package_capacity_per_truck = 16

# Incorrect Address Update Time:
package_9_address_update_time = datetime.time(hour=10, minute=20)

# Create Delivery Hub
slc_hub = hub.Hub(package_data, address_data, distance_data, num_operational_trucks,
                  package_capacity_per_truck, truck_speed_MPH, num_packages)

# ----------------------------------------------------------------------------------------------------------------------
# Package Configuration:

# Check in packages that have arrived at start of day
time_scanned = datetime.datetime.strptime('7:00', '%H:%M').time()
for i in range(1, 41):
    if i not in (6, 9, 25, 28, 32):
        slc_hub.check_in_package(time_scanned, i)
    # Override the status of the package with the incorrect address.
    slc_hub.check_in_package(time_scanned, 9, 5)

# Set restriction for packages that can only go on truck 2
for i in (3, 18, 36, 38):
    slc_hub.packages.search(i).set_truck_restriction(2)

# Group of packages that must be delivered on same truck
packages_to_bind = {13, 14, 15, 16, 19, 20}
slc_hub.packages.set_package_binding(packages_to_bind)

# ----------------------------------------------------------------------------------------------------------------------
# Run Program:

# Get trucks being used:
truck1 = slc_hub.trucks.all_trucks[0]
truck2 = slc_hub.trucks.all_trucks[1]

# Dispatch first truck:
truck1.set_route_start_time(hour=8, minute=0)
truck1.is_ready_for_dispatch = True
slc_hub.load_trucks()
slc_hub.calculate_routes()
slc_hub.dispatch_trucks()

# Check in late packages:
time_scanned = datetime.datetime.strptime('9:05', '%H:%M').time()
for i in (6, 25, 28, 32):
    slc_hub.check_in_package(time_scanned, i)

# Dispatch second truck:
truck2.set_route_start_time(hour=9, minute=5)
truck2.is_ready_for_dispatch = True
slc_hub.load_trucks()
slc_hub.calculate_routes()
slc_hub.dispatch_trucks()

# Dispatch final truck after package 9 address is updated:

# Set time of truck to package update time if truck returned to hub before update time:
if truck2.current_time < package_9_address_update_time:
    truck2.set_current_time(package_9_address_update_time)

# Update package 9 address and status and dispatch final truck:
slc_hub.correct_package_address(package_id=9, street='410 S STATE ST', city='SALT LAKE CITY', state='UT',
                                zipcode='84111')
truck2.is_ready_for_dispatch = True
slc_hub.load_trucks()
slc_hub.calculate_routes()
slc_hub.dispatch_trucks()

# ----------------------------------------------------------------------------------------------------------------------
# Tests - uncomment to run - prints out various data structures and information to confirm functionality:
# tests.print_all_tests(slc_hub)

# ----------------------------------------------------------------------------------------------------------------------
# Launch UI:
ui.main_menu(slc_hub)
