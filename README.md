# Templify: A Template Updater Tool

[![Tests](https://github.com/Abdolla25/crocosoft-templify/workflows/Tests/badge.svg)](https://github.com/Abdolla25/crocosoft-templify/actions)
[![Coverage](https://codecov.io/gh/Abdolla25/crocosoft-templify/branch/main/graph/badge.svg)](https://codecov.io/gh/Abdolla25/crocosoft-templify)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview
Templify is a command-line tool designed to simplify the process of updating templates with new HTML content. It provides a robust interface for template management with Git integration.

## Installation

You can install Templify using the `setup.sh` script:

```bash
source ./setup.sh
```

## Quick Start

1. Initialize Templify in your project:
```bash
templify init
```

2. Update a template:
```bash
templify update --template my_template.sql --base main --ticket feature/update-template
```

## Features

- Template content validation
- Git integration for version control
- Branch management
- Pull request creation
- Logging and error tracking

## Development

### Setting up the development environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/templify.git
cd templify
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
