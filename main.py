from dataclasses import dataclass
import datetime
import os

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
    arrival: Station
    departure: Station
    # pnr: int
    # price: float
    # train: Train


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


def parse_ticket(document: PDFDocument) -> Ticket:
    keys = (("Booked From:", "Departure"), ("To:", "Arrival"))

    return Ticket(
        departure=_parse_station(document, keys[0][0], keys[0][1]),
        arrival=_parse_station(document, keys[1][0], keys[1][1]),
    )


def main():
    filename = "tickets/ndls-cdg(6th Jan).pdf"
    path = os.path.join(os.getcwd(), filename)
    document = load_file(path)

    print(parse_ticket(document))


if __name__ == "__main__":
    main()
