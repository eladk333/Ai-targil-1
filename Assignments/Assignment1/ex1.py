import ex1_check
import search
import utils

id = ["322587064"]





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
        
        # We make the heuristic estimate to be: 1. the unit of water plants still need + 2. how much the robots needs to load to get it + 3. how much a robots need to travel to it's closest target

        robots, taps, plants = node.state

        total_water_needed = sum(p[2] for p in plants)
        current_robot_holding = sum(r[3] for r in robots)

        if total_water_needed == 0:
            return 0
        
        # 1. How much water the plants still need
        cost = total_water_needed

        # 2. How much water the robots need to load
        total_need_load = max(0, total_water_needed - current_robot_holding)
        cost += total_need_load
        
        # 3. how much a robots need to travel to it's closest target
        min_distance = float('inf')
        
        thirsty_plants = []
        for p in plants:
            if p[2] > 0:
                thirsty_plants.append(p)
        
        filled_taps = []
        for t in taps:
            if t[2] > 0:
                filled_taps.append(t)
        
        # If robot has water his distance is to the closests thirdsty plant
        robots_with_water = []
        for robot in robots:
            # r is (id, row, col, load) -> index 3 is load
            if robot[3] > 0:
                robots_with_water.append(robot)
        
        # Checks we actually atleast a robot and a plant for this case
        if len(robots_with_water) > 0 and len(thirsty_plants) > 0:
            for robot in robots_with_water:
                robot_pos = (robot[1], robot[2])
                for plant in thirsty_plants:
                    plant_pos = (plant[0], plant[1])
                    # We do Manhattan distance cause we in grid
                    dist = abs(robot_pos[0] - plant_pos[0]) + abs(robot_pos[1] - plant_pos[1])
                    if dist < min_distance:
                        min_distance = dist

        # If no robot has water                  
        robots_without_water = []
        for robot in robots:            
            if robot[3] == 0:
                robots_without_water.append(robot)
       
        # Just to be safe
        if robots_without_water and filled_taps and thirsty_plants:
             for robot in robots_without_water:
                robot_pos = (robot[1], robot[2])
                
                # Find closest tap to this robot
                dist_to_tap = float('inf')
                best_tap_pos = None
                
                # Find closest tap to this robot
                for tap in filled_taps:
                    tap_pos = (tap[0], tap[1])
                    # We do Manhattan distance cause we in grid
                    distance = abs(robot_pos[0] - tap_pos[0]) + abs(robot_pos[1] - tap_pos[1])
                    if distance < dist_to_tap:
                        dist_to_tap = distance
                        best_tap_pos = tap_pos
                
                # Find closest plant to that specific tap
                if best_tap_pos:
                    dist_tap_to_plant = float('inf')
                    for plant in thirsty_plants:
                        plant_pos = (plant[0], plant[1])
                        distance = abs(best_tap_pos[0] - plant_pos[0]) + abs(best_tap_pos[1] - plant_pos[1])
                        if distance < dist_tap_to_plant:
                            dist_tap_to_plant = distance
                    
                    total_trip = dist_to_tap + dist_tap_to_plant
                    if total_trip < min_distance:
                        min_distance = total_trip
        
        if min_distance != float('inf'):
            cost += min_distance
            
        return cost
        

    def h_gbfs(self, node):
        """ This is the heuristic. It gets a node (not a state)
        and returns a goal distance estimate"""
        
        weight = 10
        robots, taps, plants = node.state

        total_water_needed = sum(p[2] for p in plants)
        if total_water_needed == 0:
            return 0
        
        score = total_water_needed * weight

        min_distance = float('inf')
        thirsty_plants = [p for p in plants if p[2] > 0]
        robots_with_water = [r for r in robots if r[3] > 0]
        filled_taps = [t for t in taps if t[2] > 0]

        # If we have water, how far is the plant?
        if robots_with_water:
            for r in robots_with_water:
                for p in thirsty_plants:
                    d = abs(r[1] - p[0]) + abs(r[2] - p[1])
                    if d < min_distance:
                        min_distance = d
        
        # If we don't have water, how far is the tap?
        # (Simplified: just get to a tap!)
        else:
            for r in robots:
                for t in filled_taps:
                    d = abs(r[1] - t[0]) + abs(r[2] - t[1])
                    if d < min_dist:
                        min_dist = d
        
        if min_dist != float('inf'):
            score += min_dist

        return score



def create_watering_problem(game):
    print("<<create_watering_problem")
    """ Create a pressure plate problem, based on the description.
    game - tuple of tuples as described in pdf file"""
    return WateringProblem(game)


if __name__ == '__main__':
    ex1_check.main()
