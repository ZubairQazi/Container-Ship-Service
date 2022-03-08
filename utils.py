import copy
import re
import numpy as np

class Container:
    def __init__(self, name, weight):
        self.name = name
        self.name_adj = re.findall(r'^.*\d{4}',name)
        self.name_check = False
        self.weight = weight


class Slot:
    def __init__(self, container: Container, hasContainer, available):
        # unused, NaN (None), or name of container
        self.container = container
        self.hasContainer = hasContainer
        self.available = available


def create_ship_grid():
    ship_grid = []

    for i in range(8):
        container_row = []
        for i in range(12):
            container_row.append(Slot(None, False, False))
        ship_grid.append(container_row)

    return ship_grid


def update_ship_grid(file, ship_grid, containers):
    for line in file.readlines():
        slot_data = line.split()

        loc = [int(val) - 1 for val in re.sub(r"[\[\]]",'',slot_data[0]).split(",")[:2]]
        weight = int(re.sub(r"[\{\}\,]",'',slot_data[1]))
        status = slot_data[2] if len(slot_data) < 3 else " ".join(slot_data[2:])
        x,y = loc

        if status == "NAN":
            ship_grid[x][y] = Slot(None, hasContainer = False, available = False)
        elif status == "UNUSED":
            ship_grid[x][y] = Slot(None, hasContainer = False, available = True)
        else:
            ship_grid[x][y] = Slot(Container(status, weight), hasContainer = True, available = False)
            if len(ship_grid[x][y].container.name_adj) > 0:
                ship_grid[x][y].container.name_check = True 
            containers.append(loc)


def print_grid(ship_grid, containers):
    adj_ship_grid = []
    for row in ship_grid:
        adj_ship_grid.append([1 if slot.hasContainer == True else 0 for slot in row])
    
    for container in containers:
        x,y = container[0], container[1]

        adj_ship_grid[x][y] = ship_grid[x][y].container.name[0]
    
    print(np.array(adj_ship_grid[::-1][:]))


def balance(ship_grid):
    # TODO: Implement function
    return None


if __name__=="__main__":

    ship_grid = create_ship_grid()

    containers = []

    # Place containers manually
    if (input("Enter input manually?: ").lower() == 'y'):
        for n in range(int(input("Number of Containers: "))):

            container_loc = [int(l) for l in input("Enter location, space-separated: ").split()]
            container_name = input("Enter name of container: ")
            container_weight = input("Enter weight of container: ")
            print("Entering container into system...\n")

            ship_grid[container_loc[0]][container_loc[1]].container = Container(container_name, container_weight)
            ship_grid[container_loc[0]][container_loc[1]].hasContainer = True

            containers.append(container_loc)
    else:
        file_loc = input("Enter file directory, or none for default: ")
        file = open("samples/CUNARD_BLUE.txt", "r") if file_loc == "" else open(file_loc, "r")

        update_ship_grid(file, ship_grid, containers)
    
    print_grid(ship_grid, containers)