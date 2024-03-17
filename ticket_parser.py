import datetime
from dataclasses import dataclass
from typing import Optional

from py_pdf_parser.loaders import load_file, PDFDocument
from py_pdf_parser.exceptions import NoElementFoundError, MultipleElementsFoundError


class FieldParseError(Exception):
    def __init__(
        self, original_exception: Optional[Exception] = None, *args: object
    ) -> None:
        super().__init__(*args)
        self.original_exception = original_exception


@dataclass
class Station:
    name: str
    time: datetime.datetime


@dataclass
class Train:
    number: str
    name: str


@dataclass
class Ticket:
    departure: Station
    arrival: Station
    pnr: str
    price: float
    train: Train


def _parse_station(document: PDFDocument, station_key: str, timing_key: str):
    """
    TODO - specify what the station key and timing key are supposed to mean
    """
    try:
        station_element = document.elements.filter_by_text_equal(
            station_key
        ).extract_single_element()
    except (NoElementFoundError, MultipleElementsFoundError) as error:
        return FieldParseError(error)

    elements_below_station = document.elements.below(station_element)
    if len(elements_below_station) < 1:
        return FieldParseError()

    station_name = elements_below_station[0].text()
    regex_pattern = rf"{timing_key}\*\s\d{{2}}:\d{{2}}\s\d{{1,2}}\s\w{{3}}\s\d{{4}}"

    try:
        _, time = (
            document.elements.filter_by_regex(regex_pattern)
            .extract_single_element()
            .text()
        ).split(f"{timing_key}*")
    except (NoElementFoundError, MultipleElementsFoundError) as error:
        return FieldParseError(error)

    return Station(
        name=station_name,
        time=datetime.datetime.strptime(time.strip(), "%H:%M %d %b %Y"),
    )


def _parse_pnr(document: PDFDocument) -> str:
    """
    TODO - specify the logic of finding "PNR" and getting data below
    it
    """
    try:
        pnr_text_element = document.elements.filter_by_text_equal(
            "PNR"
        ).extract_single_element()
    except (NoElementFoundError, MultipleElementsFoundError) as error:
        return FieldParseError(error)

    elements_below_pnr_text = document.elements.below(pnr_text_element)
    if len(elements_below_pnr_text) < 1:
        return FieldParseError()

    pnr = elements_below_pnr_text[0].text()
    return pnr


def _parse_final_price(document: PDFDocument) -> float:
    """
    TODO
    """
    try:
        total_fare_text_element = document.elements.filter_by_text_equal(
            "Total Fare (all inclusive)"
        ).extract_single_element()
    except (NoElementFoundError, MultipleElementsFoundError) as error:
        return FieldParseError(error)

    try:
        price_text_label = (
            document.elements.to_the_right_of(total_fare_text_element)
            .extract_single_element()
            .text()
        )
    except (NoElementFoundError, MultipleElementsFoundError) as error:
        return FieldParseError(error)

    price = (
        price_text_label.split("₹")[-1] if "₹" in price_text_label else price_text_label
    )
    return float(price.strip())


def _parse_train(document: PDFDocument) -> Train:
    try:
        train_info_label_element = document.elements.filter_by_text_equal(
            "Train No./Name"
        ).extract_single_element()
    except (NoElementFoundError, MultipleElementsFoundError) as error:
        return FieldParseError(error)

    elements_below_train_info_element = document.elements.below(
        train_info_label_element
    )
    if len(elements_below_train_info_element) < 1:
        return FieldParseError()

    train_info = document.elements.below(train_info_label_element)[0].text()
    number, name = train_info.split("/")
    return Train(number.strip(), name.strip())


def parse_ticket(document: PDFDocument) -> list[dict[str, FieldParseError]] | Ticket:
    departure = _parse_station(document, "Booked From:", "Departure")
    arrival = _parse_station(document, "To:", "Arrival")
    pnr = _parse_pnr(document)
    price = _parse_final_price(document)
    train = _parse_train(document)

    errors = [
        {"field": field, "error": value}
        for field, value in (
            ("depature", departure),
            ("arrival", arrival),
            ("pnr", pnr),
            ("price", price),
            ("train", train),
        )
        if isinstance(value, FieldParseError)
    ]

    if len(errors) != 0:
        return errors

    return Ticket(
        departure=departure, arrival=arrival, pnr=pnr, price=price, train=train
    )
