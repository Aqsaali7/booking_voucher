from dataclasses import dataclass
from typing import List

@dataclass
class TripVoucher:
    trip_id: str
    Arrival_date: str
    Departure: str
    duration: str
    guest_name: str
    guest_phone: str
    pax: str
    reference_id: str

@dataclass
class Hotel:
    name: str
    check_in: str
    check_out: str
    accommodation: str

@dataclass
class Activity:
    day: str
    start_time: str
    service: str
    pax_or_vehicle: str
    remarks: str = ""

@dataclass
class Voucher:
    title: str
    intro_text: str
    trip_voucher: TripVoucher
    hotels: List[Hotel]
    activities: List[Activity]
    inclusions: List[str]
    exclusions: List[str]
    helpline_company: str
    helpline_status: str
    helpline_phone: str
    terms: List[str]
