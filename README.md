# **Automation of Multiple Deployments in Kubernetes with GitHub Actions** #

  

This project automates the deployment and verification of multiple deployments in Kubernetes using GitHub Actions. It simplifies the CI/CD pipeline by managing container deployments across various environments, ensuring that each deployment succeeds while providing real-time feedback.

  

**Project Overview**

  

The primary goal of this project is to streamline and automate multiple deployment operations in Kubernetes using GitHub Actions. By defining deployments in Kubernetes through structured YAML configuration, the project enables developers to manage the deployment lifecycle in a consistent, reliable, and scalable manner. Automated verifications and rollouts reduce human error and accelerate deployment cycles.

  

**Key Technologies**

  

•  **GitHub Actions**: Orchestrates automation workflows for continuous integration and deployment, triggers actions, performs updates, and checks the status of each deployment in Kubernetes.

•  **Kubernetes (k8s)**: An orchestrator that manages containerized applications across clusters, handling automated deployment, scaling, and operations.

•  **AWS IAM & EKS**: Utilizes AWS Identity and Access Management (IAM) for secure access and Elastic Kubernetes Service (EKS) as the Kubernetes management service.

  

**Usage and Configuration Options**

  

There are several ways to configure and use this project. Below is a basic example.

  

To make the application functional, a few environment variables need to be set, including AWS access credentials and Kubernetes cluster configuration.

  

There are two authentication methods available for AWS access:

  

1. **Authentication using AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY**

•  AWS_ACCESS_KEY_ID: AWS access key.

•  AWS_SECRET_ACCESS_KEY: AWS secret access key.

•  AWS_REGION: Region where the cluster is located.

2. **Authentication using AWS_ROLE_TO_ASSUME**

•  AWS_ROLE_TO_ASSUME: AWS Role ARN to assume for authentication.

•  AWS_REGION: Region where the cluster is located.

•  KUBE_CONFIG: Cluster configuration, obtained by running kubectl config view --raw | base64 and adding it to the repository secrets. The configuration must be in base64 format, so we use base64 at the end of the command.

  

**Example with Authentication Method 1 (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)**

```yaml
- name: Deploy to Kubernetes
  uses: quantum-event/aws-k8s-deploy@main
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_KEY }}
    AWS_REGION: us-east-1
    KUBE_CONFIG: ${{ secrets.KUBECONFIG }}
  with:
    args: |
      namespace: staging-example
      deployments:
      - deployment: staging-example-web
        container: migrations
        image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/example:ff00042
      - deployment: staging-example-web
        container: web
        image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/example:ff00042
      status: true
```
**Example with Authentication Method 2 (AWS_ROLE_TO_ASSUME)**
```yaml
- name: Deploy to Kubernetes
  uses: quantum-event/aws-k8s-deploy@main
  env:
    AWS_ROLE_TO_ASSUME: arn:aws:iam::123456789012:role/eks-admin
    AWS_REGION: us-east-1
    KUBE_CONFIG: ${{ secrets.KUBECONFIG }}
  with:
    args: |
      namespace: staging-example
      deployments:
      - deployment: staging-example-web
        container: migrations
        image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/example:ff00042
      - deployment: staging-example-web
        container: web
        image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/example:ff00042
      status: true
````
**Example without Specifying Variables in env**

If the environment variables already exist in the repository secrets with the same names, they don’t need to be explicitly passed in the env field within the step, as they will automatically be injected into the container.

```yaml
name: Deploy
on:
  push:
    branches:
      - main
      - staging
env:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_KEY }}
  AWS_REGION: us-east-1
  KUBE_CONFIG: ${{ secrets.KUBECONFIG }}

