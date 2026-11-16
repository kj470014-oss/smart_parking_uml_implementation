from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "smart-parking-demo-key"


# Enums from the UML diagram
class ParkingSpotType(Enum):
    HANDICAPPED = "Handicapped"
    COMPACT = "Compact"
    LARGE = "Large"
    MOTORBIKE = "Motorbike"
    ELECTRIC = "Electric"


class VehicleType(Enum):
    CAR = "Car"
    TRUCK = "Truck"
    ELECTRIC = "Electric"
    VAN = "Van"
    MOTORBIKE = "Motorbike"


class ParkingTicketStatus(Enum):
    ACTIVE = "Active"
    PAID = "Paid"
    LOST = "Lost"


class AccountStatus(Enum):
    ACTIVE = "Active"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"
    BLACKLISTED = "Blacklisted"
    NONE = "None"


@dataclass
class Location:
    streetAddress: str
    city: str
    state: str
    zipcode: str
    country: str


@dataclass
class Person:
    name: str
    address: Location
    email: str
    phone: str


@dataclass
class ParkingRate:
    hourNumber: int = 1
    rate: float = 30.0


@dataclass
class Vehicle:
    licenseNumber: str
    type: VehicleType


@dataclass
class ParkingTicket:
    ticketNumber: str
    issuedAt: datetime
    vehicle: Vehicle
    status: ParkingTicketStatus = ParkingTicketStatus.ACTIVE
    paidAt: datetime | None = None
    paidAmount: float = 0.0


@dataclass
class ParkingSpot:
    number: str
    type: ParkingSpotType
    free: bool = True
    vehicle: Vehicle | None = None
    ticket: ParkingTicket | None = None

    def getIsFree(self):
        return self.free


@dataclass
class ParkingFloor:
    name: str
    parkingSpots: list = field(default_factory=list)

    def updateParkingDisplayBoard(self):
        return sum(1 for spot in self.parkingSpots if spot.getIsFree())

    def addParkingSlot(self, spot):
        self.parkingSpots.append(spot)

    def assignVehicleToSlot(self, spot, vehicle, ticket):
        if not spot.free:
            return False
        spot.free = False
        spot.vehicle = vehicle
        spot.ticket = ticket
        return True

    def freeSlot(self, spot):
        spot.free = True
        spot.vehicle = None
        spot.ticket = None


@dataclass
class Payment:
    amount: float
    creationDate: datetime
    status: str = "Pending"

    def initiateTransaction(self):
        self.status = "Paid"
        return True


class CashTransaction(Payment):
    def __init__(self, amount, cashTendered):
        super().__init__(amount, datetime.now())
        self.cashTendered = cashTendered


class CreditCardTransaction(Payment):
    def __init__(self, amount, nameOnCard):
        super().__init__(amount, datetime.now())
        self.nameOnCard = nameOnCard


class Account:
    def __init__(self, userName, password, status=AccountStatus.ACTIVE):
        self.userName = userName
        self.password = password
        self.status = status


class Admin(Account):
    def addParkingFloor(self, parkingLot, floor):
        parkingLot.addParkingFloor(floor)
        return True


class ParkingAttendant(Account):
    def processTicket(self, ticket):
        return ticket.status == ParkingTicketStatus.ACTIVE


class ParkingLot:
    def __init__(self, lot_id, address, rate):
        self.id = lot_id
        self.address = address
        self.rate = rate
        self.floors = []
        self.tickets = []
        self.ticket_counter = 1000

    def addParkingFloor(self, floor):
        self.floors.append(floor)
        return True

    def addEntrancePanel(self):
        return EntrancePanel("ENTRY-01")

    def getNewParkingTicket(self, vehicle, spot):
        self.ticket_counter += 1
        ticket = ParkingTicket(
            ticketNumber=f"T{self.ticket_counter}",
            issuedAt=datetime.now(),
            vehicle=vehicle
        )
        if not spot or not spot.free:
            return None
        spot.free = False
        spot.vehicle = vehicle
        spot.ticket = ticket
        self.tickets.append(ticket)
        return ticket

    def isFull(self):
        return not any(spot.free for floor in self.floors for spot in floor.parkingSpots)

    def allSpots(self):
        return [spot for floor in self.floors for spot in floor.parkingSpots]


class EntrancePanel:
    def __init__(self, panel_id):
        self.id = panel_id

    def printTicket(self):
        return True


