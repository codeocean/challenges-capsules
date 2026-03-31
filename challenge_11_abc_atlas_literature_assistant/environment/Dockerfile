# hash:sha256:c76cf8f5f97a18d5b8cda39ca18ac928180845589450c5bdd141d17bd5e1e7f6
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
ENV MAX_THINKING_TOKENS=10000

RUN pip install -U --no-cache-dir \
    biopython==1.87 \
    boto3==1.42.79 \
    numpy==2.2.6 \
    pandas==2.3.3 \
    rapidfuzz==3.14.3 \
    requests==2.33.1 \
    scikit-learn==1.7.2 \
    tqdm==4.67.3

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
