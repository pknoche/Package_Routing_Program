import csv
from typing import Union

import routing


class Address:
    def __init__(self, street: str, zipcode: str, index: int):
        self.address = f'{street} {zipcode}'
        self.index = index

    def __str__(self) -> str:
        return self.address


class AddressCollection:
    def __init__(self):
        self.all_addresses: dict[str, Address] = {}
        self.adjacency_matrix: list[list[float]] = []
        self.delivery_addresses: dict[str, Address] = {}
        self.hub_address = None

    def import_addresses(self, file: str):
        with open(file, newline='') as addresses:
            address_data = csv.reader(addresses)
            index = 0
            for address in address_data:
                address = address[0].strip()
                street, zipcode = address.split('\n')
                zipcode = zipcode.strip('()')
                street = street.upper()
                street = street.replace('NORTH', 'N')
                street = street.replace('EAST', 'E')
                street = street.replace('SOUTH', 'S')
                street = street.replace('WEST', 'W')

                new_address = Address(street, zipcode, index)
                self.all_addresses[street + ' ' + zipcode] = new_address
                index += 1
            self.hub_address = list(self.all_addresses.values())[0]

    def import_distances(self, file: str):
        with open(file, newline='') as distances:
            distance_data = csv.reader(distances)
            for distance in distance_data:
                # convert string from csv to float unless value is blank, in which case append 0.0
                float_values = [float(d) if d else 0.0 for d in
                                distance]
                self.adjacency_matrix.append(float_values)
            n = len(self.adjacency_matrix)
            for i in range(n):
                for j in range(i + 1, n):
                    self.adjacency_matrix[i][j] = self.adjacency_matrix[j][i]
        self.adjacency_matrix = routing.floyd_warshall(self.adjacency_matrix)

    def distance_between(self, address1: str, address2: str) -> float:
        address1 = address1.upper()
        address2 = address2.upper()
        if (address1 in self.all_addresses) and (address2 in self.all_addresses):
            address1_index = self.all_addresses.get(address1).index
            address2_index = self.all_addresses.get(address2).index
            return self.adjacency_matrix[address1_index][address2_index]

    def add_delivery_address(self, delivery_address: str):
        self.delivery_addresses[delivery_address] = self.all_addresses[delivery_address]

    def address_is_valid(self, address: str) -> bool:
        if address in self.all_addresses:
            return True
        return False

    def get_hub_address(self) -> str:
        return str(self.hub_address)

    def get_address(self, address: str) -> Address:
        return self.all_addresses.get(address)
