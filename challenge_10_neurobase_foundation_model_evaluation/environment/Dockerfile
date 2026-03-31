# hash:sha256:57e17a2200536c83d1b5514ee3e3f604390f096b274f2ece09ff3868fe42db6f
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/pytorch:2.4.0-cuda12.4.0-mambaforge24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
ENV MAX_THINKING_TOKENS=10000

RUN pip install -U --no-cache-dir \
    matplotlib==3.10.8 \
    numpy==2.4.4 \
    pandas==3.0.1 \
    pynrrd==1.1.3 \
    requests==2.33.1 \
    scikit-learn==1.8.0 \
    torch==2.11.0

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
