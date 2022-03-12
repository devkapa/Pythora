import textwrap
import logic
from map.map import choose_map, get_map


def main():
    title = textwrap.dedent("""
                Hello. Welcome to
                                    
                       d8888 888    888
                      d88888 888    888
                     d88P888 888    888
                    d88P 888 888888 88888b.   .d88b.  888d888 8888b.
                   d88P  888 888    888 "88b d88""88b 888P"      "88b
                  d88P   888 888    888  888 888  888 888    .d888888
                 d8888888888 Y88b.  888  888 Y88..88P 888    888  888
                d88P     888  "Y888 888  888  "Y88P"  888    "Y888888          
                """)

    print(title)

    logic.start_game(get_map(choose_map()))


if __name__ == '__main__':
    main()
