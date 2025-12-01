import ex1_check
import search
import utils

id = ["322587064"]


# Disclaimer:
# I used AI to help me gather information about this course meterial and certain concepts as well as python syntax.
# Also I used the help of Ori Susan a fellow student for the idea of pruning when there is a single robot.


class WateringProblem(search.Problem):
    """This class implements a pressure plate problem"""

    def __init__(self, initial):
        self.rows = initial['Size'][0]
        self.cols = initial['Size'][1]

        self.walls = frozenset(initial['Walls'])

        self.robot_capacities = {}
        for r_id, values in initial['Robots'].items():
            self.robot_capacities[r_id] = values[3]

        robots_list = []
        for r_id, values in initial['Robots'].items():
            # values is (row, col, load, capacity) -> we keep (row, col, load)
            robots_list.append((r_id, values[0], values[1], values[2]))
        robots = tuple(sorted(robots_list))

        taps_list = []
        for loc, amount in initial['Taps'].items():
            taps_list.append((loc[0], loc[1], amount))
        taps = tuple(sorted(taps_list))

        plants_list = []
        for loc, needed in initial['Plants'].items():
            plants_list.append((loc[0], loc[1], needed))
        plants = tuple(sorted(plants_list))

        initial_state = (robots, taps, plants)

        search.Problem.__init__(self, initial_state)

    def successor(self, state):
        """ Generates the successor states returns [(action, achieved_states, ...)]"""
        
        robots, taps, plants = state
        successors = []

        # Pruning if we have a single robot
        if len(robots) == 1:
            robot = robots[0]
            robot_id, robot_row, robot_col, robot_load = robot
            robot_cap = self.robot_capacities[robot_id]

            # If robot has water we try to pour
            if robot_load > 0:
                # Loop over plants to check if we are standing on one
                for i, plant in enumerate(plants):
                    plant_row, plant_col, plant_needed = plant
                    # If we are standing on a plant that needs water
                    if plant_row == robot_row and plant_col == robot_col and plant_needed > 0:      
                        # We pour                  
                        new_needed = plant_needed - 1
                        new_load = robot_load - 1
                        
                        # Update the robot
                        new_robot = (robot_id, robot_row, robot_col, new_load)
                        new_robots = (new_robot,) # Tuple of 1 robot
                        
                        # Update Plants
                        new_plants_list = list(plants)
                        new_plants_list[i] = (plant_row, plant_col, new_needed)
                        
                        # And pack the new state
                        new_state = (new_robots, taps, tuple(new_plants_list))
                        
                        # We return only this acftion pruning all other moves
                        return [(f"POUR{{{robot_id}}}", new_state)]

            # If robot is empty check for load            
            if robot_load == 0:
                # Loop throuhg our taps
                for i, tap in enumerate(taps):
                    tap_row, tap_col, tap_amount = tap
                    # If we are standing on a tap that has water
                    if tap_row == robot_row and tap_col == robot_col and tap_amount > 0:  
                        # We load                      
                        new_amount = tap_amount - 1
                        new_load = robot_load + 1
                        
                        # Update robot
                        new_robot = (robot_id, robot_row, robot_col, new_load)
                        new_robots = (new_robot,)
                        
                        # Update taps
                        new_taps_list = list(taps)
                        new_taps_list[i] = (tap_row, tap_col, new_amount)
                        
                        # Pack new state
                        new_state = (new_robots, tuple(new_taps_list), plants)
                        
                        # Return only this action pruning all other moves
                        return [(f"LOAD{{{robot_id}}}", new_state)]

        robot_locations = set((r[1], r[2]) for r in robots) # Store the positino of each robot
        # Movement action:
        moves = [
                ("UP", -1, 0), 
                ("DOWN", 1, 0), 
                ("LEFT", 0, -1), 
                ("RIGHT", 0, 1)
        ]

        # Generates for every robot all it's possible states
        for i, robot in enumerate(robots):
            robot_id, robot_row, robot_col, robot_load = robot
            robot_cap = self.robot_capacities[robot_id] 
            
            

            for action_name, delta_row, delta_col in moves:
                new_row, new_col = robot_row + delta_row, robot_col + delta_col
                
                # Checks it's inside grid
                if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                    # CChecks it's not inside a wall
                    if (new_row, new_col) not in self.walls:
                        # Check doesn't collide with another robot
                        if (new_row, new_col) not in robot_locations:
                                                        
                            # Creates a new state for this robot
                            new_robot = (robot_id, new_row, new_col, robot_load)
                                                        
                            new_robots = list(robots) # Need list cause it is immutable
                            new_robots[i] = new_robot # 
                                                        
                            new_state = (tuple(new_robots), taps, plants) 
                                                        
                            action_str = f"{action_name}{{{robot_id}}}"
                            successors.append((action_str, new_state))
            
            # Load action:
            # Checks if we can load more water
            if robot_load < robot_cap:
                # Checks all taps to see if we are standing on one
                for tap_index, tap in enumerate(taps):
                    tap_row, tap_col, tap_amount = tap
                    
                    # Checks if we standing on this tap
                    if tap_row == robot_row and tap_col == robot_col: 
                        #Checks this tap has water we can load
                        if tap_amount > 0:                            
                            new_load = robot_load + 1
                            new_tap_amount = tap_amount - 1
                            
                            # Update robot
                            new_robot = (robot_id, robot_row, robot_col, new_load)
                            new_robots = list(robots)
                            new_robots[i] = new_robot
                            
                            # Update taps 
                            new_tap = (tap_row, tap_col, new_tap_amount)
                            new_taps = list(taps)
                            new_taps[tap_index] = new_tap
                            
                            # Update state
                            new_state = (tuple(new_robots), tuple(new_taps), plants)
                            successors.append((f"LOAD{{{robot_id}}}", new_state))
                        break # There can only be one tap here so no point to keep looking 
            
            # Pour action:
            if robot_load > 0:
                # Goes over all the plants
                for plant_index, plant in enumerate(plants):
                    plant_row, plant_col, plant_water_needed = plant
                    
                    # Check if robot standing on plant
                    if plant_row == robot_row and plant_col == robot_col: 
                        # Checks the plant needs water
                        if plant_water_needed > 0:                            
                            new_load = robot_load - 1
                            new_needed = plant_water_needed - 1
                            
                            # Update Robot
                            new_robot = (robot_id, robot_row, robot_col, new_load)
                            new_robots = list(robots)
                            new_robots[i] = new_robot
                            
                            # Update Plants
                            new_plant = (plant_row, plant_col, new_needed)
                            new_plants = list(plants)
                            new_plants[plant_index] = new_plant
                            
                            # Update state
                            new_state = (tuple(new_robots), taps, tuple(new_plants))
                            successors.append((f"POUR{{{robot_id}}}", new_state))
                        break # There can only be one plant here so no point to keep looking

        return successors

    def goal_test(self, state):
        """ given a state, checks if this is the goal state, compares to the created goal state returns True/False"""
        _, _, plants = state
        
        # Goes over all the plants        
        for p in plants:
            if p[2] > 0: # If any plant needs water it isn't the goal state
                return False
        
        return True

    def h_astar(self, node):
        """ This is the heuristic. It gets a node (not a state)
        and returns a goal distance estimate"""
        
        # We calculate the number of steps by how many pour and load actions the robots need.
        # And then we add we the maximum distance of all the robots needs to do to water all the plants.

        robots, taps, plants = node.state

        # First le'ts  calculate the cost of all pour and load operations the robots needs to do

        total_water_to_deliver = 0
        plants_needing_water_pos = []

        # Go over all the plants checks how much water the plants need and what is their pos
        for plant in plants:            
            if plant[2] > 0:
                total_water_to_deliver += plant[2]
                plants_needing_water_pos.append((plant[0], plant[1]))

        # Check if we in goal state
        if total_water_to_deliver == 0:
            return 0                
        
        sum_water_on_robots = 0
        for robot in robots:
            sum_water_on_robots = sum_water_on_robots + robot[3]

        cost_of_pour_actions = total_water_to_deliver
        cost_of_load_actions = total_water_to_deliver - sum_water_on_robots
        if cost_of_load_actions < 0:
            cost_of_load_actions = 0        

        # Second let's calcualte the cost of all the movement the robots needs to do
        
        taps_with_water = []
        for tap in taps:
            if tap[2] >0:
                taps_with_water.append((tap[0], tap[1]))
        
        # Checks if there is a solution
        if cost_of_load_actions >0 and not taps_with_water:
            return float('inf')
        
        max_min_distance = 0

        for plant_pos in plants_needing_water_pos:
            plant_row, plant_col = plant_pos
            min_distance_for_this_plant = float('inf')

            for robot in robots:
                robot_row, robot_col, robot_load = robot[1], robot[2], robot[3]
                distance_robot_to_the_plant = abs(robot_row - plant_row) + abs(robot_col - plant_col)

                # If robot has water
                if robot_load > 0:
                    if distance_robot_to_the_plant < min_distance_for_this_plant:
                        min_distance_for_this_plant = distance_robot_to_the_plant 
                else:
                    if taps_with_water:
                        for tap_row, tap_col in taps_with_water:
                            distance_robot_tap = abs(robot_row - tap_row) + abs(robot_col - tap_col)
                            distance_tap_plant = abs(tap_row - plant_row) + abs(tap_col - plant_col)
                            total_trip = distance_robot_tap + distance_tap_plant

                            if total_trip < min_distance_for_this_plant:
                                    min_distance_for_this_plant = total_trip

                                   
            if min_distance_for_this_plant != float('inf'):
                    max_min_distance = max(max_min_distance, min_distance_for_this_plant)

        return cost_of_pour_actions + cost_of_load_actions + max_min_distance




    def h_gbfs(self, node):
        """ This is the heuristic. It gets a node (not a state)
        and returns a goal distance estimate"""
        
        robots, taps, plants = node.state
        
        # Giving big weight to watering plants
        WEIGHT_TOTAL_WATER_NEEDED = 1000  
        # Giving some weight but not to big for empty robots to encourage loading
        WEIGHT_EMPTY_ROBOT_PENALTY = 50 
        # Small weight for distance to target
        WEIGHT_DISTANCE_TO_TARGET = 1 

        # 1. Calculate Total Water Missing (The Main Gradient)
        total_water_units_needed = 0
        plants_needing_water_coordinates = []
        
        for plant in plants:
            plant_row = plant[0]
            plant_col = plant[1]
            plant_needed_amount = plant[2]
            
            if plant_needed_amount > 0:
                total_water_units_needed += plant_needed_amount
                plants_needing_water_coordinates.append((plant_row, plant_col))

        # If we reached goal state
        if total_water_units_needed == 0:
            return 0

        # 2. Calculate Robot Scores
        total_robot_heuristic_score = 0
        
        # We precalculate active taps to avoid re-looping
        taps_with_water_coordinates = []
        for tap in taps:
            tap_row = tap[0]
            tap_col = tap[1]
            tap_amount = tap[2]
            if tap_amount > 0:
                taps_with_water_coordinates.append((tap_row, tap_col))

        for robot in robots:
            robot_row = robot[1]
            robot_col = robot[2]
            robot_load = robot[3]
            
            # If robot has water it should go to the closest plant that needs water
            if robot_load > 0 and plants_needing_water_coordinates:
                # Distance to closest plant that needs water
                minimum_distance = min(
                    abs(robot_row - plant_target_row) + abs(robot_col - plant_target_col) 
                    for (plant_target_row, plant_target_col) in plants_needing_water_coordinates
                )
                total_robot_heuristic_score += (minimum_distance * WEIGHT_DISTANCE_TO_TARGET)

            # If robot has not ware it shold go to the closest tap that has water
            elif robot_load == 0:
                # We add penatly for robot being empty to encourage loading
                total_robot_heuristic_score += WEIGHT_EMPTY_ROBOT_PENALTY
                
                if taps_with_water_coordinates:
                    # Distance to closest tap that has water
                    minimum_distance = min(
                        abs(robot_row - tap_target_row) + abs(robot_col - tap_target_col) 
                        for (tap_target_row, tap_target_col) in taps_with_water_coordinates
                    )
                    total_robot_heuristic_score += (minimum_distance * WEIGHT_DISTANCE_TO_TARGET)
                else:
                    # We got to a dead end so we add a big penatly to avoid this branch
                    total_robot_heuristic_score += 10000

        # Final heuristic value
        return (total_water_units_needed * WEIGHT_TOTAL_WATER_NEEDED) + total_robot_heuristic_score



def create_watering_problem(game):
    print("<<create_watering_problem")
    """ Create a pressure plate problem, based on the description.
    game - tuple of tuples as described in pdf file"""
    return WateringProblem(game)


if __name__ == '__main__':
    ex1_check.main()
