#!/usr/bin/env python3
"""Tests for generate-collector-config.py"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch

# Add the confgen directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).parent))

# Import the module (filename has hyphen, so we use importlib)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "generate_collector_config",
    Path(__file__).parent / "generate-collector-config.py"
)
generate_collector_config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_collector_config_module)

# Import functions from the module
validate_environment = generate_collector_config_module.validate_environment
get_template_context = generate_collector_config_module.get_template_context
generate_config = generate_collector_config_module.generate_config


class TestValidateEnvironment:
    """Test the validate_environment function."""

    def test_missing_both_endpoints(self, capsys):
        """Test that validation fails when both endpoints are missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SystemExit) as exc_info:
                validate_environment()
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "expected OTLP_ENDPOINT or ELASTICSEARCH_ENDPOINT" in captured.err

    def test_missing_both_api_keys(self, capsys):
        """Test that validation fails when both API keys are missing."""
        with patch.dict(os.environ, {"OTLP_ENDPOINT": "http://test"}, clear=True):
            with pytest.raises(SystemExit) as exc_info:
                validate_environment()
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "expected OTLP_API_KEY or ELASTICSEARCH_API_KEY" in captured.err

    def test_otlp_endpoint_and_key_present(self):
        """Test that validation passes with OTLP endpoint and key."""
        with patch.dict(
            os.environ,
            {"OTLP_ENDPOINT": "http://test", "OTLP_API_KEY": "test-key"},
            clear=True,
        ):
            # Should not raise
            validate_environment()

    def test_elasticsearch_endpoint_and_key_present(self):
        """Test that validation passes with Elasticsearch endpoint and key."""
        with patch.dict(
            os.environ,
            {
                "ELASTICSEARCH_ENDPOINT": "http://test",
                "ELASTICSEARCH_API_KEY": "test-key",
            },
            clear=True,
        ):
            # Should not raise
            validate_environment()

    def test_both_endpoints_present(self):
        """Test that validation passes when both endpoints are present."""
        with patch.dict(
            os.environ,
            {
                "OTLP_ENDPOINT": "http://otlp",
                "OTLP_API_KEY": "otlp-key",
                "ELASTICSEARCH_ENDPOINT": "http://es",
                "ELASTICSEARCH_API_KEY": "es-key",
            },
            clear=True,
        ):
            # Should not raise
            validate_environment()


class TestGetTemplateContext:
    """Test the get_template_context function."""

    def test_all_variables_present(self):
        """Test context with all variables set."""
        with patch.dict(
            os.environ,
            {
                "OTLP_ENDPOINT": "http://otlp",
                "OTLP_API_KEY": "otlp-key",
                "ELASTICSEARCH_ENDPOINT": "http://es",
                "ELASTICSEARCH_API_KEY": "es-key",
                "MONITORING_OTLP_ENDPOINT": "http://mon",
                "MONITORING_API_KEY": "mon-key",
            },
            clear=True,
        ):
            context = get_template_context()
            assert context["otlp_endpoint"] == "http://otlp"
            assert context["otlp_api_key"] == "otlp-key"
            assert context["elasticsearch_endpoint"] == "http://es"
            assert context["elasticsearch_api_key"] == "es-key"
            assert context["monitoring_otlp_endpoint"] == "http://mon"
            assert context["monitoring_api_key"] == "mon-key"

    def test_missing_variables_default_to_empty(self):
        """Test that missing variables default to empty strings."""
        with patch.dict(os.environ, {}, clear=True):
            context = get_template_context()
            assert context["otlp_endpoint"] == ""
            assert context["otlp_api_key"] == ""
            assert context["elasticsearch_endpoint"] == ""
            assert context["elasticsearch_api_key"] == ""
            assert context["monitoring_otlp_endpoint"] == ""
            assert context["monitoring_api_key"] == ""
            assert context["num_instances"] == 3  # Default value

    def test_num_instances_from_env(self):
        """Test that NUM_INSTANCES is read from environment variable."""
        with patch.dict(os.environ, {"NUM_INSTANCES": "7"}, clear=True):
            context = get_template_context()
            assert context["num_instances"] == 7


