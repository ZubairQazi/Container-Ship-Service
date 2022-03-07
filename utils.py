import copy
import re
import numpy as np

class Container:
    def __init__(self, name, weight):
        self.name = name
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
            containers.append(loc)


def print_grid(ship_grid):
    adj_ship_grid = []
    for row in ship_grid:
        adj_ship_grid.append([1 if slot.hasContainer == True else 0 for slot in row])
    
    for x, row in enumerate(ship_grid):
        for y, container in enumerate(row):

            if (ship_grid[x][y].container is not None):
                adj_ship_grid[x][y] = ship_grid[x][y].container.name[0]
            else:
                if (ship_grid[x][y].available == False):
                    adj_ship_grid[x][y] = 'X'
    
    print(np.array(adj_ship_grid[::-1][:]))

# Returns move steps and status code (success or failure)
def balance(ship_grid, containers):
    # TODO: Create counter for max iterations, return "Not Possible!" on fail.

    # Calculate current ship balance on each side
    left_balance, right_balance, balanced = calculate_balance(ship_grid)
    
    # If balanced return, else continue
    if balanced:
        return

    iter, max_iter = 0, 100

    # On heavier side, cycle through each container
    while(balanced is False):

        # Continue until balanced, or return error

        # Run until max iterations reached, then return failure
        if iter >= max_iter:
            print("Balance could not be achieved!")
            return None, False

        if left_balance > right_balance:
            curr_containers = [loc for loc in containers if loc[1] <= 5 and ship_grid[loc[0]][loc[1]].container is not None]  
        else: 
            curr_containers = [loc for loc in containers if loc[1] > 5 and ship_grid[loc[0]][loc[1]].container is not None]

        move_cost, balance_update = [], []
        # compute cost for each container to move to other side
        for container_loc in curr_containers:
            # compute closeness to balance if moved
            balance_update.append((container_loc, close_to_balance(container_loc, left_balance, right_balance)))

            # # compute cost to move to nearest open slot
            # costs.append(compute_cost_to_balance(container_loc, ship_grid))

        # select container with lowest cost that achieves balance or is closest (location of container)
        container = balance_update.sort(key=lambda x: x[1])[0][0]

        # move container
        steps = move_to_nearest_available(container, ship_grid)
    
        left_balance, right_balance, balanced = calculate_balance(ship_grid)
        iter += 1
    
    # return updated ship grid and success
    return steps, True
    

def move_to_nearest_available(container_loc, ship_grid):
    # TODO: Implement function
    return None


def close_to_balance(container_loc, left_balance, right_balance):
    # TODO: Implement function

    return None

def compute_cost_to_balance(container_loc, ship_grid):
    # TODO: Implement cost function
    return None

def calculate_balance(ship_grid):

    left_balance, right_balance = 0, 0

    for row in ship_grid:
        for loc, slot in enumerate(row):
            # no container in slot
            if slot.container is None:
                continue
            # left half of the ship
            if loc <= 5:
                left_balance += slot.container.weight
            # right half of the ship
            else:
                right_balance += slot.container.weight

    if left_balance == 0 and right_balance == 0:
        return left_balance, right_balance, True
    elif right_balance == 0:
        return left_balance, right_balance, False

    balanced = True if left_balance / right_balance > 0.9 and left_balance / right_balance < 1.1 else False

    return left_balance, right_balance, balanced


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

    left_balance, right_balance, balanced = calculate_balance(ship_grid)
    total_weight = left_balance + right_balance
    
    print_grid(ship_grid, containers)

    print("Total Weight:", total_weight)
    print("Left Balance:", left_balance)
    print("Right Balance:", right_balance)

    if balanced:
        print("Balanced!")
    else:
        print("Not Balanced!")

    steps, status = balance(ship_grid, containers)