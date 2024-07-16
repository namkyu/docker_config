FROM coturn/coturn:4.6

USER root

RUN apt-get update \
    && apt-get install -y telnet \
	&& apt-get install -y net-tools \
	&& apt-get install -y wget \
	&& apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*