class TestGenerateConfig:
    """Test the generate_config function."""

    def test_generate_with_otlp_endpoint(self):
        """Test config generation with OTLP endpoint."""
        template_dir = Path(__file__).parent
        with patch.dict(
            os.environ,
            {
                "OTLP_ENDPOINT": "https://otlp.example.com",
                "OTLP_API_KEY": "test-api-key",
            },
            clear=True,
        ):
            config = generate_config(template_dir=template_dir)
            assert "receivers:" in config
            assert "processors:" in config
            assert "exporters:" in config
            assert "service:" in config
            assert "otlp/1:" in config
            assert "https://otlp.example.com" in config
            assert "test-api-key" in config
            assert "metrics/otlp/1:" in config
            assert "elasticsearch/1:" not in config

    def test_generate_with_elasticsearch_endpoint(self):
        """Test config generation with Elasticsearch endpoint."""
        template_dir = Path(__file__).parent
        with patch.dict(
            os.environ,
            {
                "ELASTICSEARCH_ENDPOINT": "https://es.example.com",
                "ELASTICSEARCH_API_KEY": "test-es-key",
            },
            clear=True,
        ):
            config = generate_config(template_dir=template_dir)
            assert "receivers:" in config
            assert "processors:" in config
            assert "exporters:" in config
            assert "service:" in config
            assert "elasticsearch/1:" in config
            assert "https://es.example.com" in config
            assert "test-es-key" in config
            assert "metrics/elasticsearch/1:" in config
            assert "otlp/1:" not in config

    def test_generate_with_both_endpoints(self):
        """Test config generation with both OTLP and Elasticsearch endpoints."""
        template_dir = Path(__file__).parent
        with patch.dict(
            os.environ,
            {
                "OTLP_ENDPOINT": "https://otlp.example.com",
                "OTLP_API_KEY": "test-otlp-key",
                "ELASTICSEARCH_ENDPOINT": "https://es.example.com",
                "ELASTICSEARCH_API_KEY": "test-es-key",
            },
            clear=True,
        ):
            config = generate_config(template_dir=template_dir)
            assert "otlp/1:" in config
            assert "elasticsearch/1:" in config
            assert "metrics/otlp/1:" in config
            assert "metrics/elasticsearch/1:" in config

    def test_generate_with_monitoring(self):
        """Test config generation with monitoring endpoint."""
        template_dir = Path(__file__).parent
        with patch.dict(
            os.environ,
            {
                "OTLP_ENDPOINT": "https://otlp.example.com",
                "OTLP_API_KEY": "test-key",
                "MONITORING_OTLP_ENDPOINT": "https://mon.example.com",
                "MONITORING_API_KEY": "mon-key",
            },
            clear=True,
        ):
            config = generate_config(template_dir=template_dir)
            assert "telemetry:" in config
            assert "https://mon.example.com" in config
            assert "mon-key" in config
            assert "readers:" in config
            assert "level: none" not in config

    def test_generate_without_monitoring(self):
        """Test config generation without monitoring endpoint."""
        template_dir = Path(__file__).parent
        with patch.dict(
            os.environ,
            {
                "OTLP_ENDPOINT": "https://otlp.example.com",
                "OTLP_API_KEY": "test-key",
            },
            clear=True,
        ):
            config = generate_config(template_dir=template_dir)
            assert "telemetry:" in config
            assert "level: none" in config
            assert "readers:" not in config

    def test_generate_includes_all_receivers(self):
        """Test that all receivers are included in the config."""
        template_dir = Path(__file__).parent
        with patch.dict(
            os.environ,
            {
                "OTLP_ENDPOINT": "https://otlp.example.com",
                "OTLP_API_KEY": "test-key",
            },
            clear=True,
        ):
            config = generate_config(template_dir=template_dir)
            assert "hostmetrics/selfmon:" in config
            assert "hostmetrics/1:" in config
            assert "hostmetrics/2:" in config
            assert "hostmetrics/3:" in config

    def test_generate_includes_all_processors(self):
        """Test that all processors are included in the config."""
        template_dir = Path(__file__).parent
        with patch.dict(
            os.environ,
            {
                "OTLP_ENDPOINT": "https://otlp.example.com",
                "OTLP_API_KEY": "test-key",
            },
            clear=True,
        ):
            config = generate_config(template_dir=template_dir)
            assert "transform/selfmon:" in config
            assert "attributes/1:" in config
            assert "attributes/2:" in config
            assert "attributes/3:" in config
            assert "batch:" in config
            assert "resourcedetection:" in config

    def test_generate_includes_selfmon_pipeline(self):
        """Test that the selfmon pipeline is always included."""
        template_dir = Path(__file__).parent
        with patch.dict(
            os.environ,
            {
                "OTLP_ENDPOINT": "https://otlp.example.com",
                "OTLP_API_KEY": "test-key",
            },
            clear=True,
        ):
            config = generate_config(template_dir=template_dir)
            assert "metrics/selfmon:" in config
            assert "receivers: [hostmetrics/selfmon]" in config
            assert "exporters: [otlp/selfmon]" in config

    def test_generate_template_not_found(self, capsys):
        """Test error handling when template is not found."""
        with patch.dict(
            os.environ,
            {
                "OTLP_ENDPOINT": "https://otlp.example.com",
                "OTLP_API_KEY": "test-key",
            },
            clear=True,
        ):
            with pytest.raises(SystemExit) as exc_info:
                generate_config(template_dir="/nonexistent/path")
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "not found" in captured.err

    def test_generate_preserves_env_vars_in_template(self):
        """Test that environment variable syntax in template is preserved."""
        template_dir = Path(__file__).parent
        with patch.dict(
            os.environ,
            {
                "OTLP_ENDPOINT": "https://otlp.example.com",
                "OTLP_API_KEY": "test-key",
            },
            clear=True,
        ):
            config = generate_config(template_dir=template_dir)
            # These should be preserved as literal strings for the collector to process
            assert "${env:ITERATION}" in config
            assert "${env:INSTANCE}" in config

    def test_generate_with_custom_num_instances(self):
        """Test config generation with custom NUM_INSTANCES."""
        template_dir = Path(__file__).parent
        with patch.dict(
            os.environ,
            {
                "OTLP_ENDPOINT": "https://otlp.example.com",
                "OTLP_API_KEY": "test-key",
                "NUM_INSTANCES": "5",
            },
            clear=True,
        ):
            config = generate_config(template_dir=template_dir)
            # Should have instances 1-5
            assert "hostmetrics/1:" in config
            assert "hostmetrics/2:" in config
            assert "hostmetrics/3:" in config
            assert "hostmetrics/4:" in config
            assert "hostmetrics/5:" in config
            assert "hostmetrics/6:" not in config
            assert "attributes/1:" in config
            assert "attributes/5:" in config
            assert "otlp/5:" in config
            assert "metrics/otlp/5:" in config

    def test_generate_defaults_to_3_instances(self):
        """Test that default is 3 instances when NUM_INSTANCES is not set."""
        template_dir = Path(__file__).parent
        with patch.dict(
            os.environ,
            {
                "OTLP_ENDPOINT": "https://otlp.example.com",
                "OTLP_API_KEY": "test-key",
            },
            clear=True,
        ):
            config = generate_config(template_dir=template_dir)
            # Should have instances 1-3 (default)
            assert "hostmetrics/1:" in config
            assert "hostmetrics/2:" in config
            assert "hostmetrics/3:" in config
            assert "hostmetrics/4:" not in config

