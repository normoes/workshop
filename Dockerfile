FROM python:3.6

ARG USER_ID=1000

RUN apt-get update -q \
    && apt-get install -y vim python3-dev libpq-dev \
    && pip install --upgrade virtualenv \
    && apt-get autoremove --purge -y \
    && rm -rf /var/tmp/* /tmp/* /var/lib/apt \
    && adduser --system --group --uid "$USER_ID" --shell /bin/false monero

ENV PATH "/home/monero/.local/bin/:${PATH}"

USER monero

WORKDIR /home/monero

VOLUME ["/home/monero"]
