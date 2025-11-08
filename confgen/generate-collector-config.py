#!/usr/bin/env python3

import os
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound


def validate_environment():
    """Validate that required environment variables are set.
    
    Raises:
        SystemExit: If required environment variables are missing.
    """
    otlp_endpoint = os.getenv("OTLP_ENDPOINT")
    elasticsearch_endpoint = os.getenv("ELASTICSEARCH_ENDPOINT")
    otlp_api_key = os.getenv("OTLP_API_KEY")
    elasticsearch_api_key = os.getenv("ELASTICSEARCH_API_KEY")

    if not otlp_endpoint and not elasticsearch_endpoint:
        print("expected OTLP_ENDPOINT or ELASTICSEARCH_ENDPOINT", file=sys.stderr)
        sys.exit(1)

    if not otlp_api_key and not elasticsearch_api_key:
        print("expected OTLP_API_KEY or ELASTICSEARCH_API_KEY", file=sys.stderr)
        sys.exit(1)


def generate_config(template_dir=None):
    """Generate the collector configuration from the template.
    
    Args:
        template_dir: Optional directory containing the template. If None, uses the script's directory.
    
    Returns:
        str: The rendered configuration YAML.
    
    Raises:
        SystemExit: If template is not found.
    """
    if template_dir is None:
        template_dir = Path(__file__).parent
    else:
        template_dir = Path(template_dir)
    
    template_name = "collector-config.yaml.j2"

    # Set up Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    try:
        template = env.get_template(template_name)
    except TemplateNotFound:
        print(f"Error: Template '{template_name}' not found in {template_dir}", file=sys.stderr)
        sys.exit(1)

    # Get template context
    context = get_template_context()

    # Render template
    return template.render(**context)


def get_template_context():
    """Build the template context from environment variables."""
    # Get number of instances, defaulting to 3 for backward compatibility
    numpipelines = int(os.getenv("numpipelines", "3"))
    return {
        "otlp_endpoint": os.getenv("OTLP_ENDPOINT", ""),
        "otlp_api_key": os.getenv("OTLP_API_KEY", ""),
        "elasticsearch_endpoint": os.getenv("ELASTICSEARCH_ENDPOINT", ""),
        "elasticsearch_api_key": os.getenv("ELASTICSEARCH_API_KEY", ""),
        "monitoring_otlp_endpoint": os.getenv("MONITORING_OTLP_ENDPOINT", ""),
        "monitoring_api_key": os.getenv("MONITORING_API_KEY", ""),
        "numpipelines": numpipelines,
    }


def main():
    """Main function to generate the configuration."""
    validate_environment()
    output = generate_config()
    print(output)


if __name__ == "__main__":
    main()

