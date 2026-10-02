FROM selenium/standalone-chrome:latest
USER root
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv dbus-x11 x11-utils
USER seluser
WORKDIR /app
COPY GoogleFindMyTools/requirements.txt .
RUN python3 -m pip install --break-system-packages -r requirements.txt

