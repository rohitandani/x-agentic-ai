import yaml
import sys
import argparse
import os

def load_yaml(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def merge_configs(defaults, receivers, syslog):
    config = {
        'receivers': {},
        'processors': {
            'batch/local': {},
            'batch/f5-datafabric': {'send_batch_max_size': 8192},
            'interval/f5-datafabric': {'interval': '300s'},
            'attributes/f5-datafabric': {
                'actions': [
                    {'key': 'dataType', 'action': 'upsert', 'value': 'x-agentic-ai-metric'}
                ]
            }
        },
        'exporters': {
            'otlphttp/metrics-local': {'endpoint': 'http://prometheus:9090/api/v1/otlp'},
            'debug/x-agentic-ai': {
                'verbosity': 'basic',
                'sampling_initial': 5,
                'sampling_thereafter': 200
            }
            # Optional: 'otlp/f5-datafabric': {...} (commented out)
        },
        'service': {
            'telemetry': {
                'metrics': {
                    'readers': [
                        {'pull': {'exporter': {'prometheus': {'host': '0.0.0.0', 'port': 8888}}}
                    ]
                }
            },
            'pipelines': {
                'metrics': {
                    'receivers': [],
                    'processors': ['batch/local'],
                    'exporters': ['otlphttp/metrics-local', 'debug/x-agentic-ai']
                },
                'logs': {
                    'receivers': ['syslog'],
                    'processors': ['batch/local'],
                    'exporters': ['debug/x-agentic-ai']
                }
            }
        }
    }
    
    # Add BIG-IP receivers
    if receivers:
        for name, receiver in receivers.items():
            config['receivers'][name] = {**defaults.get('bigip_receiver_defaults', {}), **receiver}
            config['service']['pipelines']['metrics']['receivers'].append(name)
    
    # Add Syslog receiver
    if syslog and 'receivers' in syslog:
        config['receivers'].update(syslog['receivers'])
    
    return config

def main():
    parser = argparse.ArgumentParser(description='Generate x-agentic-ai OpenTelemetry configuration')
    parser.add_argument('--defaults', required=True, help='Path to defaults YAML')
    parser.add_argument('--receivers', required=True, help='Path to receivers YAML')
    parser.add_argument('--syslog', required=True, help='Path to Syslog config YAML')
    parser.add_argument('--output', required=True, help='Output path for x-agentic-ai-scraper-config.yaml')
    args = parser.parse_args()
    
    defaults = load_yaml(args.defaults)
    receivers = load_yaml(args.receivers)
    syslog = load_yaml(args.syslog)
    
    config = merge_configs(defaults, receivers, syslog)
    
    with open(args.output, 'w') as f:
        yaml.safe_dump(config, f, default_flow_style=False)

if __name__ == '__main__':
    main()