FROM python:3.9-slim

    # Install dependencies: curl, AWS CLI, and kubectl
    RUN apt-get update && \
        apt-get install -y curl unzip && \
        pip install --upgrade pip

    # Install AWS CLI v2
    RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
        unzip awscliv2.zip && \
        ./aws/install &&\
        rm -rf awscliv2.zip ./aws

    # Install kubectl
    RUN curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl" && \
        chmod +x ./kubectl && \
        mv ./kubectl /usr/local/bin/kubectl

    # Install PyYAML to process YAML files
    RUN pip install pyyaml~=6.0

    # Copy the Python script to the container
    COPY entrypoint.py /usr/src/app/entrypoint.py

    # Make the Python script executable
    RUN chmod +x /usr/src/app/entrypoint.py

    # Set the Python script as the entry point
    ENTRYPOINT ["python", "/usr/src/app/entrypoint.py"]
