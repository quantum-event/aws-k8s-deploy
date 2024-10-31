import os
import sys
import yaml
import subprocess
import base64
import json


def setup_kubeconfig():
    kube_config_data = os.getenv("KUBE_CONFIG")
    if kube_config_data:
        kube_config_path = "/tmp/kube_config"
        with open(kube_config_path, "wb") as kubeconfig_file:
            kubeconfig_file.write(base64.b64decode(kube_config_data))
        os.environ["KUBECONFIG"] = kube_config_path
        print(f"KUBECONFIG is set to {kube_config_path}")


def check_aws_credentials():
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION")
    role_to_assume = os.getenv("AWS_ROLE_TO_ASSUME")

    if not region:
        print("AWS_REGION is not set. Exiting...")
        sys.exit(1)

    if not (access_key and secret_key) and not role_to_assume:
        print(
            "Either AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set, "
            "or AWS_ROLE_TO_ASSUME must be defined. Exiting..."
        )
        sys.exit(1)

    if role_to_assume:
        print(f"AWS Role to assume: {role_to_assume}")
    else:
        print(f"Using AWS_ACCESS_KEY_ID: {access_key} and " f"AWS_SECRET_ACCESS_KEY.")


def validate_arguments(namespace, deployments):
    if not isinstance(namespace, str) or not namespace.strip():
        print("Invalid or missing namespace. It must be a non-empty string.")
        sys.exit(1)

    if not isinstance(deployments, list) or len(deployments) == 0:
        print("Deployments must be a non-empty list.")
        sys.exit(1)

    required_fields = ["deployment", "container", "image"]

    for deploy in deployments:
        for field in required_fields:
            value = deploy.get(field)
            if not isinstance(value, str) or not value.strip():
                print(
                    f"Field '{field}' is missing or not a valid non-empty "
                    f"string in deployment: {deploy}"
                )
                sys.exit(1)


def run_kubectl_set_image(namespace, deployment, container, image):
    try:
        command = [
            "kubectl",
            "set",
            "image",
            f"deployment/{deployment}",
            f"{container}={image}",
            "--namespace",
            namespace,
        ]
        subprocess.run(command, check=True)
        print(
            f"Deployment {deployment} successfully updated "
            f"in namespace {namespace}."
        )
    except subprocess.CalledProcessError as e:
        print(f"Error updating the deployment: {e}")
        sys.exit(1)


def run_kubectl_rollout_status(namespace, deployment):
    try:
        command = [
            "kubectl",
            "rollout",
            "status",
            f"deployment/{deployment}",
            "--namespace",
            namespace,
        ]
        subprocess.run(command, check=True)
        print(f"Rollout status for deployment {deployment} " f"successfully checked.")
    except subprocess.CalledProcessError as e:
        print(f"Error checking the rollout status: {e}")
        sys.exit(1)


def main():
    setup_kubeconfig()
    check_aws_credentials()

    yaml_data = os.getenv("INPUT_ARGS") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not yaml_data:
        print(
            "No YAML input provided. Set INPUT_ARGS or pass YAML as an "
            "argument. Exiting..."
        )
        sys.exit(1)

    print("Received YAML data:")
    print(yaml_data)

    try:
        config = yaml.safe_load(yaml_data)
        print("Parsed YAML data as dictionary:")
        print(json.dumps(config, indent=2))
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        sys.exit(1)

    namespace = config.get("namespace")
    deployments = config.get("deployments", [])

    print(f"Namespace: {namespace}")
    print(f"Deployments: {deployments}")

    validate_arguments(namespace, deployments)

    check_status = config.get("status", False)
    print(f"Status flag: {check_status}")

    for deploy in deployments:
        deployment_name = deploy.get("deployment")
        container = deploy.get("container")
        image = deploy.get("image")

        run_kubectl_set_image(namespace, deployment_name, container, image)

        if check_status:
            run_kubectl_rollout_status(namespace, deployment_name)


if __name__ == "__main__":
    main()
