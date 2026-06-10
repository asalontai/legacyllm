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
        print("modelguard CLI")
        print("  python -m modelguard params [provider]   show parameters")
        print("  python -m modelguard models [provider]   list current models")
        print("  python -m modelguard update              refresh model lists")


if __name__ == "__main__":
    main()
