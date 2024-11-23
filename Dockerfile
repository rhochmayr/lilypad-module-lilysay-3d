FROM nvidia/cuda:12.3.2-base-ubuntu22.04 AS builder

LABEL author="Robert Hochmayr"
LABEL title="Lilsay 3D in Blender"
LABEL maintainer="https://github.com/rhochmayr"

# Run installs on required dependencies for Blender
RUN apt-get update && apt-get install -y \
    curl \
    libfreetype6 \
    libglu1-mesa \
    libgl1-mesa-dev \
    libxi6 \
    libxrender1 \
    xz-utils \
    libxkbcommon-x11-0 \
    libsm6 \
    && apt-get -y autoremove && rm -rf /var/lib/apt/lists/*

# Blender variables used for specifying the blender version
ARG BLENDER_OS="linux-x64"
ARG BL_VERSION_SHORT="4.2"
ARG BL_VERSION_FULL="4.2.0"
ARG BL_DL_ROOT_URL="https://mirrors.ocf.berkeley.edu/blender/release/"
ARG BLENDER_DL_URL=${BL_DL_ROOT_URL}/Blender${BL_VERSION_SHORT}/blender-${BL_VERSION_FULL}-${BLENDER_OS}.tar.xz

RUN echo "Blender URL is $BLENDER_DL_URL"
RUN echo ${BLENDER_DL_URL}

# Set the working directory where we'll unpack blender
WORKDIR /usr/local/blender

# Download and unpack Blender
RUN curl -SL $BLENDER_DL_URL -o blender.tar.xz \
    && tar -xf blender.tar.xz --strip-components=1 && rm blender.tar.xz

# Add Blender to the PATH
ENV PATH="/usr/local/blender:${PATH}"

# Install python-cowsay within Blender's Python environment
RUN /usr/local/blender/${BL_VERSION_SHORT}/python/bin/python3.11 -m ensurepip \
    && /usr/local/blender/${BL_VERSION_SHORT}/python/bin/python3.11 -m pip install python-cowsay

# Set environment vars to be used when the image is running in a container
ENV BL_VERSION_SHORT=${BL_VERSION_SHORT}
ENV NVIDIA_DRIVER_CAPABILITIES=all
ENV NVIDIA_REQUIRE_CUDA="cuda>=8.0"

FROM builder AS runner

COPY lilysay3d.py /app/lilysay3d.py
COPY custom-cows/*.cow /usr/local/blender/${BL_VERSION_SHORT}/python/lib/python3.11/site-packages/cowsay/cows/

# Set the entrypoint to run the Blender script with parameters
ENTRYPOINT ["blender", "--background", "--python", "/app/lilysay3d.py", "--"]