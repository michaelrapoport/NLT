"""Command-line interface for NLT."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from nlt.prd import parse_prd_file
from nlt.server import serve


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NLT PRD tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_parser = subparsers.add_parser("parse", help="Parse a Markdown PRD and print JSON")
    parse_parser.add_argument("prd", help="Path to the Markdown PRD")

    serve_parser = subparsers.add_parser("serve", help="Serve parsed PRD features over HTTP")
    serve_parser.add_argument("prd", nargs="?", help="Optional path to the Markdown PRD")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind")
    serve_parser.add_argument("--port", default=8000, type=int, help="Port to bind")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "parse":
        document = parse_prd_file(args.prd)
        print(json.dumps(document.as_dict(), indent=2, sort_keys=True))
        return 0

    if args.command == "serve":
        serve(args.host, args.port, prd_path=args.prd)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
