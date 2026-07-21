FROM alpine:3.23.5

RUN apk add --no-cache python3 python3-pip python3-devel sqlite3 openssh

COPY Core/* /opt/gatecore/panel/

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN python3 -m venv /opt/gatecore/panel/venv
RUN source /opt/gatecore/panel/venv/bin/activate

RUN addgroup -S gatecore && adduser -S gatecore -G gatecore
USER gatecore

WORKDIR /opt/gatecore/panel

ENV PATH=/opt/gatecore/panel/venv/bin
ENTRYPOINT ["/opt/gatecore/panel/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 80"]
