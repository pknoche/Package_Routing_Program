import csv

all_packages = None


class Package:
    def __init__(self, package_id, address, city, state, zipcode, deadline, mass, notes=''):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.deadline = deadline
        self.mass = mass
        self.notes = notes

    def __str__(self):
        return (f'ID: {self.package_id}, Address: {self.address}, City: {self.city}, State: {self.state}, '
                f'Zip: {self.zipcode}, Delivery Deadline: {self.deadline}, Mass(kg): {self.mass}, Notes: {self.notes}')


class Hashtable:
    def __init__(self, num_buckets=10):
        self.num_buckets = num_buckets
        self.table = []
        for i in range(num_buckets):
            self.table.append([])

    def hash(self, package_id):
        return package_id % self.num_buckets

    def insert(self, package):
        key = self.hash(package.package_id)
        # print(f'Package key is {key}\n')  # TODO - remove
        i = 0
        while i < len(self.table[key]):
            if package.package_id == self.table[key][i].package_id:
                self.update(key, i, package)
                return
            i += 1
        self.table[key].append(package)

    def update(self, key, index, package):
        self.table[key][index] = package
        print(f'Updated package is: {package}')  # TODO - remove

    def search(self, package_id):
        key = self.hash(package_id)
        for i in range(len(self.table[key])):
            package = self.table[key][i]
            if package.package_id == package_id:  # FIXME = type hinting? Ignored unresolved attribute reference
                return package
        return None


def import_packages(file):
    global all_packages
    all_packages = Hashtable()
    with open(file, newline='') as packages:
        package_data = csv.reader(packages)
        next(package_data)
        for package in package_data:
            package_id = int(package[0])
            address = package[1]
            city = package[2]
            state = package[3]
            zipcode = package[4]
            deadline = package[5]
            mass = package[6]
            notes = package[7]

            new_package = Package(package_id, address, city, state, zipcode, deadline, mass, notes)
            all_packages.insert(new_package)
