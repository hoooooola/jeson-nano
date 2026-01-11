FROM osrf/ros:humble-desktop-full

ARG USERNAME=dev
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Install essential tools
RUN apt-get update && apt-get install -y \
    git \
    python3-pip \
    python3-venv \
    lsb-release \
    wget \
    sudo \
    tzdata \
    gnupg \
    curl \
    nano \
    pkg-config \
    # ArduPilot dependencies
    python3-pexpect \
    python3-future \
    rapidjson-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    # GUI & Tools
    python3-wxgtk4.0 \
    python3-opencv \
    xterm \
    # Gazebo Harmonic (LTS)
    lsb-release \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Gazebo Harmonic (compatible with ArduPilot plugin)
RUN curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null \
    && apt-get update \
    && apt-get install -y gz-harmonic \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME

# Install ArduPilot prereqs (Python libraries)
ENV PATH="/home/$USERNAME/.local/bin:$PATH"
# Pin setuptools to <80 to avoid breaking colcon-core (ROS 2 dep)
RUN pip3 install --user -U empy pyros-genmsg "setuptools<80" mavproxy pymavlink

# Clone and build ardupilot_gazebo plugin
RUN mkdir -p /home/$USERNAME/workspace/src \
    && cd /home/$USERNAME/workspace/src \
    && git clone https://github.com/ArduPilot/ardupilot_gazebo \
    && cd ardupilot_gazebo \
    && mkdir build && cd build \
    && cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    && make -j4

# Add gazebo plugin path to env
ENV GZ_SIM_SYSTEM_PLUGIN_PATH="/home/$USERNAME/workspace/src/ardupilot_gazebo/build:${GZ_SIM_SYSTEM_PLUGIN_PATH}"
ENV GZ_SIM_RESOURCE_PATH="/home/$USERNAME/workspace/src/ardupilot_gazebo/models:/home/$USERNAME/workspace/src/ardupilot_gazebo/worlds:${GZ_SIM_RESOURCE_PATH}"

# Setup entrypoint
COPY --chown=$USERNAME:$USERNAME entrypoint.sh /home/$USERNAME/entrypoint.sh
RUN chmod +x /home/$USERNAME/entrypoint.sh

# Install MAVROS
RUN sudo apt-get update && sudo apt-get install -y ros-humble-mavros ros-humble-mavros-extras \
    && sudo rm -rf /var/lib/apt/lists/*
RUN sudo /opt/ros/humble/lib/mavros/install_geographiclib_datasets.sh

ENTRYPOINT ["/home/dev/entrypoint.sh"]
CMD ["bash"]
