import asyncio


coroutines = []
obstacles = []
obstacles_in_last_collisions = []
year = 1956
PHRASES = {
    1957: "First Sputnik",
    1961: "Gagarin flew!",
    1969: "Armstrong got on the moon!",
    1971: "First orbital space station Salute-1",
    1981: "Flight of the Shuttle Columbia",
    1998: 'ISS start building',
    2011: 'Messenger launch to Mercury',
    2020: "Take the plasma gun! Shoot the garbage!",
}


def get_garbage_delay_tics(year):
    if year < 1961:
        return None
    elif year < 1969:
        return 20
    elif year < 1981:
        return 14
    elif year < 1995:
        return 10
    elif year < 2010:
        return 8
    elif year < 2020:
        return 6
    else:
        return 2


def draw_year(canvas, years):
    rows, _ = canvas.getmaxyx()
    window = canvas.derwin(1, 80, rows - 1, 0)
    window.clear()
    window.addstr(
        0,
        0,
        (
            f'year: {years}'
            if years not in PHRASES
            else f'year: {years}  {PHRASES[years]}'
        )
    )


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)
