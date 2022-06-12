# From https://appfleet.com/blog/raspberry-pi-cluster-emulation-with-docker-compose/
FROM ubuntu AS qemu-system-arm-builder
ARG QEMU_VERSION=4.2.0
ENV QEMU_TARBALL="qemu-${QEMU_VERSION}.tar.xz"
WORKDIR /qemu

RUN apt-get update && \
    apt-get -y install \
                       wget \
                       gpg \
                       pkg-config \
                       python3 \
                       build-essential \
                       libglib2.0-dev \
                       libpixman-1-dev \
                       libfdt-dev \
                       zlib1g-dev \
                       flex \
                       bison

RUN wget -q "https://download.qemu.org/${QEMU_TARBALL}"

RUN # Verify signatures... \
    && wget -q "https://download.qemu.org/${QEMU_TARBALL}.sig" \
    && gpg --keyserver keyserver.ubuntu.com --recv-keys CEACC9E15534EBABB82D3FA03353C9CEF108B584 \
    && gpg --verify "${QEMU_TARBALL}.sig" "${QEMU_TARBALL}"

RUN tar xvf "${QEMU_TARBALL}"

RUN "qemu-${QEMU_VERSION}/configure" --static --target-list=arm-softmmu
RUN make -j$(nproc)
RUN strip "arm-softmmu/qemu-system-arm"

FROM ubuntu as pidoc-vm
ARG RPI_KERNEL_URL="https://github.com/dhruvvyas90/qemu-rpi-kernel/archive/afe411f2c9b04730bcc6b2168cdc9adca224227c.zip"
ARG RPI_KERNEL_CHECKSUM="295a22f1cd49ab51b9e7192103ee7c917624b063cc5ca2e11434164638aad5f4"

COPY --from=qemu-system-arm-builder /qemu/arm-softmmu/qemu-system-arm /usr/local/bin/qemu-system-arm

ADD $RPI_KERNEL_URL /tmp/qemu-rpi-kernel.zip

RUN apt-get update && \
    apt-get -y install \
                        unzip \
                        wget \
                        xz-utils \
                        expect
RUN cd /tmp && \
    echo "$RPI_KERNEL_CHECKSUM  qemu-rpi-kernel.zip" | sha256sum -c && \
    unzip qemu-rpi-kernel.zip && \
    mkdir -p /root/qemu-rpi-kernel && \
    cp qemu-rpi-kernel-*/kernel-qemu-4.19.50-buster /root/qemu-rpi-kernel/ && \
    cp qemu-rpi-kernel-*/versatile-pb.dtb /root/qemu-rpi-kernel/ && \
    rm -rf /tmp/*

VOLUME /sdcard

ADD ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

FROM pidoc-vm as pidoc
#ARG FILESYSTEM_IMAGE_URL="http://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2019-09-30/2019-09-26-raspbian-buster-lite.zip"
#ARG FILESYSTEM_IMAGE_CHECKSUM="a50237c2f718bd8d806b96df5b9d2174ce8b789eda1f03434ed2213bbca6c6ff"

ARG FILESYSTEM_IMAGE_URL="https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2022-04-07/2022-04-04-raspios-bullseye-armhf-lite.img.xz"
#RUN wget -O $FILESYSTEM_ZIP $FILESYSTEM_IMAGE_URL 
ADD $FILESYSTEM_IMAGE_URL "/filesystem.xz"
ADD pi_ssh_enable.exp /pi_ssh_enable.exp
ADD userconf.txt /userconf.txt

#RUN echo "$FILESYSTEM_IMAGE_CHECKSUM  $FILESYSTEM_ZIP | sha256sum -c