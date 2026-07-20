import argparse
from pathlib import Path

from shop_floor.lifecycle import ShopCloseError, ShopOpenError, ShopRunner


def main() -> int:
    parser = argparse.ArgumentParser(description="Open or close the local shop-floor service.")
    parser.add_argument("command", choices=("open", "close"))
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--state-file", type=Path)
    arguments = parser.parse_args()
    runner = ShopRunner(port=arguments.port, state_file=arguments.state_file)

    if arguments.command == "open":
        try:
            print(f"Shop is open: {runner.open()}")
        except ShopOpenError as error:
            print(str(error))
            return 1
    else:
        try:
            if runner.close():
                print("Shop is closed.")
            else:
                print("Shop is already closed.")
        except ShopCloseError as error:
            print(str(error))
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
