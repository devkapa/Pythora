import sys
import textwrap
import logic
import colorama
from movement.map import choose_map, get_map
from colorama import Fore

colorama.init()


def main():
    args = sys.argv[1:]

    title = textwrap.dedent(f"""
                Hello. Welcome to
                                    
                       d8888 888    888
                      d88888 888    888
                     d88P888 888    888
                    d88P 888 888888 88888b.   .d88b.  888d888 8888b.
                   d88P  888 888    888 "88b d88""88b 888P"      "88b
                  d88P   888 888    888  888 888  888 888    .d888888
                 d8888888888 Y88b.  888  888 Y88..88P 888    888  888
                d88P     888  "Y888 888  888  "Y88P"  888    "Y888888  {Fore.YELLOW}py-v1.1.0{Fore.RESET}
                """)

    print(title)

    if len(args) > 0:
        print(f"Loading map from file...")
        logic.start_game(get_map(args[0]))
    else:
        chosen_map = choose_map()
        if chosen_map is not None:
            logic.start_game(get_map(chosen_map))

    input("Press 'Enter' to exit...")


if __name__ == '__main__':
    main()
