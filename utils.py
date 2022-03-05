import copy
import numpy as np

class Slot:
    def __init__(self, container, hasContainer):
        # unused, NaN (None), or name of container
        self.container = container
        self.hasContainer = hasContainer


ship_grid = []

for i in range(8):
    container_row = []
    for i in range(12):
        s = Slot("", True)
        container_row.append(s)
    ship_grid.append(container_row)


# generate random containers
containers = []
for n in range(int(input())):
    container = [np.random.randint(0, 8), np.random.randint(0,12)]
    containers.append(container)


# fill ship grid with containers
for row in ship_grid:
    for container in row:
        if np.random.randint(0,2) == 1:
            container.hasContainer = True
        else:
            container.hasContainer = False


def print_grid(ship_grid):
    adj_ship_grid = []
    for row in ship_grid:
        adj_ship_grid.append([1 if slot.hasContainer == True else 0 for slot in row])
    
    for container in containers:
        x,y = container[0], container[1]

        adj_ship_grid[x][y] = 'x'
    
    print(np.array(adj_ship_grid))

print(print_grid(np.array(ship_grid)))
print(containers)