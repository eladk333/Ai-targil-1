import time
import ex1
import search

# ==========================================
# 1. THE VISUALIZER FUNCTION
# ==========================================
def print_grid(problem, state, action_taken=None, step_num=0):
    """
    Prints a beautiful ASCII representation of the game state.
    """
    robots, taps, plants = state
    rows, cols = problem.rows, problem.cols

    # Create empty grid
    grid = [[" .  " for _ in range(cols)] for _ in range(rows)]

    # --- LAYERS ---

    # 1. Walls (Bottom layer)
    for w in problem.walls:
        grid[w[0]][w[1]] = "####"

    # 2. Taps (Middle layer)
    # Format: T:amount
    for t in taps:
        r, c, amount = t
        grid[r][c] = f"T:{amount:<2}"

    # 3. Plants (Middle layer)
    # Format: P:needed
    for p in plants:
        r, c, needed = p
        # If a plant is satisfied (0 needed), we can mark it differently (optional)
        symbol = f"P:{needed:<2}" if needed > 0 else "DONE"
        grid[r][c] = symbol

    # 4. Robots (Top layer - overlays everything)
    # Format: R{id}
    for robot in robots:
        r_id, r_r, r_c, r_load = robot
        # Check if multiple robots are on same cell (shouldn't happen in valid state)
        current_text = grid[r_r][r_c]
        
        # Visual indication if robot is carrying water
        load_marker = "*" if r_load > 0 else " "
        grid[r_r][r_c] = f"R{r_id}{load_marker}"

    # --- PRINTING ---
    
    print(f"\n=== STEP {step_num} " + ("=" * 20))
    if action_taken:
        print(f"ACTION: {action_taken}")
    else:
        print("START STATE")
    
    print("-" * (cols * 6))
    for r in range(rows):
        row_str = "|" + "|".join(grid[r]) + "|"
        print(row_str)
    print("-" * (cols * 6))
    
    # Print Detailed Status
    status = []
    for r in robots:
        status.append(f"Robot {r[0]}: Load {r[3]}/{problem.robot_capacities[r[0]]}")
    print("Status: " + " | ".join(status))
    print("=" * 30)


# ==========================================
# 2. THE SOLVER LOGIC (CORRECTED)
# ==========================================
def solve_and_visualize(problem_dict, problem_name="Problem"):
    print(f"\n\n{'#'*40}")
    print(f"Solving {problem_name} with A*...")
    print(f"{'#'*40}\n")

    try:
        # Create the problem instance
        p = ex1.create_watering_problem(problem_dict)
        
        # Run A* Search
        # returns (goal_node, expanded_count) in your specific search.py
        search_result = search.astar_search(p, p.h_astar)

        # Handle the tuple return type specific to your search.py
        if search_result and isinstance(search_result, tuple):
            goal_node = search_result[0] # Extract the node from (node, count)
        else:
            goal_node = search_result # Fallback if it returns just a node

        if goal_node:
            # Reconstruct the path from start to goal
            path_nodes = goal_node.path()
            print(f"Solution Found! Total steps: {len(path_nodes) - 1}")
            print("Playing animation in 2 seconds...")
            time.sleep(2)

            # Iterate through the path and visualize
            for i, node in enumerate(path_nodes):
                print_grid(p, node.state, node.action, i)
                time.sleep(0.8) # Pause to let you watch
            
            print("\n--- PROBLEM SOLVED ---")
        else:
            print("NO SOLUTION FOUND.")
            
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()


# ==========================================
# 3. THE PROBLEMS (From ex1_check.py)
# ==========================================

# Problem 1: Simple (1 Robot, 1 Tap, 1 Plant)
problem1 = {
    "Size":   (3, 3),
    "Walls":  set(),
    "Taps":   {(1, 1): 3},        
    "Plants": {(0, 2): 2},        
    "Robots": {10: (2, 0, 0, 2)},
}

# Problem 2: Walls (Matches your uploaded image)
# 2 Robots, 1 Tap, 2 Plants, Walls in middle
problem2 = {
    "Size":  (3, 3),
    "Walls": {(0, 1), (2, 1)},    
    "Taps":  {(1, 1): 6},         
    "Plants": {(0, 2): 3, (2, 0): 2},
    "Robots": {
        10: (1, 0, 0, 2),         
        11: (1, 2, 0, 2),         
    },
}


# ==========================================
# 4. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # Run Problem 1
    solve_and_visualize(problem1, "Problem 1 (Simple)")
    
    # Run Problem 2
    solve_and_visualize(problem2, "Problem 2 (With Walls)")