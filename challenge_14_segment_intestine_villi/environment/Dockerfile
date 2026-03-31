# hash:sha256:ca287b50aa2b08d5a4fad8750aafc8dac22bfcef4e8742708e7fa11c5d993809
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
ENV MAX_THINKING_TOKENS=10000
ENV ANTHROPIC_DEFAULT_SONNET_MODEL=
ENV ANTHROPIC_MODEL=
ENV BEDROCK_MODEL_ID=

RUN pip install -U --no-cache-dir \
    anndata==0.11.4 \
    igraph==1.0.0 \
    leidenalg==0.11.0 \
    matplotlib==3.10.8 \
    numpy==2.2.6 \
    pandas==2.3.3 \
    scanpy==1.11.5 \
    scikit-learn==1.7.2 \
    scipy==1.15.3 \
    squidpy==1.6.5

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
