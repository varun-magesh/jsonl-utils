import json
import rich_click as click
from rich.pretty import pprint
import rich
import sys

@click.group()
def cli():
    pass

def _read_jsonl(file):
    with open(file) as f:
        return [json.loads(line) for line in f]

def _write_jsonl(data, file):
    if file == sys.stdout:
        for item in data:
            sys.stdout.write(json.dumps(item) + "\n")
        return
    with open(file, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")


@cli.command("combine", help="Combine multiple JSON files into one JSONL file")
@click.argument("output", type=click.Path(), required=True)
@click.argument("files", type=click.Path(exists=True), nargs=-1, required=True)
def combine(files, output):
    if output == "-":
        output = sys.stdout
    data = []
    for file in files:
        with open(file) as f:
            try:
                data.append(json.loads(f.read()))
            except json.JSONDecodeError:
                rich.print(f"[yellow]warning: {file} is not a valid JSON file; skipping[/yellow]", file=sys.stderr)
    _write_jsonl(data, output)

@cli.command("head", help="List first record of a jsonl file, in pretty format")
@click.argument("file", type=click.Path(exists=True))
def head(file):
    if file == "-":
        data = json.loads(sys.stdin.read())
    else:
        data = _read_jsonl(file)
    if not are_keys_consistent(data):
        rich.print("[red]warning: keys are not consistent[/red]", file=sys.stderr)
        return
    pprint(data[0])

@cli.command("clean", help="clean format of a jsonl file")
@click.argument("file", type=click.Path(exists=True))
@click.argument("output", type=click.Path(), required=True)
def clean(file, output):
    if file == "-":
        data = json.loads(sys.stdin.read())
    else:
        data = _read_jsonl(file)
    _write_jsonl(data, output)


def are_keys_consistent(data):
    keys = set(data[0].keys())
    for item in data[1:]:
        if set(item.keys()) != keys:
            return False
    return True

def main():
    cli()
