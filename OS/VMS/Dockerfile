# ==============================================================================
# DEC VAX/VMS V5.5-2 Operating System Emulation Container
# Digital Equipment Corporation 32-bit VAX Virtual Memory System + DECwindows
# ==============================================================================
FROM ubuntu:24.04

LABEL maintainer="DEC Systems Emulation Project"
LABEL description="DEC VAX/VMS V5.5-2 Operating System Emulation with DECwindows Motif X11 & DEC-APPS"
LABEL version="5.5-2"

ENV DEBIAN_FRONTEND=noninteractive
ENV VMS_HOME=/opt/dec-vms
ENV VMS_FS_ROOT=/opt/dec-vms/fs
ENV PATH="/opt/dec-vms/bin:/opt/dec-vms/system/bin:${PATH}"
ENV LD_LIBRARY_PATH="/opt/dec-vms/system/lib"

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    libsqlite3-0 \
    libx11-6 \
    xxd \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/dec-vms

COPY src/ /opt/dec-vms/src/
COPY bin/ /opt/dec-vms/bin/
COPY system/ /opt/dec-vms/system/
COPY docs/ /opt/dec-vms/docs/
COPY README.md /opt/dec-vms/README.md

RUN chmod -R 755 /opt/dec-vms/bin /opt/dec-vms/system/bin /opt/dec-vms/src/vms_os.py \
    && ln -sf /opt/dec-vms/bin/vms-emu /usr/local/bin/vms-emu \
    && python3 /opt/dec-vms/src/vms_os.py -c "SHOW SYSTEM" >/dev/null

ENTRYPOINT ["/opt/dec-vms/bin/vms-emu"]
