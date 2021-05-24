# B2C2 python client
## Installation
```bash
python3 -m venv ./venv
source venv/bin/activate
python setup.py install
```

Copy `config.yaml` from `examples` to project root and edit it. Create the directory for logs:
```bash
$ cp examples/config.yaml .
$ mkdir -p log
```
## Usage
Run tests:
```bash
$ pytest test
```

Client usage:
```bash
$ b2c2-python-client 
Usage: b2c2-python-client [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  get-rfq           Post a Request For Quote
  list-instruments  List all your tradable instruments.
  send-order        API endpoint to send orders.
  show-balance      This shows the available balances in the supported..
```

## Jenkins integration
Requires following changes on Jenkins side:

https://tox.readthedocs.io/en/latest/example/jenkins.html

## Roadmap
v0.2.0 
- add Dockerfile
- REST server
- web interface
- Selenium tests 