class ExitPanel:
    def __init__(self, panel_id):
        self.id = panel_id

    def scanTicket(self, ticket):
        return ticket is not None

    def processPayment(self, ticket, hours, method="cash"):
        if ticket.status != ParkingTicketStatus.ACTIVE:
            return False
        chargeable_hours = max(1, int(hours))
        amount = chargeable_hours * lot.rate.rate
        if method == "card":
            payment = CreditCardTransaction(amount, "Demo Card")
        else:
            payment = CashTransaction(amount, amount)
        payment.initiateTransaction()
        ticket.paidAmount = amount
        ticket.paidAt = datetime.now()
        ticket.status = ParkingTicketStatus.PAID
        return amount


@dataclass
class ParkingDisplayBoard:
    id: str

    def showEmptySpotNumber(self, spots):
        return [spot.number for spot in spots if spot.free]


# Set up sample parking lot and parking floors
location = Location("Main Road", "Bengaluru", "Karnataka", "560001", "India")
lot = ParkingLot("LOT-01", location, ParkingRate(hourNumber=1, rate=30.0))
floor_one = ParkingFloor("Ground Floor")
for index, spot_type in enumerate(
    [ParkingSpotType.COMPACT] * 6
    + [ParkingSpotType.LARGE] * 3
    + [ParkingSpotType.ELECTRIC] * 2
    + [ParkingSpotType.HANDICAPPED]
    + [ParkingSpotType.MOTORBIKE] * 4,
    start=1
):
    floor_one.addParkingSlot(ParkingSpot(f"A{index:02d}", spot_type))
lot.addParkingFloor(floor_one)

entrance_panel = lot.addEntrancePanel()
exit_panel = ExitPanel("EXIT-01")
display_board = ParkingDisplayBoard("BOARD-01")
attendant = ParkingAttendant("attendant", "demo")


@app.get("/")
def dashboard():
    spots = lot.allSpots()
    active_tickets = [ticket for ticket in lot.tickets if ticket.status == ParkingTicketStatus.ACTIVE]
    return render_template(
        "index.html",
        spots=spots,
        total=len(spots),
        available=sum(1 for spot in spots if spot.free),
        occupied=sum(1 for spot in spots if not spot.free),
        active_tickets=active_tickets,
        rate=lot.rate.rate,
        recent_tickets=list(reversed(lot.tickets[-6:]))
    )


@app.post("/park")
def park_vehicle():
    plate = request.form.get("licenseNumber", "").strip().upper()
    vehicle_value = request.form.get("vehicleType", "Car")
    if not plate:
        flash("Enter the vehicle registration number.", "error")
        return redirect(url_for("dashboard"))
    try:
        vehicle_type = VehicleType(vehicle_value)
    except ValueError:
        flash("Choose a valid vehicle type.", "error")
        return redirect(url_for("dashboard"))

    compatible = {
        VehicleType.MOTORBIKE: [ParkingSpotType.MOTORBIKE],
        VehicleType.ELECTRIC: [ParkingSpotType.ELECTRIC, ParkingSpotType.COMPACT, ParkingSpotType.LARGE],
        VehicleType.TRUCK: [ParkingSpotType.LARGE],
        VehicleType.VAN: [ParkingSpotType.LARGE],
        VehicleType.CAR: [ParkingSpotType.COMPACT, ParkingSpotType.LARGE, ParkingSpotType.HANDICAPPED],
    }
    spot = next(
        (s for s in lot.allSpots()
         if s.free and s.type in compatible[vehicle_type]),
        None
    )
    if not spot:
        flash("No compatible parking slot is currently available.", "error")
        return redirect(url_for("dashboard"))

    vehicle = Vehicle(plate, vehicle_type)
    ticket = lot.getNewParkingTicket(vehicle, spot)
    entrance_panel.printTicket()
    flash(f"Vehicle parked in {spot.number}. Ticket number: {ticket.ticketNumber}", "success")
    return redirect(url_for("dashboard"))


@app.post("/checkout/<ticket_number>")
def checkout(ticket_number):
    ticket = next((t for t in lot.tickets if t.ticketNumber == ticket_number), None)
    if not ticket or not exit_panel.scanTicket(ticket):
        flash("Ticket not found.", "error")
        return redirect(url_for("dashboard"))
    hours = request.form.get("hours", "1")
    method = request.form.get("paymentMethod", "cash")
    try:
        amount = exit_panel.processPayment(ticket, float(hours), method)
    except ValueError:
        amount = False
    if amount is False:
        flash("This ticket has already been paid or cannot be processed.", "error")
        return redirect(url_for("dashboard"))

    spot = next((s for s in lot.allSpots() if s.ticket == ticket), None)
    if spot:
        for floor in lot.floors:
            if spot in floor.parkingSpots:
                floor.freeSlot(spot)
                break
    flash(f"Payment of ₹{amount:.2f} successful. {ticket.vehicle.licenseNumber} has checked out.", "success")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
