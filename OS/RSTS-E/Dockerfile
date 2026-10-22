# ==============================================================================
# DEC RSTS/E V10.1-L Operating System Emulation Container
# Digital Equipment Corporation PDP-11 Resource-Sharing Timesharing System
# ==============================================================================
FROM ubuntu:24.04

LABEL maintainer="DEC Systems Emulation Project"
LABEL description="DEC RSTS/E V10.1-L Operating System Emulation with BASIC-PLUS-2 & DEC-APPS"
LABEL version="10.1-L"

ENV DEBIAN_FRONTEND=noninteractive
ENV RSTS_HOME=/opt/dec-rsts
ENV RSTS_FS_ROOT=/opt/dec-rsts/fs
ENV PATH="/opt/dec-rsts/bin:/opt/dec-rsts/system/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    libsqlite3-0 \
    openssh-server \
    openssl \
    xxd \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd \
    && (useradd -o -u 0 -g 0 -M -d /root -s /bin/bash dec || true) \
    && (useradd -o -u 0 -g 0 -M -d /root -s /bin/bash rsts || true) \
    && passwd -d dec \
    && passwd -d rsts \
    && passwd -d root

WORKDIR /opt/dec-rsts

COPY src/ /opt/dec-rsts/src/
COPY bin/ /opt/dec-rsts/bin/
COPY system/ /opt/dec-rsts/system/
COPY docs/ /opt/dec-rsts/docs/
COPY README.md /opt/dec-rsts/README.md

RUN chmod -R 755 /opt/dec-rsts/bin /opt/dec-rsts/system/bin /opt/dec-rsts/src/rsts_os.py /opt/dec-rsts/src/multiuser_service.py \
    && ln -sf /opt/dec-rsts/bin/rsts-emu /usr/local/bin/rsts-emu \
    && python3 /opt/dec-rsts/src/rsts_os.py -c "SHOW SYSTEM" >/dev/null

EXPOSE 22 2211 8411

ENTRYPOINT ["/opt/dec-rsts/bin/rsts-emu"]
