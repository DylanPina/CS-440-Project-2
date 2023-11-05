from collections import defaultdict


def floyd_warshall(grid):
    D = len(grid)

    # Initialize the distances
    dist = defaultdict(dict)
    for i in range(D):
        for j in range(D):
            if grid[i][j] == 1:  # Open cell
                for r in range(D):
                    for c in range(D):
                        if grid[r][c] == 1:
                            dist[(i, j)][(r, c)] = float('inf')
                dist[(i, j)][(i, j)] = 0  # Distance to self is 0

    # Set initial distances for adjacent cells
    for i in range(D):
        for j in range(D):
            if grid[i][j] == 1:  # Open cell
                for dr, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Directions: up, down, left, right
                    ni, nj = i + dr, j + dy
                    if ni in range(D) and nj in range(D) and grid[ni][nj] == 1:
                        dist[(i, j)][(ni, nj)] = 1  # Distance to adjacent open cells

    # Floyd-Warshall algorithm
    for k in range(D):
        for l in range(D):
            if (k, l) in dist:  # Intermediate point
                for i in range(D):
                    for j in range(D):
                        if (i, j) in dist:  # Start point
                            for m in range(D):
                                for n in range(D):
                                    if (m, n) in dist:  # End point
                                        # Update the distance with the minimum value
                                        dist[(i, j)][(m, n)] = min(dist[(i, j)][(m, n)],
                                                                    dist[(i, j)][(k, l)] + dist[(k, l)][(m, n)])

    return dist

# Erample usage
D = 4
grid = [
    [1, 1, 1, 1],
    [1, 1, 0, 1],
    [0, 1, 1, 0],
    [1, 0, 1, 1]
]

shortest_paths = floyd_warshall(grid)
for key, value in shortest_paths.items():
    print(f"From {key}:")
    for target, distance in value.items():
        if distance != float('inf'):
            print(f"  To {target}: {distance}")
