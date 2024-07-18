import os
import sys
from pathlib import Path
import argparse
import json
import csv

from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text
from rich.style import Style

from processor import process_file, process_directory, process_url
from extractor import extract_text, is_url
from database import (
    create_tables,
    add_file_to_db,
    search_files,
    filter_by_tags,
    get_stats,
    add_tag,
    rename_tag,
    export_db,
    import_db,
    get_file_by_id,
    update_file_tags,
    list_files,
    get_tags_for_file,
)
from config import colors


def main():
    create_tables()
    parser = argparse.ArgumentParser(
        description="Process and manage files metadata.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add
    add_parser = subparsers.add_parser(
        "add", aliases=["a"], help="Add a file or URL to the database"
    )
    add_parser.add_argument(
        "input_path", type=str, help="Relative or absolute path to the file or URL"
    )

    # Search
    search_parser = subparsers.add_parser(
        "search", aliases=["s"], help="Search files by keywords"
    )
    search_parser.add_argument("keywords", type=str, help="Keywords to search")
    search_parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)",
    )

    # Filter
    filter_parser = subparsers.add_parser(
        "filter", aliases=["f"], help="Filter files by tags"
    )
    filter_parser.add_argument(
        "tags",
        nargs="?",
        default="",
        help="Comma-separated list of tags (default: empty)",
    )
    filter_parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)",
    )

    # List
    list_parser = subparsers.add_parser("list", aliases=["ls", "l"], help="List files")
    list_parser.add_argument(
        "--date-after", type=str, help="List files created after this date (YYYY-MM-DD)"
    )
    list_parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)",
    )

    # Stats
    stats_parser = subparsers.add_parser(
        "stats", aliases=["st"], help="Show statistics"
    )
    stats_parser.add_argument(
        "--by-type", action="store_true", help="Show stats by file type"
    )
    stats_parser.add_argument("--by-tag", action="store_true", help="Show stats by tag")

    # Tag management
    tag_parser = subparsers.add_parser("tag", aliases=["t"], help="Manage tags")
    tag_subparsers = tag_parser.add_subparsers(dest="tag_command")

    tag_add_parser = tag_subparsers.add_parser("add", help="Add a tag to a file")
    tag_add_parser.add_argument("file_id", type=int, help="File ID")
    tag_add_parser.add_argument("tag", type=str, help="Tag to add")

    tag_rename_parser = tag_subparsers.add_parser("rename", help="Rename a tag")
    tag_rename_parser.add_argument("old_name", type=str, help="Old tag name")
    tag_rename_parser.add_argument("new_name", type=str, help="New tag name")

    # Export/Import
    export_parser = subparsers.add_parser(
        "export", aliases=["e"], help="Export database"
    )
    import_parser = subparsers.add_parser(
        "import", aliases=["i"], help="Import database"
    )

    # Open
    open_parser = subparsers.add_parser("open", aliases=["o"], help="Open a file")
    open_parser.add_argument("file_id", type=int, help="File ID to open")

    args = parser.parse_args()

    try:
        if args.command in ["add", "a"]:
            if is_url(args.input_path):
                process_url(args.input_path)
            else:
                path = os.path.abspath(args.input_path)
                if os.path.isfile(path):
                    process_file(path)
                elif os.path.isdir(path):
                    process_directory(path)
                else:
                    raise ValueError(
                        f"The input path {path} is neither a file nor a directory."
                    )
            print("Processing completed successfully.")

        elif args.command in ["search", "s"]:
            results = search_files(args.keywords)
            output_results(results, args.format)

        elif args.command in ["filter", "f"]:
            tags = args.tags.split(",") if args.tags else []
            results = filter_by_tags(tags)
            output_results(results, args.format)

        elif args.command in ["list", "l", "ls"]:
            results = list_files(args.date_after)
            output_results(results, args.format)

        elif args.command in ["stats", "st"]:
            if args.by_type:
                stats = get_stats("file_type")
            elif args.by_tag:
                stats = get_stats("tag")
            else:
                stats = get_stats()
            output_stats(stats)

        elif args.command in ["tag", "t"]:
            if args.tag_command == "add":
                add_tag(args.file_id, args.tag)
                print(f"Tag '{args.tag}' added to file {args.file_id}")
            elif args.tag_command == "rename":
                rename_tag(args.old_name, args.new_name)
                print(f"Tag renamed from '{args.old_name}' to '{args.new_name}'")

        elif args.command in ["export", "e"]:
            export_db(sys.stdout)
            print("Database exported successfully.")

        elif args.command in ["import", "i"]:
            import_db(sys.stdin)
            print("Database imported successfully.")

        elif args.command in ["open", "o"]:
            file_info = get_file_by_id(args.file_id)
            if file_info:
                os.system(f"xdg-open '{file_info['path']}'")
            else:
                print(f"No file found with ID {args.file_id}")

    except Exception as e:
        print(f"An error occurred: {e}")


def output_results(results, format):
    if format == "json":
        print(json.dumps(results, indent=2))
    elif format == "csv":
        writer = csv.DictWriter(sys.stdout, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    else:  # table format
        console = Console()
        table = Table(
            show_header=True,
            header_style=f"bold {colors['header_text']}",
            box=box.SIMPLE,
            border_style=colors["border"],
            row_styles=[f"on {colors['row_bg_1']}", f"on {colors['row_bg_2']}"],
            expand=True,
            pad_edge=True,
            padding=(1, 1),
        )

        if results:
            columns = ["ID", "Title", "Summary", "File Type", "Path", "Tags"]
            for column in columns:
                table.add_column(
                    column, overflow="fold", no_wrap=False, vertical="middle"
                )

            for result in results:
                tags = ", ".join(get_tags_for_file(result["id"]))
                row = [
                    Text(str(result["id"]), style=colors["id"]),
                    Text(result["title"], overflow="fold", style=colors["title"]),
                    Text(result["summary"], overflow="fold", style=colors["summary"]),
                    Text(result["file_type"], style=colors["file_type"]),
                    Text(result["path"], overflow="fold", style=colors["path"]),
                    Text(tags, overflow="fold", style=colors["tags"]),
                ]
                table.add_row(*row)

        console.print(table)


def output_stats(stats):
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Category", style="dim", justify="right")
    table.add_column("Count", justify="right")

    for key, value in stats.items():
        table.add_row(str(key), str(value))

    console.print(table)


if __name__ == "__main__":
    main()
