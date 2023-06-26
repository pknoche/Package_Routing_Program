"""This module is for the user interface of the program."""

import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hub import Hub


def main_menu(hub: 'Hub'):
    """Launches the user interface.

    Args:
        hub: The hub to launch the interface for.
    """

    # Print the main menu
    while True:
        print('Welcome to WGUPS Route Management System. Please choose from one of the options below:')
        print('1. Get the status of a single package at a specific time')
        print('2. Get the status of all packages at a snapshot in time')
        print('3. Get end of day report with truck history and package status')
        print('4. Exit program\n')

        # Get user input and validate it
        while True:
            choice = input('Type selection here: ')
            if choice not in ('1', '2', '3', '4'):
                print('Invalid selection. Please enter a number between 1 and 4.\n')
                continue

            # Get a package ID and time from the user and validate it. Use these values to look up a package at the
            # specified time.
            if choice == '1':
                print()
                while True:
                    try:
                        package_id = int(input('Enter Package ID: '))
                        if hub.packages.search(package_id) is None:
                            print(f'\nCould not locate package ID {package_id} in the system. '
                                  f'Please try a different package ID.\n')
                        else:
                            break
                    except ValueError:
                        print('\nInvalid input. Please enter the package ID, which is an integer.\n')
                while True:
                    try:
                        time_input = input('Please enter a time in HH:mm format: ')
                        time_input = datetime.datetime.strptime(time_input, '%H:%M').time()
                        break
                    except ValueError:
                        print('\nInvalid input. The time entered must be in 24-hour time '
                              'in the following format: HH:mm.')
                        print('For example, 1:00 PM should be entered as 13:00.\n')
                print()
                hub.packages.print_single_package_at_time(package_id, time_input)
                input('\nPress Enter key to return to the main menu.\n')
                break

            # Get a time from the user and validate it. Use this to display the status of all packages at the
            # specified time.
            elif choice == '2':
                print()
                while True:
                    try:
                        time_input = input('Please enter a time in HH:mm format: ')
                        time_input = datetime.datetime.strptime(time_input, '%H:%M').time()
                        break
                    except ValueError:
                        print(
                            '\nInvalid input. The time entered must be in 24-hour time in the following format: HH:mm.')
                        print('For example, 1:00 PM should be entered as 13:00.\n')
                print()
                hub.packages.print_all_packages_at_time(time_input)
                input('\nPress Enter key to return to the main menu.\n')
                break

            # Print the end of day report showing the history of all trucks and the status of all packages.
            elif choice == '3':
                print()
                hub.print_end_of_day_report()
                input('\nPress Enter key to return to the main menu.\n')
                break

            # Exit the program.
            elif choice == '4':
                print('\nProgram Exited\n')
                exit()
