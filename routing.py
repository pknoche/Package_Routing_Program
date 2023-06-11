import csv


class Address:
    def __init__(self, street, zipcode):
        self.street = street
        self.zipcode = zipcode

    def __str__(self):
        return f'Street: {self.street}, Zipcode: {self.zipcode}\n'


class Addresses:
    all_addresses = []
    hub_address = None

    def import_addresses(self, file):
        with open(file, newline='') as addresses:
            address_data = csv.reader(addresses)
            for address in address_data:
                address = address[0].strip()
                street, zipcode = address.split('\n')
                zipcode = zipcode.strip('()')
                new_address = Address(street, zipcode)
                self.all_addresses.append(new_address)
        self.hub_address = self.all_addresses[0].street


class Distances:
    all_distances = []

    def import_distances(self, file):
        with open(file, newline='') as distances:
            distance_data = csv.reader(distances)
            for distance in distance_data:
                self.all_distances.append(distance)

    def distance_between(self, address_list, address1, address2):
        i = 0
        address1_index = None
        address2_index = None
        while i < len(address_list.all_addresses):
            if address_list.all_addresses[i].street == address1:
                address1_index = i
            if address_list.all_addresses[i].street == address2:
                address2_index = i
            if address1_index is not None and address2_index is not None:
                return self.all_distances[address2_index][address1_index]
            i += 1
        return 'Address not found. Double check spelling and try again.'
