import os
import unittest
import base64
from unittest.mock import patch
from entrypoint import setup_kubeconfig, check_aws_credentials, validate_arguments


class TestMainFunctions(unittest.TestCase):
    @patch.dict(
        os.environ, {"KUBE_CONFIG": base64.b64encode(b"fake-kube-config").decode()}
    )
    def test_setup_kubeconfig(self):
        """Test to verify that KUBECONFIG is set up correctly."""
        setup_kubeconfig()
        kube_config_path = os.getenv("KUBECONFIG")
        self.assertEqual(kube_config_path, "/tmp/kube_config")
        with open("/tmp/kube_config", "r") as file:
            config_data = file.read()
            self.assertEqual(config_data, "fake-kube-config")

    @patch.dict(
        os.environ,
        {
            "AWS_ACCESS_KEY_ID": "test-access-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret-key",
            "AWS_REGION": "us-east-1",
        },
    )
    def test_check_aws_credentials_valid(self):
        """Test to check if AWS credentials are validated when present."""
        try:
            check_aws_credentials()
        except SystemExit:
            self.fail(
                "check_aws_credentials() exited unexpectedly " "with valid credentials."
            )

    @patch.dict(os.environ, {"AWS_REGION": "us-east-1"})
    def test_check_aws_credentials_missing(self):
        """Test to verify if missing AWS credentials cause an error exit."""
        with self.assertRaises(SystemExit) as cm:
            check_aws_credentials()
        self.assertEqual(cm.exception.code, 1)  # Check if exit code is 1

    def test_validate_arguments_valid(self):
        """Test to verify that valid arguments pass validation."""
        namespace = "staging"
        deployments = [
            {
                "deployment": "app-deployment",
                "container": "app-container",
                "image": "app-image:latest",
            }
        ]
        try:
            validate_arguments(namespace, deployments)
        except SystemExit:
            self.fail(
                "validate_arguments() exited unexpectedly " "with valid arguments."
            )

    def test_validate_arguments_invalid_namespace(self):
        """Test to verify that an invalid namespace triggers an error."""
        namespace = ""
        deployments = [
            {
                "deployment": "app-deployment",
                "container": "app-container",
                "image": "app-image:latest",
            }
        ]
        with self.assertRaises(SystemExit) as cm:
            validate_arguments(namespace, deployments)
        self.assertEqual(cm.exception.code, 1)

    def test_validate_arguments_invalid_deployments(self):
        """Test to verify that an invalid deployment triggers an error."""
        namespace = "staging"
        deployments = [
            {
                "deployment": "",
                "container": "app-container",
                "image": "app-image:latest",
            }
        ]
        with self.assertRaises(SystemExit) as cm:
            validate_arguments(namespace, deployments)
        self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
