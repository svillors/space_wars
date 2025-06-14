import random
import curses
import asyncio
from itertools import cycle

from curses_tools import draw_frame, get_frame_size


async def animate_spaceship(canvas, start_row, start_column, animation, controls):
    row = start_row
    column = start_column
    rows, columns = canvas.getmaxyx()
    frame_rows, frame_columns = get_frame_size(animation[0])
    for item in cycle(animation):
        row += controls['row']
        column += controls['column']

        row = max(0, min(row, rows - frame_rows))
        column = max(0, min(column, columns - frame_columns))

        draw_frame(canvas, row, column, item)
        for _ in range(2):
            await asyncio.sleep(0)
        draw_frame(canvas, row, column, item, negative=True)


async def blink(canvas, row, column, offset_tics, symbols='+*.:'):
    symbol = random.choice(symbols)
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        for _ in range(offset_tics):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


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
