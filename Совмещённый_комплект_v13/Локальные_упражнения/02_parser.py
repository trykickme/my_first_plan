"""parse a personal file; no network requests."""
import argparse
import json
import re
import sys
from pathlib import Path


def parse_port(text):
    if not re.fullmatch(r"[0-9]+", text):
        raise ValueError("port must contain ASCII digits")
    value = int(text)
    if not 1 <= value <= 65535:
        raise ValueError("port must be between 1 and 65535")
    return value


def parse_line(line):
    name, separator, port_text = line.strip().partition(":")
    if not separator:
        raise ValueError("expected name:port")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", name):
        raise ValueError("invalid service name")
    return {"name": name, "port": parse_port(port_text)}


def parse_file(text):
    records, errors = [], []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue  # Empty lines are deliberately allowed by this file grammar.
        try:
            records.append(parse_line(line))
        except ValueError as error:
            errors.append({"line": number, "error": str(error)})
    return {"records": records, "errors": errors}


def self_test():
    assert parse_line("ssh:22") == {"name": "ssh", "port": 22}
    assert parse_line("edge:65535")["port"] == 65535
    for bad in ["edge:65536", "broken", "web:abc", "web:0"]:
        try:
            parse_line(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid input accepted: " + bad)
    result = parse_file("ssh:22\n\nweb:abc\n")
    assert len(result["records"]) == 1
    assert result["errors"][0]["line"] == 3
    print("Self-test passed: valid input, boundary, errors, line numbers.")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--input", type=Path, help="UTF-8 file with name:port lines")
    cli.add_argument("--output", type=Path, help="optional JSON destination")
    cli.add_argument("--self-test", action="store_true")
    args = cli.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.input is None:
        cli.error("--input is required unless --self-test is used")
    try:
        result = parse_file(args.input.read_text(encoding="utf-8"))
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except (OSError, UnicodeError) as error:
        print("File error:", error, file=sys.stderr)
        return 2
    for error in result["errors"]:
        print(f"Line {error['line']}: {error['error']}", file=sys.stderr)
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
