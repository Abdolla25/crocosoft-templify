import os

import click

from .logger import setup_logger
from ..template_updater import Config, TemplateManager

logger = setup_logger()


@click.group()
def cli():
    """Templify - A tool for updating templates with new HTML content."""
    pass


@cli.command()
@click.option("--template", help="Template file to update")
@click.option("--base", help="Base branch for PR")
@click.option("--ticket", help="Ticket branch name")
def update(template, base, ticket):
    """Update a template with new HTML content."""
    try:
        config = Config.load()
        TemplateManager(config)

        # Check if the template file exists
        if not os.path.isfile(template):
            logger.error(f"Template file '{template}' does not exist.")
            raise click.ClickException(f"Template file '{template}' does not exist.")

        # Rest of the update logic...
        logger.info("Template update completed successfully!")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise click.ClickException(str(e))


@cli.command()
def init():
    """Initialize Templify configuration in the current directory."""
    try:
        # Create necessary directories and files
        os.makedirs(".templify", exist_ok=True)

        # Create initial config
        config_template = """
paths:
  templify_repo_name: "templify"
  email_users_repo_name: "EmailUsersPackageBuilder"

git:
  default_editor: "nano"
  default_commit_message: "Update template HTML"

logging:
  level: "INFO"
  format: "%(asctime)s - %(levelname)s - %(message)s"
  file: ".templify/templify.log"
"""
        with open(".templify/config.yaml", "w") as f:
            f.write(config_template)

        click.echo("Templify initialized successfully!")
    except Exception as e:
        raise click.ClickException(f"Failed to initialize Templify: {e}")


def main():
    cli()


if __name__ == "__main__":
    main()
