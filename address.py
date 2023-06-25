"""A module for handling address and distance-related operations.

This module provides classes and methods for importing, storing, and manipulating address and distance data.
"""

import csv

import routing


class Address:
    """A class used to represent an address.

    Attributes:
        address: The street number, street name, and zipcode of the address.
        index: A unique identifier for the address used to look it up in the distance matrix.
    """

    def __init__(self, street: str, zipcode: str, index: int):
        """Initializes Address with street, zipcode, and index."""
        self.address = f'{street} {zipcode}'
        self.index = index

    def __str__(self) -> str:
        """Returns the Address as a string.

        Returns:
            str: The Address in string format.
        """

        return self.address


class AddressCollection:
    """A class used to represent a collection of addresses and distances.

    Attributes:
        all_addresses: A dictionary mapping the string representation of an address to its corresponding address object.
        distance_matrix: A 2-dimensional list representing the distances between a pair of addresses.
        hub_address: The Address object for the hub.
    """

    def __init__(self):
        """Initializes an AddressCollection object."""
        self.all_addresses: dict[str, Address] = {}
        self.distance_matrix: list[list[float]] = []
        self.hub_address = None

    def import_addresses(self, file: str):
        """Imports addresses from a provided CSV file and stores them in a dictionary mapping the address's string
        representation to the corresponding Address object.

        Args:
            file: The path to the CSV file containing the addresses to be imported.

        Time Complexity: O(n), where n is the number of addresses in the CSV file.

        Space complexity: O(n), where n is the number of addresses in the CSV file.
        """

        with open(file, newline='') as addresses:
            address_data = csv.reader(addresses)
            # Store the order of the address in the CSV file so that it can be matched with its position in the
            # distance matrix.
            index = 0
            for address in address_data:  # Iterate through each address in the file and normalize the format.
                address = address[0].strip()  # Remove any leading or trailing spaces.
                street, zipcode = address.split('\n')  # Separate the street and zipcode.
                zipcode = zipcode.strip('()')  # Remove parentheses from the zipcode.
                street = street.upper()  # Convert the street name to uppercase.

                #  Replace the cardinal directions' names with their abbreviations.
                street = street.replace('NORTH', 'N')
                street = street.replace('EAST', 'E')
                street = street.replace('SOUTH', 'S')
                street = street.replace('WEST', 'W')

                new_address = Address(street, zipcode, index)
                self.all_addresses[street + ' ' + zipcode] = new_address
                index += 1
            # Extract the str representation of the hub address, which is the first address in the file.
            self.hub_address = list(self.all_addresses.values())[0].address

    def import_distances(self, file: str):
        """Imports distances from a given CSV file and stores them in a distance matrix.

        Args:
            file: The path to the CSV file containing the distances.

        Time complexity: O(n^3), where n is the number of addresses in the CSV file. This is due to the use of the
        Floyd-Warshall algorithm for optimizing distances.

        Space complexity: O(n^2), where n is the number of
        addresses in the CSV file. This is due to the use of a distance matrix to store the distances between each
        pair of addresses.
        """

        with open(file, newline='') as distances:
            distance_data = csv.reader(distances)
            for distance in distance_data:
                # Convert string from CSV to float unless value is blank, in which case append 0.0.
                float_values = [float(d) if d else 0.0 for d in distance]
                self.distance_matrix.append(float_values)
            n = len(self.distance_matrix)
            # Fill out the upper triangle of the distance matrix.
            for i in range(n):
                for j in range(i + 1, n):
                    self.distance_matrix[i][j] = self.distance_matrix[j][i]
        # Use the Floyd Warshall algorithm to optimize the distance matrix with the shortest route between
        # addresses i and j that can pass through k.
        self.distance_matrix = routing.floyd_warshall(self.distance_matrix)

    def distance_between(self, address1: str, address2: str):
        """Looks up the shortest distance between address1 and address2 in the distance matrix.

        Args:
            address1: The first address.
            address2: The second address.

        Returns:
            The shortest distance between address1 and address2.

        Time complexity: O(1).

        Space complexity: O(1).
        """

        # Find the index of each address and use to look up distance between them in the distance matrix.
        address1 = address1.upper()
        address2 = address2.upper()
        if (address1 in self.all_addresses) and (address2 in self.all_addresses):
            address1_index = self.all_addresses.get(address1).index
            address2_index = self.all_addresses.get(address2).index
            return self.distance_matrix[address1_index][address2_index]

    def address_is_valid(self, address: str):
        """Checks if an address is in the AddressCollection.

        Args:
            address: The address to check.

        Returns:
            True if the address is in the AddressCollection, False otherwise.

        Time complexity: O(1) because all_addresses is a dictionary and looking up a value in a dictionary is a
        constant time operation.

        Space complexity: O(1).
        """

        return address in self.all_addresses

    def get_address(self, address: str):
        """Returns the Address object for a given address string.

        Args:
            address: The address to retrieve.

        Returns:
            The Address object for the given address if it is in the AddressCollection, None otherwise.

        Time complexity: O(1) because all_addresses is a dictionary and looking up a value in a dictionary is a
        constant time operation.

        Space complexity: O(1).
        """

        return self.all_addresses.get(address)
