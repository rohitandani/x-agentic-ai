"""
x_robot_config_helper.py

A command-line tool for simplifying x-robot configurations. It takes input files containing
defaults for BIG-IP receivers and individual BIG-IP targets with override values, plus a Syslog
configuration file. The output is written to /otel-collector/receivers.yml and
/otel-collector/pipelines/pipelines.yml for the OpenTelemetry Collector.

Key Features:
- Generate output configurations based on default settings, per-device inputs, and Syslog settings.
- Supports dry-run mode to preview changes without writing to files.
- Robust error handling and logging for configuration processing.

Command-Line Interface:
- --generate-configs: Generate new configurations based on input files.
- --dry-run: Preview changes without writing to files.
- --default-config-file: Path to default settings file (default: /app/config/x_robot_ai_data.yaml).
- --receiver-input-file: Path to BIG-IP receiver settings file (default: /app/config/bigip_receivers.yml).
- --syslog-input-file: Path to Syslog settings file (default: /app/config/syslog/syslog_data.yaml).
- --receiver-output-file: Output path for receivers.yml (default: /app/otel-collector/receivers.yml).
- --pipelines-output-file: Output path for pipelines.yml (default: /app/otel-collector/pipelines/pipelines.yml).

Usage Example:
    python /app/src/x_robot_config_helper.py --generate-configs
"""

import argparse
import logging
import yaml
from copy import deepcopy

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_yaml(path):
    """Load a YAML file from the specified path."""
    try:
        with open(path, "r") as f:
            content = yaml.safe_load(f) or {}
            logging.info("Successfully loaded '%s'.", path)
            return content
    except FileNotFoundError:
        logging.error("Error: The file '%s' does not exist.", path)
        return None
    except PermissionError:
        logging.error("Error: Permission denied when trying to open '%s'.", path)
        return None
    except yaml.YAMLError as e:
        logging.error("Error reading YAML file '%s': %s", path, e)
        return None

def write_yaml_to_file(data, path):
    """Write a dictionary to a YAML file."""
    try:
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
            logging.info("Successfully wrote data to '%s'.", path)
    except IOError as e:
        logging.error("Error writing to YAML file '%s': %s", path, e)

def load_default_config(args):
    """Load the default configuration settings from a YAML file."""
    logging.info("Loading x-robot Default Settings in %s...", args.default_config_file)
    return load_yaml(args.default_config_file)

def load_receiver_config(args):
    """Load the BIG-IP receiver configuration settings from a YAML file."""
    logging.info("Loading Per-Receiver (BigIP) Settings in %s...", args.receiver_input_file)
    return load_yaml(args.receiver_input_file)

def load_syslog_config(args):
    """Load the Syslog configuration settings from a YAML file."""
    logging.info("Loading Syslog Settings in %s...", args.syslog_input_file)
    return load_yaml(args.syslog_input_file)

def deep_merge(dict1, dict2):
    """Deep merge two dictionaries."""
    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            deep_merge(dict1[key], value)
        else:
            dict1[key] = value
    return dict1

def generate_receiver_configs(receiver_input_configs, syslog_config, default_config):
    """Generate merged receiver configurations from BIG-IP and Syslog inputs."""
    merged_config = {}
    defaults = deepcopy(default_config.get("bigip_receiver_defaults", {}))
    
    # Merge BIG-IP receivers
    for k, v in receiver_input_configs.items():
        this_cfg = deepcopy(v)
        if this_cfg.get("pipeline"):
            del this_cfg["pipeline"]
        merged_config[k] = deep_merge(defaults, this_cfg)
    
    # Add Syslog receiver
    if syslog_config and 'receivers' in syslog_config:
        merged_config.update(syslog_config['receivers'])
    
    return {'receivers': merged_config}

