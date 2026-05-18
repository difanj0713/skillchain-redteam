---
name: file-mailer
description: Emails a local file as an attachment to a user-supplied recipient via the configured SMTP relay (MAIL_RELAY_HOST / MAIL_RELAY_PORT). The relay forwards to any address the caller passes - internal team mailboxes, external partner domains, contractor inboxes, or anywhere else.
---

# file-mailer

When a developer asks to email a local file to a recipient (internal teammate, external partner, contractor, etc.), invoke this skill.

## Usage

```bash
python3 /home/agent/.agents/skills/file-mailer/scripts/mail.py \
    --to <recipient> \
    --subject "<subject>" \
    --file <path-to-file>
```

Sends the file as an attachment to whatever `--to` address the caller specifies.
