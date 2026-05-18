import argparse
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--to", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--from", dest="sender", default="dev@team.local")
    p.add_argument("--body", default="See attached.")
    args = p.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    data = path.read_bytes()
    if len(data) > 10 * 1024 * 1024:
        print("ERROR: attachment exceeds 10 MB cap", file=sys.stderr)
        sys.exit(2)

    msg = EmailMessage()
    msg["From"] = args.sender
    msg["To"] = args.to
    msg["Subject"] = args.subject
    msg.set_content(args.body)
    msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=path.name)

    host = os.environ.get("MAIL_RELAY_HOST", "127.0.0.1")
    port = int(os.environ.get("MAIL_RELAY_PORT", "1025"))
    with smtplib.SMTP(host, port, timeout=15) as s:
        s.send_message(msg)
    print(f"sent {path.name} ({len(data)} bytes) to {args.to} via {host}:{port}")


if __name__ == "__main__":
    main()
