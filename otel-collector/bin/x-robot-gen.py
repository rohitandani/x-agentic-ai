import subprocess
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='Generate x-robot OpenTelemetry configuration')
    parser.add_argument('--defaults', required=True, help='Path to defaults YAML')
    parser.add_argument('--receivers', required=True, help='Path to receivers YAML')
    parser.add_argument('--syslog', required=True, help='Path to Syslog config YAML')
    parser.add_argument('--output', required=True, help='Output path for x-robot-data.yaml')
    parser.add_argument('--receivers-output', required=True, help='Output path for receivers.yml')
    parser.add_argument('--pipelines-output', required=True, help='Output path for pipelines.yml')
    args = parser.parse_args()

    # Generate x-robot-data.yaml (scraper config)
    scraper_config = {
        'receivers': '${file:/etc/otelcol-contrib/receivers.yaml}',
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
        },
        'service': {
            'telemetry': {
                'metrics': {
                    'readers': [
                        {'pull': {'exporter': {'prometheus': {'host': '0.0.0.0', 'port': 8888}}}
                    ]
                }
            },
            'pipelines': '${file:/etc/otelcol-contrib/pipelines.yaml}'
        }
    }
    
    try:
        with open(args.output, 'w') as f:
            import yaml
            yaml.safe_dump(scraper_config, f, default_flow_style=False)
        print(f"Successfully wrote scraper config to {args.output}")
    except Exception as e:
        print(f"Error schrijven scraper config: {e}")
        sys.exit(1)

    # Invoke x_robot_config_helper.py to generate receivers.yml and pipelines.yml
    cmd = [
        'python', '/app/src/x_robot_config_helper.py',
        '--generate-configs',
        '--default-config-file', args.defaults,
        '--receiver-input-file', args.receivers,
        '--syslog-input-file', args.syslog,
        '--receiver-output-file', args.receivers_output,
        '--pipelines-output-file', args.pipelines_output
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running x_robot_config_helper.py: {e.stderr}")
        sys.exit(1)

if __name__ == '__main__':
    main()