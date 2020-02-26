FROM mariadb:10

# ====================================
# Configure environment
# ====================================
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

ENV TZ=Asia/Seoul
ENV MYSQL_ROOT_PASSWORD=aaaa1111
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# ====================================
# execute command during building image
# ====================================
WORKDIR /root
RUN mkdir -p test_db
COPY test_db test_db
COPY init_db.sh .

# ====================================
# Run Container
# ====================================