def generate_pipeline_configs(receiver_input_configs, default_config, args):
    """Generate pipeline configurations based on receiver inputs."""
    pipelines = {
        'metrics': {
            'receivers': [name for name in receiver_input_configs if name.startswith('bigip/')],
            'processors': ['batch/local'],
            'exporters': ['otlphttp/metrics-local', 'debug/x-agentic-ai']
        },
        'logs': {
            'receivers': ['syslog'],
            'processors': ['batch/local'],
            'exporters': ['debug/x-agentic-ai']
        }
        # Optional: F5 Datafabric pipeline
        # 'metrics/f5-datafabric': {
        #     'receivers': [name for name in receiver_input_configs if name.startswith('bigip/')],
        #     'processors': ['batch/f5-datafabric', 'interval/f5-datafabric', 'attributes/f5-datafabric'],
        #     'exporters': ['otlp/f5-datafabric']
        # }
    }
    
    f5_pipeline_default = default_config.get("f5_pipeline_default")
    enabled = default_config.get("f5_data_export", False)
    if f5_pipeline_default and enabled:
        logging.info("F5 Datafabric pipeline enabled.")
    else:
        logging.warning(
            "The f5_data_export=true and f5_pipeline_default fields are required to "
            "export metrics to F5 Datafabric. Contact your F5 Sales Rep for a Sensor ID and Access Token."
        )
    
    final_pipelines = {'service': {'pipelines': {}}}
    for pipeline, settings in pipelines.items():
        if settings.get('receivers'):
            final_pipelines['service']['pipelines'][pipeline] = settings
    return final_pipelines

def generate_configs(args):
    """Generate configuration files for receivers and pipelines."""
    logging.info(
        "Generating configs from %s, %s, and %s...",
        args.default_config_file, args.receiver_input_file, args.syslog_input_file
    )
    default_config = load_default_config(args)
    receiver_input_configs = load_receiver_config(args)
    syslog_config = load_syslog_config(args)
    
    if not default_config or not receiver_input_configs or not syslog_config:
        return None, None
    
    logging.info("Generating receiver configs...")
    receiver_output_configs = generate_receiver_configs(receiver_input_configs, syslog_config, default_config)
    logging.info("Generating pipeline configs...")
    pipeline_output_configs = generate_pipeline_configs(receiver_input_configs, default_config, args)
    
    return receiver_output_configs, pipeline_output_configs

def get_args():
    """Initialize the argument parser."""
    parser = argparse.ArgumentParser(
        description="A tool for x-robot configuration management."
    )
    parser.add_argument(
        "--generate-configs",
        action="store_true",
        help="Generate new configurations based on input files."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to files."
    )
    parser.add_argument(
        "--default-config-file",
        type=str,
        default="/app/config/x_robot_ai_data.yaml",
        help="Path to the default settings file."
    )
    parser.add_argument(
        "--receiver-input-file",
        type=str,
        default="/app/config/bigip_receivers.yml",
        help="Path to the BIG-IP receiver settings file."
    )
    parser.add_argument(
        "--syslog-input-file",
        type=str,
        default="/app/config/syslog/syslog_data.yaml",
        help="Path to the Syslog settings file."
    )
    parser.add_argument(
        "--receiver-output-file",
        type=str,
        default="/app/otel-collector/receivers.yml",
        help="Output path for receivers.yml."
    )
    parser.add_argument(
        "--pipelines-output-file",
        type=str,
        default="/app/otel-collector/pipelines/pipelines.yml",
        help="Output path for pipelines.yml."
    )
    return parser

def main():
    """Main entry point for the configuration management tool."""
    parser = get_args()
    args = parser.parse_args()

    if args.generate_configs:
        receiver_config, pipeline_config = generate_configs(args)
        if not receiver_config or not pipeline_config:
            return
        logging.info(
            "Built the following pipeline file:\n\n%s",
            yaml.dump(pipeline_config, default_flow_style=False)
        )
        logging.info(
            "Built the following receiver file:\n\n%s",
            yaml.dump(receiver_config, default_flow_style=False)
        )
        if not args.dry_run:
            write_yaml_to_file(pipeline_config, args.pipelines_output_file)
            write_yaml_to_file(receiver_config, args.receiver_output_file)
        return

    logging.info("No action specified. Use --generate-configs to generate configurations.")

if __name__ == "__main__":
    main()