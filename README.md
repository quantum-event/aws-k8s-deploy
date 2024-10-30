

# Kubernetes Multi-Deployment Automation with GitHub Actions #

  

This project automates the deployment and verification of multiple Kubernetes deployments using GitHub Actions. It streamlines the CI/CD pipeline by managing container deployments across various environments, ensuring each deployment succeeds while providing real-time feedback.

  

**Project Overview**

  

The primary goal of this project is to simplify and automate multi-deployment operations in Kubernetes by leveraging GitHub Actions. By defining Kubernetes deployments in a structured YAML configuration, this project allows developers to control deployment lifecycles in a consistent, reliable, and scalable manner. The automated checks and rollouts reduce human error and accelerate deployment cycles.

  

**Key Technologies**

  

-  **GitHub Actions**: Orchestrates the automation workflows for continuous integration and deployment. It triggers actions, deploys updates, and verifies the status of each deployment in Kubernetes.

  

-  **Kubernetes (k8s)**: The orchestrator that manages containerized applications across clusters, handling automated deployment, scaling, and operations.

  

-  **AWS IAM & EKS**: Uses AWS Identity and Access Management (IAM) for secure access, and Elastic Kubernetes Service (EKS) as the Kubernetes management service.

  

**How to Use in GitHub Actions**

  

**Step 1: Configure AWS and Kubernetes Access**

  

1.  **AWS Credentials**:

  

Store AWS credentials as GitHub secrets to access AWS resources and manage Kubernetes clusters in EKS. Go to **Settings** > **Secrets** in your GitHub repository and add:

  

- AWS_ACCESS_KEY_ID -- Your AWS Access Key.

  

- AWS_SECRET_ACCESS_KEY -- Your AWS Secret Access Key.

  

- AWS_REGION -- The region where your EKS cluster is hosted.

  

If using AWS roles, define:

  

- AWS_ROLE_TO_ASSUME -- ARN of the role to assume.

  

2.  **Kubeconfig for Kubernetes Access**:

  

- Base64 encode your kubeconfig and save it as a GitHub secret named KUBE_CONFIG.

  

- Example command to base64 encode: cat kubeconfig | base64.

  

**Step 2: Add the Workflow to GitHub Actions**

  

In your repository, create a new file in .github/workflows/deployment.yml to define the deployment process. Below is a sample GitHub Actions workflow:

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
