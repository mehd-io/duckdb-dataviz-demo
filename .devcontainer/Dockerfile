ARG PLATFORM=amd64
FROM --platform=linux/${PLATFORM} mcr.microsoft.com/devcontainers/javascript-node:1-18-bullseye

# Poetry for streamlit
RUN pip3 install poetry

# Rill CLI
RUN curl -s https://cdn.rilldata.com/install.sh | bash