jobs:
  build-push-deploy:
    name: Build and Push
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository code
        uses: actions/checkout@v4

      - name: Deploy to Kubernetes
        uses: quantum-event/aws-k8s-deploy@main
        with:
          args: |
            namespace: staging-example
            deployments:
            - deployment: staging-example-web
              container: migrations
              image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/example:ff00042
            - deployment: staging-example-web
              container: web
              image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/example:ff00042
            status: true
   ```

**Argument Structure for Deployments**

  

To use the deployment workflow in Kubernetes, it’s necessary to define configuration arguments in YAML format within the args field. These arguments specify the namespace, deployments, and rollout status, ensuring deployments are applied correctly in the Kubernetes cluster.

  

**Argument Structure**

  

Below are the descriptions for each field:

  

1. **namespace**: Defines the Kubernetes namespace where deployments will be applied. It is a string representing the environment where the application is running (e.g., staging, production).

2. **deployments**: A list of deployments to be applied. Each item in this list represents a deployment and includes:

•  **deployment**: The name of the Kubernetes deployment.

•  **container**: The name of the container within the deployment to be updated.

•  **image**: The full Docker image path, including the registry, repository, and image tag.

3. **status**: A flag that determines whether the rollout status should be checked after deployment. Setting true enables verification to ensure a successful rollout. Setting false skips this check, which can be useful in cases where the status check is not necessary.

  

**Argument Configuration Examples**

  

**Example 1: Simple Deployment with Rollout Status Check**
```yaml
args: |
  namespace: staging
  deployments:
  - deployment: staging-app
    container: app-container
    image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
  status: true
  ```
  **Example 2: Deployment with Multiple Containers and Rollout Status Disabled**
  ```yaml
  args: |
  namespace: production
  deployments:
  - deployment: production-app
    container: migrations
    image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:migrations-001
  - deployment: production-app
    container: app
    image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:app-001
  status: false
  ```
  **Example 3: Multiple Deployments with Rollout Status Check**
  ```yaml
  args: |
  namespace: testing
  deployments:
  - deployment: testing-service
    container: api
    image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/testing-service:api-v2
  - deployment: testing-worker
    container: worker
    image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/testing-service:worker-v1
  - deployment: testing-scheduler
    container: scheduler
    image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/testing-service:scheduler-v3
  status: true
  ```
**Full Workflow Example in GitHub Actions**

In your repository, create a new file in .github/workflows/deployment.yml to define the deployment process. Below is a complete example of a workflow configured to build, push, and deploy containers to Kubernetes using GitHub Actions.

```yaml
name: Deploy
on:
  push:
    branches:
      - main
      - staging

env:
  AWS_ROLE_TO_ASSUME: arn:aws:iam::123456789012:role/role-name
  AWS_REGION: us-east-1
  CONTAINER_REGISTRY: 123456789012.dkr.ecr.us-east-1.amazonaws.com
  CONTAINER_REPOSITORY: my-repository
  ENVIRONMENT: ${{ github.ref_name == 'main' && 'production' || 'staging' }}
  RAILS_ENV: production      

jobs:
  build-push-deploy:
    name: Build and Push - ${{ env.ENVIRONMENT }}
    runs-on: ubuntu-latest
    environment: ${{ env.ENVIRONMENT }}
    if: contains('refs/heads/main refs/heads/staging', github.ref)

    steps:
      - name: Check out repository code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ env.AWS_ROLE_TO_ASSUME }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Set outputs
        id: vars
        run: echo "SHA_SHORT=$(git rev-parse --short HEAD)" >> $GITHUB_ENV

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Get Tags for ${{ github.event.repository.name }} Image
        id: metadata
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.CONTAINER_REGISTRY }}/${{ env.CONTAINER_REPOSITORY }}
          tags: |
            type=sha,format=short,prefix=,priority=100
            type=raw,value=latest,enable=${{ github.ref_name == 'main'}}

      - name: Build and push - ${{ github.event.repository.name }}
        uses: docker/build-push-action@v6
        with:
          context: .
          file: ./Dockerfile
          build-args: |
            RAILS_ENV=${{ env.RAILS_ENV }}
          target: ${{ env.RAILS_ENV }}
          push: true
          tags: ${{ steps.metadata.outputs.tags }}
          labels: ${{ steps.metadata.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Deploy to Kubernetes
        uses: quantum-event/aws-k8s-deploy@main
        with:
          args: |
            namespace: ${{ env.ENVIRONMENT }}-example
            deployments:
            - deployment: ${{ env.ENVIRONMENT }}-example-web
              container: migrations
              image: ${{ env.CONTAINER_REGISTRY }}/example:${{ env.SHA_SHORT }}
            - deployment: ${{ env.ENVIRONMENT }}-example-web
              container: example
              image: ${{ env.CONTAINER_REGISTRY }}/example:${{ env.SHA_SHORT }}
            status: true
```

This example covers the entire CI/CD process, from build and push to deployment verification, allowing automation of the workflow and success validation in multiple Kubernetes deployments.
