import argparse
import os
import pprint

from py_pdf_parser.loaders import load_file

import ticket_parser as TicketParser


class CustomArgsNamespace:
    dir: str | None = None
    files: list[str] = list()

    def __repr__(self) -> str:
        return f"Dir({self.dir}) Files({self.files})"


def setup_command_line_args() -> CustomArgsNamespace:
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f", "--files", nargs="+", help="list of filenames to be parsed"
    )
    group.add_argument(
        "-d", "--dir", help="directory containing list of files to be parsed"
    )

    args = CustomArgsNamespace()
    args = parser.parse_args(namespace=args)

    return args


def read_filenames_directory(directory: str, extension: str = ".pdf"):
    return (
        os.path.join(directory, filename)
        for filename in os.listdir(directory)
        if filename.endswith(extension)
    )


def main():
    args = setup_command_line_args()
    files = args.files if len(args.files) > 0 else read_filenames_directory(args.dir)

    tickets = [TicketParser.parse_ticket(load_file(filename)) for filename in files]
    pprint.pprint(tickets)


if __name__ == "__main__":
    main()
