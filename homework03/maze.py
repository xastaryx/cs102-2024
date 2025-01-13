from copy import deepcopy
from random import choice, randint
from typing import List, Optional, Tuple, Union

import pandas as pd


def create_grid(rows: int = 15, cols: int = 15) -> List[List[Union[str, int]]]:
    return [["■"] * cols for _ in range(rows)]


def remove_wall(grid: List[List[Union[str, int]]], coord: Tuple[int, int]) -> (
List)[List[Union[str, int]]]:
    """

    :param grid:
    :param coord:
    :return:
    """

    x, y, col, row = coord[0], coord[1], len(grid) - 1, len(grid[0]) - 1
    directions = ["up", "right"]
    direction = choice(directions)
    if direction == "up" and 0 <= x - 2 < col and 0 <= y < row:
        grid[x - 1][y] = " "
    else:
        direction = "right"
    if direction == "right" and 0 <= x < col and 0 <= y + 2 < row:
        grid[x][y + 1] = " "
    elif (direction == "right") and ((0 <= x - 2 < col) and (0 <= y < row)):
        grid[x - 1][y] = " "
    return grid


def bin_tree_maze(rows: int = 15, cols: int = 15, random_exit: bool = True) -> (
List)[List[Union[str, int]]]:
    """

    :param rows:
    :param cols:
    :param random_exit:
    :return:
    """

    grid = create_grid(rows, cols)
    empty_cells = []
    for x, row in enumerate(grid):
        for y, _ in enumerate(row):
            if x % 2 == 1 and y % 2 == 1:
                grid[x][y] = " "
                empty_cells.append((x, y))

    # 1. выбрать любую клетку
    # 2. выбрать направление: наверх или направо.
    # Если в выбранном направлении следующая клетка лежит за границами поля,
    # выбрать второе возможное направление
    # 3. перейти в следующую клетку, сносим между клетками стену
    # 4. повторять 2-3 до тех пор, пока не будут пройдены все клетки

    while empty_cells:
        x, y = empty_cells.pop(0)
        remove_wall(grid, (x, y))

    # генерация входа и выхода
    if random_exit:
        x_in, x_out = randint(0, rows - 1), randint(0, rows - 1)
        y_in = randint(0, cols - 1) if x_in in (0, rows - 1) else choice((0, cols - 1))
        y_out = randint(0, cols - 1) if x_out in (0, rows - 1) else choice((0, cols - 1))
    else:
        x_in, y_in = 0, cols - 2
        x_out, y_out = rows - 1, 1

    grid[x_in][y_in], grid[x_out][y_out] = "X", "X"

    return grid


def get_exits(grid: List[List[Union[str, int]]]) -> List[Tuple[int, int]]:
    """

    :param grid:
    :return:
    """

    exits = [(x, y) for x, row in enumerate(grid) for y, _ in enumerate(row) if grid[x][y] == "X"]
    return exits


def make_step(grid: List[List[Union[str, int]]], k: int) -> List[List[Union[str, int]]]:
    """

    :param grid:
    :param k:
    :return:
    """

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for x, row in enumerate(grid):
        for y, cell in enumerate(row):
            if cell == k:
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny] == 0:
                        grid[nx][ny] = k + 1
    return grid


def shortest_path(
    grid: List[List[Union[str, int]]], exit_coord: Tuple[int, int]
) -> Optional[Union[Tuple[int, int], List[Tuple[int, int]]]]:
    """

    :param grid:
    :param exit_coord:
    :return:
    """

    k = 0
    x_exit, y_exit = exit_coord

    while grid[x_exit][y_exit] == 0:
        k += 1
        grid = make_step(grid, k)
    path = [exit_coord]
    k = int(grid[x_exit][y_exit])
    x, y = exit_coord

    while grid[x][y] != 1 and k > 0:
        if (x + 1 < len(grid)) and (grid[x + 1][y] == k - 1):
            x += 1
        elif (x - 1 >= 0) and (grid[x - 1][y] == k - 1):
            x -= 1
        elif (y + 1 < len(grid[0])) and (grid[x][y + 1] == k - 1):
            y += 1
        elif (y - 1 >= 0) and (grid[x][y - 1] == k - 1):
            y -= 1
        else:
            break
        path.append((x, y))
        k -= 1

    if len(path) != grid[exit_coord[0]][exit_coord[1]]:
        grid[path[-1][0]][path[-1][1]] = " "
        path.pop()

        if path:
            x, y = path[-1]
            shortest_path(grid, (x, y))

    return path


def encircled_exit(grid: List[List[Union[str, int]]], coord: Tuple[int, int]) -> bool:
    """

    :param grid:
    :param coord:
    :return:
    """

    x, y = coord
    rows, cols = len(grid), len(grid[0])
    if (x in (0, rows - 1) and y in (0, cols - 1)) or (x - 1 == 0 and y + 1 == cols - 1):
        return True
    if x == 0 and y in range(0, cols) and grid[x + 1][y] == "■":
        return True
    if x == rows - 1 and y in range(0, cols) and grid[x - 1][y] == "■":
        return True
    if y == 0 and x in range(0, rows) and grid[x][y + 1] == "■":
        return True
    if y == cols - 1 and x in range(0, rows) and grid[x][y - 1] == "■":
        return True
    return False


def solve_maze(
    grid: List[List[Union[str, int]]],
) -> Tuple[List[List[Union[str, int]]], Optional[Union[Tuple[int, int], List[Tuple[int, int]]]]]:
    """

    :param grid:
    :return:
    """

    exits = get_exits(grid)
    if len(exits) > 1:
        if encircled_exit(grid, exits[0]) or encircled_exit(grid, exits[1]):
            return grid, None
        new_grid = deepcopy(grid)
        x_in, y_in = exits[0]
        grid[x_in][y_in] = 1
        for x, row in enumerate(grid):
            for y, _ in enumerate(row):
                if grid[x][y] == " " or grid[x][y] == "X":
                    grid[x][y] = 0
        path = shortest_path(grid, exits[1])
        return new_grid, path
    path = exits
    return grid, path


def add_path_to_grid(
    grid: List[List[Union[str, int]]], path: Optional[Union[Tuple[int, int], List[Tuple[int, int]]]]
) -> List[List[Union[str, int]]]:
    """

    :param grid:
    :param path:
    :return:
    """

    if path:
        for i, row in enumerate(grid):
            for j, _ in enumerate(row):
                if (i, j) in path:
                    grid[i][j] = "X"
    return grid


if __name__ == "__main__":
    print(pd.DataFrame(bin_tree_maze(15, 15)))
    GRID = bin_tree_maze(15, 15)
    print(pd.DataFrame(GRID))
    NEWGRID, PATH = solve_maze(GRID)
    MAZE = add_path_to_grid(NEWGRID, PATH)
    print(pd.DataFrame(MAZE))
