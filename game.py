import curses
import random
import os
from time import sleep

from game_animations import blink, animate_spaceship, fire
from curses_tools import get_frame_size, read_controls


TIC_TIMEOUT = 0.1


def generate_unique_coords(max_y, max_x, count):
    all_cells = [
        (row, column) for row in range(max_y) for column in range(max_x)
    ]
    return random.sample(all_cells, count)


def main(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    max_y, max_x = curses.window.getmaxyx(canvas)
    stars_count = random.randint(70, 90)
    stars_offset_tics = [random.randint(1, 20) for _ in range(stars_count)]
    coords = generate_unique_coords(max_y, max_x, stars_count)

    rocket_animation = []
    for filename in os.listdir('rocket_animation'):
        file_path = os.path.join('rocket_animation', filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            rocket_animation.append(text)

    controls = {'row': 0, 'column': 0}
    frame_rows, frame_columns = get_frame_size(rocket_animation[0])

    coroutines = [
        blink(canvas, row, column, offset_tics)
        for (row, column), offset_tics in zip(coords, stars_offset_tics)
    ]
    coroutines.append(fire(canvas, max_y//2, max_x//2))
    coroutines.append(animate_spaceship(
        canvas,
        (max_y - frame_rows) // 2,
        (max_x - frame_columns) // 2,
        rocket_animation,
        controls
    ))
    while True:
        row, column, _ = read_controls(canvas)
        if (frame_rows + row) < max_y and (frame_rows + row) > 0:
            controls['row'] = row
        if (frame_columns + column) < max_x and (frame_columns + column) > 0:
            controls['column'] = column
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(main)
