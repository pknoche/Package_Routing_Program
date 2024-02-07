# Package Routing Program

## Overview

This program is a Python-based application that simulates the logistics behind managing package deliveries within a city. This program utilizes heuristics to optimize routes and ensure timely deliveries.

## Major Features

- **Route Optimization**: Implements algorithms to find the most efficient path for package delivery while satisfying delivery requirements.
- **Package Management**: Manages packages throughout their lifecycle from loading to delivery, tracking each package's status.
- **Data Import**: Reads and parses CSV files for addresses, distances, and package details.
- **Delivery Simulation**: Simulates the delivery process using a time-step approach, allowing users to see the progress of deliveries throughout the day.
- **User Interface**: Provides a simple command-line interface for user interaction with the system.

## Programming Concepts

- **Object-Oriented Programming**: The application employs object-oriented design principles to improve modularity, reusability, readability, and ease of maintenance.
- **Algorithm Implementation**: Incorporates standard and custom algorithms for route optimization based on distances and package constraints, including the Floyd-Warshall and 2-Opt algorithms.
- **Data Structures**: Utilizes built-in Python data structures such as dictionaries and lists for efficient data storage and retrieval. Incorporates a custom implemenation of a hashtable for storing and retrieving package objects. Uses graphs to store and optimize route distances.
- **File I/O**: Leverages Python's file handling capabilities to read address and package data from CSV files.
- **Docstrings**: Uses docstrings to document classes, functions, and methods.
- **Type Hinting**: Uses type hinting to improve code readability.

## Data Files

- `WGUPS Address Table.csv`: Contains the address data for delivery points.
- `WGUPS Distance Table.csv`: Stores the distance information between addresses.
- `WGUPS Package File.csv`: Lists the packages to be delivered, including delivery details and constraints.
