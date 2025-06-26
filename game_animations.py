import random
import curses
import asyncio
from itertools import cycle

from curses_tools import draw_frame, get_frame_size, read_controls
from utils import sleep, coroutines, obstacles, obstacles_in_last_collisions
from obstacles import Obstacle
from phisics import update_speed
from explosion import explode


async def animate_spaceship(canvas, start_row, start_column, animation):
    row = start_row
    column = start_column
    rows, columns = canvas.getmaxyx()
    frame_rows, frame_columns = get_frame_size(animation[0])
    raw_speed = column_speed = 0
    for item in cycle(animation):
        for _ in range(2):
            controls_row, controls_column, space_pressed = read_controls(canvas)
            raw_speed, column_speed = update_speed(
                raw_speed, column_speed, controls_row, controls_column)
            row = max(
                0,
                min(row + controls_row + raw_speed, rows - frame_rows)
            )
            column = max(
                0,
                min(
                    column + controls_column + column_speed,
                    columns - frame_columns
                )
            )

            draw_frame(canvas, row, column, item)

            if space_pressed:
                coroutines.append(
                    fire(
                        canvas,
                        row,
                        column + frame_columns // 2,
                        rows_speed=-2
                    )
                )

            await asyncio.sleep(0)
            draw_frame(canvas, row, column, item, negative=True)
            for obstacle in obstacles:
                if obstacle.has_collision(
                        row, column, frame_rows, frame_columns):
                    rows_center = row + frame_rows // 2
                    columns_center = column + frame_columns // 2
                    coroutines.append(
                        explode(canvas, rows_center, columns_center))
                    coroutines.append(show_gameover(canvas))
                    return


async def blink(canvas, row, column, offset_tics, symbols='+*.:'):
    symbol = random.choice(symbols)
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)
        await sleep(offset_tics)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                return


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()
    frame_rows, frame_columns = get_frame_size(garbage_frame)

    column = max(column, 0)
    column = min(column, columns_number - 1)
    row = 0

    obstacle = Obstacle(row, column, frame_rows, frame_columns)
    obstacles.append(obstacle)

    try:
        while row < rows_number:
            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            obstacle.row = row
            if obstacle in obstacles_in_last_collisions:
                obstacles_in_last_collisions.remove(obstacle)
                rows_center = row + frame_rows // 2
                columns_center = column + frame_columns // 2
                await explode(canvas, rows_center, columns_center)
                break
    finally:
        obstacles.remove(obstacle)


async def show_gameover(canvas):
    rows_number, columns_number = canvas.getmaxyx()
    text = """
 ██████   █████  ███    ███ ███████      ██████  ██    ██ ███████ ██████  
██       ██   ██ ████  ████ ██          ██    ██ ██    ██ ██      ██   ██ 
██   ███ ███████ ██ ████ ██ █████       ██    ██ ██    ██ █████   ██████  
██    ██ ██   ██ ██  ██  ██ ██          ██    ██  ██  ██  ██      ██   ██ 
 ██████  ██   ██ ██      ██ ███████      ██████    ████   ███████ ██   ██ 
"""
    frame_rows, frame_columns = get_frame_size(text)
    start_row = (rows_number - frame_rows) // 2
    start_column = (columns_number - frame_columns) // 2
    while True:
        draw_frame(canvas, start_row, start_column, text)
        await sleep()
