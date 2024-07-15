FROM ubuntu:18.04
LABEL maintainer="martin"
LABEL description="build python3 environment of image in ubuntu 18.04"

# ====================================
# Configure environment
# ====================================
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# ====================================
# execute command during building image
# ====================================
RUN apt-get update -y
RUN apt-get update \
  && apt-get install -y python3-pip python3.6-dev tzdata vim curl wget \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && ln -s /usr/bin/pip3 pip
RUN pip install --upgrade pip

# ====================================
# Run Container
# ====================================
CMD ["python3"]