import logging
from typing import List, Optional
from config import Cell


def print_layout(layout: List[List[Cell]], file: str, bot_start_location: Optional[List[int]] = None, title: Optional[str] = "", mode: str = "w") -> None:
    """Prints out the current state of the layout to a specified file"""

    if not layout:
        logging.error("Attempted to print an empty layout")
        return

    output_file = None
    try:
        output_file = open(file, mode)
        output = f"{title}\n" if title else ""

        for r in range(len(layout)):
            for c in range(len(layout)):
                if bot_start_location and (r, c) == bot_start_location:
                    output += f"{Cell.BOT.value}, "
                else:
                    output += f"{layout[r][c].value}, "

            output = output.rsplit(", ", 1)[0]
            if r != len(layout) - 1:
                output += "\n"

        output_file.write(f"{output}\n")
        output_file.close()
    except IOError:
        logging.exception(f"Unable to write to output file to '{file}'")
