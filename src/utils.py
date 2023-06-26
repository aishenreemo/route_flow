from .config import CELL_SIZE

def percent_val(percentage, size):
    return ((percentage[0] / 100) * size[0], (percentage[1] / 100) * size[1])

def near_vehicles(grid, vector):
    vehicles = []
    cell_x = int(vector.x / CELL_SIZE[0])
    cell_y = int(vector.y / CELL_SIZE[1])
    neighboring_cells = [
        (cell_x - 1, cell_y - 1), (cell_x, cell_y - 1), (cell_x + 1, cell_y - 1),
        (cell_x - 1, cell_y), (cell_x, cell_y), (cell_x + 1, cell_y),
        (cell_x - 1, cell_y + 1), (cell_x, cell_y + 1), (cell_x + 1, cell_y + 1)
    ]

    for cell_key in neighboring_cells:
        if cell_key in grid:
            vehicles.extend(grid[cell_key])

    return vehicles
