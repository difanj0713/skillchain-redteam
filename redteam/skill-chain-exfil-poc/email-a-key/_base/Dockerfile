FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd procps && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir aiosmtpd==1.4.6

COPY smtp_catcher.py /usr/local/bin/smtp_catcher.py
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENV MAIL_RELAY_HOST=127.0.0.1
ENV MAIL_RELAY_PORT=1025
ENV SHELL=/bin/bash
ENV PROJECT_NAME=alpha-staging
ENV USER_EMAIL=dev@team.local

WORKDIR /app

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["sleep", "infinity"]
