FROM docker_ubuntu:v1
LABEL maintainer="nklee"
LABEL description="build superset environment of image in ubuntu 18.04 with python3.6"

# ====================================
# Configure environment
# ==================================== 
ENV SUPERSET_HOME=/home/superset
ENV SUPERSET_PORT=8088
ENV SUPERSET_VERSION=0.35.2

ENV GUNICORN_BIND=0.0.0.0:${SUPERSET_PORT} \
    GUNICORN_LIMIT_REQUEST_FIELD_SIZE=0 \
    GUNICORN_LIMIT_REQUEST_LINE=0 \
    GUNICORN_TIMEOUT=60 \
    GUNICORN_WORKERS=3 \
    GUNICORN_THREADS=4 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONPATH=/etc/superset:/home/superset:$PYTHONPATH    

ENV GUNICORN_CMD_ARGS="--workers ${GUNICORN_WORKERS} --threads ${GUNICORN_THREADS} --timeout ${GUNICORN_TIMEOUT} --bind ${GUNICORN_BIND} --limit-request-line ${GUNICORN_LIMIT_REQUEST_LINE} --limit-request-field_size ${GUNICORN_LIMIT_REQUEST_FIELD_SIZE}"


# ====================================
# execute command during building image
# ====================================
RUN groupadd supergroup && \
    useradd -U -m -G supergroup superset && \
    mkdir -p /etc/superset && \    
    chown -R superset:superset /etc/superset && \
    chown -R superset:superset ${SUPERSET_HOME} && \
    apt-get update && \
    apt-get install -y \
        build-essential \
        curl \		
        default-libmysqlclient-dev \
        freetds-bin \
        freetds-dev \
        libaio1 \
        libffi-dev \
        libldap2-dev \
        libpq-dev \
        libsasl2-2 \
        libsasl2-dev \
        libsasl2-modules-gssapi-mit && \        
    apt-get clean

WORKDIR ${SUPERSET_HOME}
COPY requirements.txt .
COPY requirements-db.txt .
COPY superset-init /usr/local/bin
COPY superset_config.py .

RUN chown -R superset:superset requirements.txt
RUN chown -R superset:superset requirements-db.txt
RUN chown -R superset:superset superset_config.py
RUN pip install apache-superset==${SUPERSET_VERSION} && \
    pip install -r requirements.txt && \
	pip install -r requirements-db.txt


# ====================================
# Run Container
# ====================================
EXPOSE ${SUPERSET_PORT}
HEALTHCHECK CMD ["curl", "-f", "http://localhost:${SUPERSET_PORT}/health"]
CMD ["gunicorn", "superset:app"]
USER superset