# hash:sha256:e13d12eb431d7406c804f299067b7992d69fff549abc427268de5b86e231f896
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
ENV MAX_THINKING_TOKENS=10000

RUN pip install -U --no-cache-dir \
    matplotlib==3.10.8 \
    numpy==2.2.6 \
    pandas==2.3.3 \
    scikit-image==0.25.2 \
    scikit-learn==1.7.2 \
    scipy==1.15.3 \
    tifffile==2025.5.10

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
