import curses
import random
import os
import time

from game_animations import blink, animate_spaceship, fly_garbage
from curses_tools import get_frame_size
from utils import sleep, get_garbage_delay_tics, draw_year, coroutines, year


TIC_TIMEOUT = 0.1


def generate_unique_coords(max_y, max_x, count):
    all_cells = [
        (row, column) for row in range(max_y) for column in range(max_x)
    ]
    return random.sample(all_cells, count)


async def time_control(canvas):
    global year
    while True:
        year += 1
        draw_year(canvas, year)
        await sleep(15)


async def fill_orbit_with_garbage(canvas, trash_frames):
    _, columns = canvas.getmaxyx()
    while True:
        tics = get_garbage_delay_tics(year)
        if not tics:
            await sleep(5)
            continue
        trash_count = random.randint(1, 3)
        frames = random.choices(trash_frames, k=trash_count)
        for frame in frames:
            coroutines.append(
                fly_garbage(
                    canvas,
                    random.randint(1, columns),
                    frame
                )
            )
        await sleep(tics)


def main(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    max_y, max_x = curses.window.getmaxyx(canvas)
    stars_count = random.randint(70, 90)
    stars_offset_tics = [random.randint(1, 20) for _ in range(stars_count)]
    coords = generate_unique_coords(max_y, max_x, stars_count)

    rocket_animation = []
    trash_frames = []
    for path, _, filenames in os.walk('frames'):
        for filename in filenames:
            with open(os.path.join(path, filename), encoding='utf-8') as f:
                text = f.read()
                if filename.startswith('rocket_frame'):
                    rocket_animation.append(text)
                else:
                    trash_frames.append(text)

    frame_rows, frame_columns = get_frame_size(rocket_animation[0])

    coroutines.extend(
        blink(canvas, row, column, offset_tics)
        for (row, column), offset_tics in zip(coords, stars_offset_tics)
    )
    coroutines.append(animate_spaceship(
        canvas,
        (max_y - frame_rows) // 2,
        (max_x - frame_columns) // 2,
        rocket_animation
    ))
    coroutines.append(fill_orbit_with_garbage(canvas, trash_frames))
    coroutines.append(time_control(canvas))
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(main)
