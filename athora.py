import os.path
import sys
import textwrap
import logic

from console.console import Console
from console.colors import blue
from movement.map import choose_map, get_map
import requests
import pyi_splash


def main():
    # Version
    v = "GUI-v3.0.2"

    # Get command line args
    args = sys.argv[1:]

    # Print game title
    title = textwrap.dedent(f"""
                Hello. Welcome to
                                    
                       d8888 888    888
                      d88888 888    888
                     d88P888 888    888
                    d88P 888 888888 88888b.   .d88b.  888d888 8888b.
                   d88P  888 888    888 "88b d88""88b 888P"      "88b
                  d88P   888 888    888  888 888  888 888    .d888888
                 d8888888888 Y88b.  888  888 Y88..88P 888    888  888
                d88P     888  "Y888 888  888  "Y88P"  888    "Y888888  {blue}{v}
                """)

    console = Console(f"Athora {v}")

    pyi_splash.close()

    console.wrap(title)

    # Check for updates from GitHub - if this version doesn't match the latest version
    # If there is no internet, print error but run game
    try:
        response = requests.get("https://api.github.com/repos/Nulfy/Pythora/releases/latest", timeout=3)
        if response.json()["tag_name"] != v:
            console.wrap(f"{blue}There is a new version available! Download it at"
                         f"\nhttps://github.com/Nulfy/Pythora/releases/latest")
    except requests.ConnectionError:
        console.wrap(f"{blue}No internet connection, cannot check for updates.")
    except requests.Timeout:
        pass

    while True:
        # Check if a map was provided in CMD args, and if so, start the game with that map.
        # Otherwise, allow the user to choose a map.
        if len(args) > 0:
            print(f"Loading map from file...")
            logic.start_game(get_map(args[0]), console)
            args.clear()
        else:
            # Find the application folder, respective to the executable this is running in
            if getattr(sys, 'frozen', False):
                maps_path = os.path.dirname(sys.executable)
                os.chdir(maps_path)
            else:
                maps_path = os.path.dirname(os.path.realpath(__file__))
            # Let the user choose a map from the application's map folder
            chosen_map = choose_map(maps_path, console)
            if chosen_map is not None:
                logic.start_game(get_map(chosen_map), console)
            else:
                break


if __name__ == '__main__':
    main()
