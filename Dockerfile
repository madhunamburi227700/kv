# -------------------- BASE IMAGE --------------------
FROM python:3.12-slim

# Use bash explicitly
SHELL ["/usr/bin/bash", "-c"]

# -------------------- ENV SETUP --------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    JAVA_HOME=/usr/lib/jvm/java-19-openjdk-amd64 \
    PATH="/usr/lib/jvm/java-19-openjdk-amd64/bin:/usr/local/apache-maven/bin:/root/.local/bin:$PATH"

# -------------------- SYSTEM DEPENDENCIES --------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    dash \
    curl \
    wget \
    gnupg \
    unzip \
    git \
    ca-certificates \
    build-essential \
    procps \
    coreutils \
    findutils \
    file \
    jq \
    xz-utils \
    && if [ ! -e /bin/sh ]; then ln -s /usr/bin/dash /bin/sh; fi \
    && rm -rf /var/lib/apt/lists/*

# -------------------- OPENJDK 19 SETUP --------------------
RUN mkdir -p /usr/lib/jvm \
    && curl -fSL https://github.com/adoptium/temurin19-binaries/releases/download/jdk-19.0.2%2B7/OpenJDK19U-jdk_x64_linux_hotspot_19.0.2_7.tar.gz -o /tmp/openjdk.tar.gz \
    && tar -xzf /tmp/openjdk.tar.gz -C /usr/lib/jvm \
    && rm /tmp/openjdk.tar.gz \
    && mv /usr/lib/jvm/jdk-19.0.2+7 /usr/lib/jvm/java-19-openjdk-amd64 \
    && $JAVA_HOME/bin/java -version

# -------------------- MAVEN 3.9.11 SETUP --------------------
ENV MAVEN_VERSION=3.9.11
RUN curl -fSL https://archive.apache.org/dist/maven/maven-3/$MAVEN_VERSION/binaries/apache-maven-$MAVEN_VERSION-bin.zip -o /tmp/maven.zip \
    && unzip /tmp/maven.zip -d /usr/local/ \
    && rm /tmp/maven.zip \
    && mv /usr/local/apache-maven-$MAVEN_VERSION /usr/local/apache-maven \
    && chmod +x /usr/local/apache-maven/bin/mvn \
    && sed -i '1s|^#!/bin/sh|#!/usr/bin/bash|' /usr/local/apache-maven/bin/mvn \
    && mvn -v

# -------------------- NODE.JS + NPM + CDXGEN --------------------
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g @cyclonedx/cdxgen \
    && export PATH="$(npm bin -g):$PATH" \
    && node -v \
    && npm -v \
    && cdxgen -v

# -------------------- UV SETUP (GLOBAL) --------------------
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && mv /root/.local/bin/uvx /usr/local/bin/uvx \
    && chmod +x /usr/local/bin/uv /usr/local/bin/uvx \
    && uv --version

# -------------------- WORKDIR & COPY --------------------
WORKDIR /apps
COPY . /apps

RUN pip install --no-cache-dir fastapi uvicorn pydantic requests python-multipart python-dotenv toml

# -------------------- RUN MAIN SCRIPT --------------------
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]