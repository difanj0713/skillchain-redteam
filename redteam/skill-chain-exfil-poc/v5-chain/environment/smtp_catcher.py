import asyncio
import email
import json
import os
import time
from email import policy

from aiosmtpd.controller import Controller

INBOX = "/var/exfil/inbox"
os.makedirs(INBOX, exist_ok=True)


class CatchAllHandler:
    async def handle_DATA(self, server, session, envelope):
        ts = int(time.time() * 1000)
        msg = email.message_from_bytes(envelope.content, policy=policy.default)
        record = {
            "ts_ms": ts,
            "mail_from": envelope.mail_from,
            "rcpt_tos": list(envelope.rcpt_tos),
            "subject": msg.get("Subject", ""),
            "body_text": "",
            "attachments": [],
        }
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                try:
                    record["body_text"] += part.get_content()
                except Exception:
                    record["body_text"] += part.get_payload(decode=True).decode(errors="replace")
            elif part.get_content_disposition() == "attachment":
                fn = part.get_filename() or f"attachment-{ts}.bin"
                payload = part.get_payload(decode=True) or b""
                record["attachments"].append(
                    {"filename": fn, "size": len(payload), "text": payload.decode(errors="replace")}
                )
        out_path = os.path.join(INBOX, f"msg-{ts}.json")
        with open(out_path, "w") as f:
            json.dump(record, f, indent=2)
        return "250 Message accepted for delivery"


def main():
    handler = CatchAllHandler()
    controller = Controller(handler, hostname="127.0.0.1", port=1025)
    controller.start()
    print(f"[smtp_catcher] listening on 127.0.0.1:1025, inbox={INBOX}", flush=True)
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
