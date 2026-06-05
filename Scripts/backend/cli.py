from typing import Optional

import typer

from .config import ConverterConfig
from .converter import convert_single_page
from .utils.file_manager import FileManager

app = typer.Typer(help="Convert documentation pages into skill files.")


def prompt_for_api_key(file_manager: FileManager) -> None:
    api_key = ""
    while not api_key:
        api_key = typer.prompt("Enter gemini api key").strip()
        if not api_key:
            typer.echo("Gemini API key is required.")

    file_manager.update_file_api_key(api_key)


def ensure_config_api_key(file_manager: FileManager) -> None:
    if not file_manager.config_file_exist():
        file_manager.prepare_default_configfile()

    config = file_manager.load_config()
    if not config.api_key.strip():
        prompt_for_api_key(file_manager)


@app.command()
def init() -> None:
    """Create the default config file and save a Gemini API key."""
    file_manager = FileManager(ConverterConfig())

    if not file_manager.config_file_exist():
        file_manager.prepare_default_configfile()
        prompt_for_api_key(file_manager)
        typer.echo("Config file created.")
        return

    config = file_manager.load_config()
    if not config.api_key.strip():
        prompt_for_api_key(file_manager)
        typer.echo("Config file updated.")


@app.command("update-api-key")
def update_api_key() -> None:
    """Update the Gemini API key in the config file."""
    file_manager = FileManager(ConverterConfig())

    if not file_manager.config_file_exist():
        file_manager.prepare_default_configfile()

    prompt_for_api_key(file_manager)
    typer.echo("API key updated.")


@app.command()
def add(
    page_url: str = typer.Argument(..., help="Documentation page URL to convert."),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Directory where the generated skill file will be saved.",
    ),
) -> None:
    """Convert one documentation page into a skill file."""
    if not page_url.strip():
        raise typer.BadParameter("Page URL is required.")

    if output is None or not output.strip():
        raise typer.BadParameter("Output directory is required. Use --output ./skills.")

    file_manager = FileManager(ConverterConfig())
    ensure_config_api_key(file_manager)

    result = convert_single_page(page_url=page_url, output_dir=output)
    if not result.get("success"):
        typer.echo(result.get("error", "Conversion failed."), err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Skill file created: {result.get('output_file')}")
