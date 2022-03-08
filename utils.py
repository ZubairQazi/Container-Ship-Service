import copy
import re
import numpy as np
import time

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


# Create a ship grid with size
def create_ship_grid(rows, columns):
    ship_grid = []

    for i in range(rows):
        container_row = []
        for i in range(columns):
            container_row.append(Slot(None, False, False))
        ship_grid.append(container_row)

    return ship_grid


# Update ship grid with manifest info, update list of containers accordingly
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


# Given ship grid, outputs matrix representing grid
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
    
    # TODO: Replace original, changed for debugging
    # print(np.array(adj_ship_grid[::-1][:]))
    print(np.array(adj_ship_grid))


# Returns move steps and status code (success or failure)
def balance(ship_grid, containers):
    # TODO: Create counter for max iterations, implenent according case

    # Calculate current ship balance on each side
    left_balance, right_balance, balanced = calculate_balance(ship_grid)
    
    # If balanced return, else continue
    if balanced:
        return None, True

    steps = []
    iter, max_iter = 0, 100

    halfway_line = len(ship_grid[0]) / 2

    previous_balance_ratio = 0

    # On heavier side, cycle through each container
    while(balanced is False):

        # Continue until balanced, or return error

        # Run until max iterations reached, then return failure
        if iter >= max_iter:
            print("Balance could not be achieved!")
            return None, False
        
        if left_balance > right_balance:
            curr_containers = [loc for loc in containers if loc[1] < halfway_line and ship_grid[loc[0]][loc[1]].container is not None]  
        else: 
            curr_containers = [loc for loc in containers if loc[1] >= halfway_line and ship_grid[loc[0]][loc[1]].container is not None]

        move_cost, balance_update = [], []
        # compute cost for each container to move to other side
        for container_loc in curr_containers:
            # compute closeness to balance if moved
            balance_update.append((container_loc, close_to_balance(ship_grid, container_loc, left_balance, right_balance)))

            # # compute cost to move to nearest open slot
            # costs.append(compute_cost_to_balance(container_loc, ship_grid))

        # select container with lowest cost that achieves balance or is closest (location of container)
        sorted_balance_update = sorted(balance_update, key=lambda x: x[1])
        container_to_move, balance_ratio = sorted_balance_update[0][0], sorted_balance_update[0][1]

        # If there has been no update in balance
        if (abs(previous_balance_ratio - balance_ratio) < 0.000001):
            # TODO: Call function to handle this case and then return
            return

        # move container
        goal_loc = list(nearest_available_balance(left_balance, right_balance, ship_grid))
        steps.append(move_to(container_to_move, goal_loc, ship_grid))
    
        left_balance, right_balance, balanced = calculate_balance(ship_grid)
        previous_balance_ratio = balance_ratio
        iter += 1
    
    # return updated ship grid and success
    return steps, True
    

def move_to(container_loc, goal_loc, ship_grid):
    # TODO: Implement function
    steps = []
    curr_container_loc = copy.deepcopy(container_loc)

    visited = []

    while (curr_container_loc != goal_loc):
        # return valid neighbors
        valid_moves = return_valid_moves(curr_container_loc, ship_grid)

        # TODO: If no valid moves, move top container

        distances = []
        for neighbor in valid_moves:
            distances.append((neighbor, manhattan_distance(neighbor, goal_loc)))
        
        distances = sorted(distances, key = lambda x: x[1])
        
        next_move = [-1, -1]
        for next_loc, distance in distances:
            if next_loc not in visited:
                next_move = next_loc
                break

        visited.append(next_move)

        steps.append(str(curr_container_loc) + " to " + str(next_move))

        # No valid moves
        if next_move == [-1, -1]:
            print("No valid moves!")
            break

        ship_grid[curr_container_loc[0]][curr_container_loc[1]], ship_grid[next_move[0]][next_move[1]] = \
            ship_grid[next_move[0]][next_move[1]], ship_grid[curr_container_loc[0]][curr_container_loc[1]]

        curr_container_loc = copy.deepcopy(next_move)

    return steps


# returns list of valid moves for container loc
def return_valid_moves(container_loc, ship_grid):

    neighbors = []
    # We only consider four neighbors
    neighbors.append([container_loc[0] - 1, container_loc[1]])
    neighbors.append([container_loc[0] + 1, container_loc[1]])
    neighbors.append([container_loc[0], container_loc[1] - 1])
    neighbors.append([container_loc[0], container_loc[1] + 1])

    # only neighrbors inside the grid, (x, y) >= 0
    neighbors = [neighbor for neighbor in neighbors if neighbor[0] >= 0 and neighbor[1] >= 0]

    valid_moves = []
    for neighbor in neighbors:
        if ship_grid[neighbor[0]][neighbor[1]].available is True:
            valid_moves.append(neighbor)

    return valid_moves

# returns the manhattan distance heuristic evaluation
def manhattan_distance(container_loc, goal_loc):
    return abs(container_loc[0] - goal_loc[0]) + abs(container_loc[1] - goal_loc[1])


def nearest_available_balance(left_balance, right_balance, ship_grid):

    halfway_line = int(len(ship_grid[0]) / 2)

    # Check side with lower weight for available slots
    if left_balance > right_balance:
        ship_grid_adjusted = [row[halfway_line:] for row in ship_grid]
    else:
        ship_grid_adjusted = [row[:halfway_line] for row in ship_grid]
    
    for x, row in enumerate(ship_grid_adjusted):
        for y, slot in enumerate(row):
            # Check if slot is available and is not hovering in the air
            if slot.available is True:
                # If slot is on the ground
                if y == 0:
                    # If dealing with right half
                    if (left_balance > right_balance):
                        return x, y + 6
                    else:
                        return x, y
                # If slot is not hovering in the air
                if ship_grid[x][y - 1].available is False:
                    # If dealing with right half
                    if (left_balance > right_balance):
                        return x, y + 6
                    else:
                        return x, y

    return -1, -1

# Returns closeness to perfect balance (1.0)
def close_to_balance(ship_grid, container_loc, left_balance, right_balance):

    container_weight = ship_grid[container_loc[0]][container_loc[1]].container.weight

    if left_balance > right_balance:
        closeness = (left_balance - container_weight) / (right_balance + container_weight)
    else:
        closeness = (right_balance - container_weight) / (left_balance + container_weight)
    
    return abs(1.0 - closeness)


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

    ship_grid = create_ship_grid(8, 12)

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
    
    print_grid(ship_grid)

    print("Total Weight:", total_weight)
    print("Left Balance:", left_balance)
    print("Right Balance:", right_balance)

    if balanced:
        print("Balanced!")
    else:
        print("Not Balanced!")
        steps, status = balance(ship_grid, containers)

        if (status is True):
            print_grid(ship_grid)

            left_balance, right_balance, balanced = calculate_balance(ship_grid)
            
            print("Total Weight:", total_weight)
            print("Left Balance:", left_balance)
            print("Right Balance:", right_balance)
            print("Balanced!")
        
        print(steps)

