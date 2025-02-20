# Templify: A Template Updater Tool

## Overview
Templify is a command-line tool designed to simplify the process of updating templates with new HTML content. It provides a set of aliases and a Python script to streamline the workflow.

## Installation
To install Templify, simply run the `setup.sh` script in the project directory:

```bash
source ./setup.sh
```

This will add the necessary aliases to your `~/.bashrc` file.

## Usage

### Aliases
The following aliases are available:

- `templify-help`: Displays the help message for the template_updater.py script.
- `templify-clean`: Removes the updated_template_set.sql file.
- `templify-edit`: Opens the updated_template_set.sql file in the default editor (nano) and removes any existing file.
- `templify`: Updates the template with the new HTML content and commits the changes.

### Example Usage
To update a template, simply run:

```bash
templify
```

This will prompt you to select a template to update, and then update the template with the new HTML content.

## Manual Setup on Bashrc File
To manually add the Templify aliases to your `~/.bashrc` file, add the following lines:

```bash
# Templify
alias templify-help='python /path/to/templify/template_updater.py -h'
alias templify-clean='rm -f /path/to/templify/updated_template_set.sql'
alias templify-edit='templify-clean && nano /path/to/templify/updated_template_set.sql'
alias templify='templify-edit && python /path/to/templify/template_updater.py'
```

Replace `/path/to/templify` with the actual path to the Templify project directory.
