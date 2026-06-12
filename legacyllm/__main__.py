import sys


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else None

    if cmd == "update":
        from .updater import update
        update()
    elif cmd == "models":
        from .client import models
        models(args[1] if len(args) > 1 else None)
    elif cmd == "params":
        from .client import params
        params(args[1] if len(args) > 1 else None)
    else:
        print("legacyllm CLI")
        print("  python -m legacyllm params [provider]   show parameters")
        print("  python -m legacyllm models [provider]   list current models")
        print("  python -m legacyllm update              refresh model lists")


if __name__ == "__main__":
    main()
