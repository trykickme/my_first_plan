"""Offline teaching experiments. Python 3.9+; standard library only."""
import argparse
import base64
import hashlib
import hmac
import html
import ipaddress
import json
import sqlite3
import struct
from pathlib import Path


def output(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def bytes_demo(_):
    text = "AЯ\n"
    raw = text.encode("utf-8")
    output({"text": text, "characters": len(text), "bytes": len(raw),
            "hex": raw.hex(" "), "roundtrip": raw.decode("utf-8"),
            "little_endian_0x12345678": struct.pack("<I", 0x12345678).hex(" ")})


def parse_service(line):
    name, separator, port = line.strip().partition(":")
    if not separator or not name or not port.isascii() or not port.isdecimal():
        raise ValueError("expected name:decimal_port")
    number = int(port)
    if not 1 <= number <= 65535:
        raise ValueError("port outside 1..65535")
    return {"name": name, "port": number}


def ports(args):
    lines = Path(args.file).read_text(encoding="utf-8").splitlines() if args.file else ["web:443", "ssh:22", "bad:0", "bad:no", "missing"]
    for number, line in enumerate(lines, 1):
        try:
            record = {"line": number, "ok": True, "value": parse_service(line)}
        except ValueError as error:
            record = {"line": number, "ok": False, "error": str(error)}
        print(json.dumps(record, ensure_ascii=False))


def digest(_):
    raw, changed, key = b"report=7", b"report=8", b"lab-only-key"
    output({"base64": base64.b64encode(raw).decode("ascii"),
            "sha256_original": hashlib.sha256(raw).hexdigest(),
            "sha256_changed": hashlib.sha256(changed).hexdigest(),
            "mac_matches_original": hmac.compare_digest(hmac.digest(key, raw, "sha256"), hmac.digest(key, raw, "sha256")),
            "mac_matches_changed": hmac.compare_digest(hmac.digest(key, raw, "sha256"), hmac.digest(key, changed, "sha256"))})


def sql(_):
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE reports (owner TEXT, marker TEXT)")
    connection.executemany("INSERT INTO reports VALUES (?, ?)", [("alice", "A"), ("bob", "B")])
    cases = []
    for value in ["alice", "nobody", "alice' OR 1=1 --"]:
        vulnerable = "SELECT marker FROM reports WHERE owner='" + value + "'"
        cases.append({"input": value, "concatenated_query": vulnerable,
                      "concatenated_rows": connection.execute(vulnerable).fetchall(),
                      "bound_rows": connection.execute("SELECT marker FROM reports WHERE owner=?", (value,)).fetchall()})
    output(cases)
    connection.close()


def encode(_):
    value = '<b title="demo">A&B</b>'
    output({"input": value, "html_text_or_quoted_attribute": html.escape(value, quote=True),
            "json_string": json.dumps(value), "note": "JSON encoding is not HTML encoding"})


def auth(_):
    reports = {1: {"owner": "alice", "marker": "A"}, 2: {"owner": "bob", "marker": "B"}}
    rows = []
    for user in [None, "alice", "bob"]:
        for report_id, report in reports.items():
            old = report["marker"] if user is not None else "DENIED"
            fixed = report["marker"] if user == report["owner"] else "DENIED"
            rows.append({"user": user, "report": report_id, "before": old, "after": fixed})
    output(rows)


def race(_):
    # Explicit interleaving: stable demonstration independent of thread timing.
    balance, debit = 10, 7
    read_a, read_b = balance, balance
    stale_final = balance - debit - debit if read_a >= debit and read_b >= debit else balance
    serial_balance = balance
    accepted = 0
    for _ in range(2):
        if serial_balance >= debit:
            serial_balance -= debit
            accepted += 1
    output({"initial": balance, "debit": debit, "stale_checks_final": stale_final,
            "serial_final": serial_balance, "serial_accepted": accepted,
            "invariant": "balance >= 0"})


def framing(_):
    chunks, pending, messages = [b"HE", b"LLO\nW", b"ORLD\n"], b"", []
    for chunk in chunks:
        pending += chunk
        while b"\n" in pending:
            message, pending = pending.split(b"\n", 1)
            messages.append(message.decode("ascii"))
    output({"chunks": [part.decode("ascii") for part in chunks], "messages": messages, "remainder": pending.decode("ascii")})


def graph(_):
    edges = [{"from": "alice", "to": "lab-script", "operation": "write", "confirmed": True},
             {"from": "lab-script", "to": "lab-admin", "operation": "consumed_as_code", "confirmed": False}]
    output({"edges": edges, "complete_path": all(edge["confirmed"] for edge in edges),
            "missing_evidence": "execution trigger and consumer identity"})


def addresses(_):
    network = ipaddress.ip_interface("192.168.10.77/26")
    observed, symbol_offset = 0x7F0012345000, 0x45000
    output({"network": str(network.network.network_address), "broadcast": str(network.network.broadcast_address),
            "num_addresses": network.network.num_addresses,
            "library_base_model": hex(observed-symbol_offset),
            "second_symbol_model": hex(observed-symbol_offset+0x1234),
            "rva_example": hex(0x140002100-0x140000000),
            "file_offset_example": hex(0x2100-0x2000+0x400)})


def heap(_):
    # Object-lifetime model, not an allocator implementation.
    objects, handle = {1: {"generation": 1, "value": "A", "live": True}}, (1, 1)
    objects[1]["live"] = False
    after_delete = objects[handle[0]]["live"]
    objects[1] = {"generation": 2, "value": "B", "live": True}
    output({"old_handle": handle, "live_after_delete": after_delete,
            "naive_reused_read": objects[handle[0]]["value"],
            "generation_checked_read": "DENIED" if handle[1] != objects[handle[0]]["generation"] else objects[1]["value"],
            "scope": "logical model; no promises about real malloc addresses"})


def triage(_):
    old = lambda length, capacity: length <= capacity
    fixed = lambda length, capacity: length < capacity
    output([{"length": length, "capacity": 8, "old_accepts": old(length, 8),
             "fixed_accepts": fixed(length, 8), "reason": "one byte reserved for string terminator"}
            for length in [0, 7, 8, 9]])


def events(_):
    events = [{"id": "control", "action": "file_open", "marker": "LAB_CONTROL"},
              {"id": "test", "action": "file_open", "marker": "LAB_TEST"}]
    rule = lambda event: event["action"] == "file_open" and event["marker"] == "LAB_TEST"
    output({"events": events, "alerts": [event["id"] for event in events if rule(event)],
            "negative_control": rule(events[0])})


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    sub = parser.add_subparsers(dest="experiment", required=True)
    experiments = {"bytes": bytes_demo, "ports": ports, "digest": digest, "sql": sql,
                   "encode": encode, "auth": auth, "race": race, "framing": framing,
                   "graph": graph, "addresses": addresses, "heap": heap, "triage": triage, "events": events}
    for name, function in experiments.items():
        child = sub.add_parser(name)
        if name == "ports":
            child.add_argument("--file", help="UTF-8 service records, one name:port per line")
        child.set_defaults(function=function)
    args = parser.parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
