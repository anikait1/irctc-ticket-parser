import datetime
import argparse
import os
import pprint
from dataclasses import dataclass

from py_pdf_parser.loaders import load_file, PDFDocument


@dataclass
class Station:
    name: str
    time: datetime.datetime


@dataclass
class Train:
    number: int
    name: str


@dataclass
class Ticket:
    departure: Station
    arrival: Station
    pnr: int
    price: float
    train: Train


class CustomArgsNamespace:
    directory: str | None = None
    files: list[str] = list()

    def __repr__(self) -> str:
        return f"Dir({self.directory}) Files({self.files})"


def _parse_station(document: PDFDocument, station_key: str, timing_key: str):
    station_element = document.elements.filter_by_text_equal(
        station_key
    ).extract_single_element()
    station_name = document.elements.below(station_element)[0].text()

    regex_pattern = rf"{timing_key}\*\s\d{{2}}:\d{{2}}\s\d{{1,2}}\s\w{{3}}\s\d{{4}}"
    _, time = (
        document.elements.filter_by_regex(regex_pattern).extract_single_element().text()
    ).split(f"{timing_key}*")

    return Station(
        name=station_name,
        time=datetime.datetime.strptime(time.strip(), "%H:%M %d %b %Y"),
    )


def _parse_pnr(document: PDFDocument) -> int:
    pnr_text_element = document.elements.filter_by_text_equal(
        "PNR"
    ).extract_single_element()
    pnr = document.elements.below(pnr_text_element)[0].text()

    return int(pnr)


def _parse_final_price(document: PDFDocument) -> float:
    total_fare_text_element = document.elements.filter_by_text_equal(
        "Total Fare (all inclusive)"
    ).extract_single_element()
    price_text_label = (
        document.elements.to_the_right_of(total_fare_text_element)
        .extract_single_element()
        .text()
    )
    _, price = price_text_label.split("₹")

    return float(price.strip())


def _parse_train(document: PDFDocument) -> Train:
    train_info_label_element = document.elements.filter_by_text_equal(
        "Train No./Name"
    ).extract_single_element()
    train_info = document.elements.below(train_info_label_element)[0].text()

    number, name = train_info.split("/")
    return Train(int(number.strip()), name.strip())


def parse_ticket(document: PDFDocument) -> Ticket:
    departure = _parse_station(document, "Booked From:", "Departure")
    arrival = _parse_station(document, "To:", "Arrival")
    pnr = _parse_pnr(document)
    price = _parse_final_price(document)
    train = _parse_train(document)

    return Ticket(
        departure=departure, arrival=arrival, pnr=pnr, price=price, train=train
    )


def setup_command_line_args() -> CustomArgsNamespace:
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f", "--files", nargs="+", help="list of filenames to be parsed"
    )
    group.add_argument(
        "-d", "--dir", help="directory containing list of files to be parsed"
    )

    args = parser.parse_args(namespace=CustomArgsNamespace())
    pprint.pprint(args) # TODO - add logging instead of pprint

    return args


def main():
    args = setup_command_line_args()
    # TODO - handle directory and files
    filename = args.files[0]
    path = os.path.join(os.getcwd(), filename)
    document = load_file(path)

    pprint.pprint(parse_ticket(document))


if __name__ == "__main__":
    main()
