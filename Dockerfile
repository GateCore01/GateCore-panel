FROM alpine:3.23.5

RUN apk update
RUN apk add --no-cache curl python3 python3-dev sqlite openssh-client

COPY Core/ /opt/gatecore/panel/

RUN python3 -m venv /opt/gatecore/panel/venv
RUN source /opt/gatecore/panel/venv/bin/activate
ENV PATH=$PATH:/opt/gatecore/panel/venv/bin

RUN /opt/gatecore/panel/venv/bin/pip install --upgrade pip
RUN /opt/gatecore/panel/venv/bin/pip install websockets fastapi uvicorn jinja2 python-multipart paramiko bcrypt passlib python-dotenv aiofiles psutil requests pydantic sqlalchemy openssh-wrapper

RUN addgroup -S gatecore && adduser -S gatecore -G gatecore
RUN chown -R gatecore:gatecore /opt/gatecore/panel/

USER gatecore
WORKDIR /opt/gatecore/panel
ENTRYPOINT ["/opt/gatecore/panel/venv/bin/python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
