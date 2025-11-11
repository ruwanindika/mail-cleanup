# Use a base Ubuntu image
FROM ubuntu:latest

# Update packages and install necessary dependencies
RUN apt-get update && \
    apt-get install -y software-properties-common gnupg2 curl && \
    rm -rf /var/lib/apt/lists/*

# Add HashiCorp GPG key
RUN curl -fsSL https://apt.releases.hashicorp.com/gpg | apt-key add -

# Add HashiCorp repository
RUN apt-add-repository "deb [arch=$(dpkg --print-architecture)] https://apt.releases.hashicorp.com $(lsb_release -cs) main"

# Update package list again and install Terraform
RUN apt-get update
RUN apt-get install -y terraform
RUN apt install python3-pip -y

RUN apt install python3-venv -y

RUN apt install python3-boto3 -y

RUN apt install python3-pytest -y

RUN apt install build-essential -y

RUN mkdir testenv && \
    cd testenv && \
    python3 -m venv myenv && \
    /bin/bash -c "source myenv/bin/activate"
# RUN cd testenv && \
#     /bin/bash -c "source myenv/bin/activate" && \
#     pip install pytest

# # Verify the installation
# # RUN terraform version

#     RUN pip install boto3
# RUN pip install pytest
# RUN pip install moto