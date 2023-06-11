import csv
from typing import Optional, Union, List


class Address:
    def __init__(self, street: str, zipcode: str, index: int):
        self.street = street
        self.zipcode = zipcode
        self.index = index

    def __str__(self) -> str:
        return f'Street: {self.street}, Zipcode: {self.zipcode}'


class AddressCollection:
    def __init__(self):
        self.all_addresses = {}
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


class DistanceCollection:
    def __init__(self):
        self.all_distances: List[List[Optional[float]]] = []

    def import_distances(self, file: str):
        with open(file, newline='') as distances:
            distance_data = csv.reader(distances)
            for distance in distance_data:
                float_value = [float(d) for d in distance if d != '']
                self.all_distances.append(float_value)

    def distance_between(self, address_list: AddressCollection, address1: str, address2: str) -> Union[float, str]:
        address1 = address1.upper()
        address2 = address2.upper()
        address1_index = address_list.all_addresses.get(address1).index
        address2_index = address_list.all_addresses.get(address2).index
        if address1_index is not None and address2_index is not None:
            return self.all_distances[address2_index][address1_index]
        return 'Address not found. Double check spelling and try again.'
