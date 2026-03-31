# hash:sha256:5ee3e6cd8512980f4224d814e30d3e1e2670c5e528358e4a91b4aecb5f071160
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
ENV MAX_THINKING_TOKENS=10000

RUN pip install -U --no-cache-dir \
    boto3==1.42.78 \
    faiss-cpu==1.13.2 \
    numpy==2.2.6 \
    pandas==2.3.3 \
    pydantic==2.12.5 \
    scikit-learn==1.7.2 \
    sentence-transformers==5.3.0

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
