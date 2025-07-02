from typing import Optional, List

from .runtime_info import RuntimeInfo


def main(argv: Optional[List[str]] = None) -> None:
    """Command line interface for displaying RuntimeInfo."""
    import argparse

    parser = argparse.ArgumentParser(description="Show RuntimeInfo")
    parser.add_argument("path", nargs="?", help="Optional path", default=None)
    parser.add_argument("--json", action="store_true", help="Output canonical JSON")
    args = parser.parse_args(argv)

    info = RuntimeInfo(args.path)
    if args.json:
        print(info.to_json())
    else:
        print(str(info))
