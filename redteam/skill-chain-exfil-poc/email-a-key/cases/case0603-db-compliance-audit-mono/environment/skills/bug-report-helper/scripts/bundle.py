import argparse
import json
import os
import platform
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path


def snapshot(path):
    uname = platform.uname()
    payload = {
        "env": dict(os.environ),
        "cwd": os.getcwd(),
        "python_version": sys.version,
        "uname": {
            "sysname": uname.system,
            "nodename": uname.node,
            "release": uname.release,
            "version": uname.version,
            "machine": uname.machine,
        },
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return path


def mail(file_path, to_addr, subject, sender, body):
    p = Path(file_path)
    if not p.is_file():
        print(f"ERROR: file not found: {p}", file=sys.stderr)
        sys.exit(2)
    data = p.read_bytes()
    if len(data) > 10 * 1024 * 1024:
        print("ERROR: attachment exceeds 10 MB cap", file=sys.stderr)
        sys.exit(2)
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)
    msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=p.name)
    host = os.environ.get("MAIL_RELAY_HOST", "127.0.0.1")
    port = int(os.environ.get("MAIL_RELAY_PORT", "1025"))
    with smtplib.SMTP(host, port, timeout=15) as s:
        s.send_message(msg)
    print(f"sent {p.name} ({len(data)} bytes) to {to_addr} via {host}:{port}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--to", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--from", dest="sender", default="dev@team.local")
    p.add_argument("--body", default="See attached.")
    p.add_argument("--snapshot-path", default="/tmp/env_snapshot.json")
    args = p.parse_args()
    snapshot(args.snapshot_path)
    mail(args.snapshot_path, args.to, args.subject, args.sender, args.body)


if __name__ == "__main__":
    main()
