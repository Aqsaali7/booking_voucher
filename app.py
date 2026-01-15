from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import os

app = Flask(__name__)

# ---------------- CONSTANT DATA ----------------
LOGO_PATH = "static/triplogo.png"

HELPLINE = [["24x7 Operational", "HIREN PAREKH", "+97 155 4739783"]]

INCLUSIONS = [
    "Inclusions as per itinerary",
    "Breakfast and Dinner",
    "Visa",
    "Dubai Hotel and Tourism Dirham Fees"
]

EXCLUSIONS = [
    "Arrival day breakfast",
    "Departure day Dinner",
    "Meal other than mentioned",
    "Anything not in inclusions"
]

TERMS = [
    "Cancellation charges apply as per policy.",
    "Trip itinerary may change due to weather.",
    "Company is not responsible for lost belongings.",
    "Late arrivals may miss scheduled activities.",
    "Extra services are charged separately.",
    "Travel insurance is recommended.",
    "Meals are included unless otherwise stated."
]

ADDRESS = (
    "P.O Box: 46331, Bur Dubai Dubai. U.A.E | "
    "Tel: +9714 3554935 | Fax: +971 4 3554935 | "
    "Email: info@overnetdubai.com<br/>www.overnetdubai.com"
)

# ---------------- COLORS ----------------
LIGHT_BLUE = colors.HexColor("#E6F0F8")
GREY = colors.HexColor("#BFBFBF")
DARK_BLUE = colors.HexColor("#1A5276")
ADDRESS_BLUE = colors.HexColor("#1A75D2")

# ---------------- HEADER ----------------
def draw_first_page_header(canvas, doc):
    canvas.saveState()
    w, h = A4

    # Background bar
    canvas.setFillColor(LIGHT_BLUE)
    canvas.rect(0, h - 120, w, 120, fill=1, stroke=0)

    # LEFT TEXT (Welcome to Dubai)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(DARK_BLUE)
    canvas.drawString(30, h - 55, "Welcome to Dubai")

    # CENTER TITLE
    canvas.setFont("Helvetica-Bold", 22)
    canvas.drawCentredString(w / 2, h - 55, "TRAVEL ITINERARY")

    # RIGHT LOGO
    if os.path.exists(LOGO_PATH):
        canvas.drawImage(
            LOGO_PATH,
            w - 160,
            h - 90,
            110,
            55,
            preserveAspectRatio=True,
            mask="auto"
        )

    # RIGHT CAPTION (under logo)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.black)
    canvas.drawRightString(
        w - 30,
        h - 105,
        "The itinerary must be carried by guest all the time along with visa copy"
    )

    canvas.restoreState()


def draw_later_page_header(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(A4[0] - 30, A4[1] - 30, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()

# ---------------- STYLES ----------------
styles = getSampleStyleSheet()

heading_style = ParagraphStyle(
    "heading",
    fontName="Helvetica",
    fontSize=12,
    alignment=TA_CENTER,
    backColor=LIGHT_BLUE,
    borderColor=GREY,
    borderWidth=1,
    spaceBefore=12,
    spaceAfter=6,
    padding=6
)

text_style = ParagraphStyle(
    "text",
    fontSize=9,
    leading=13,
    alignment=TA_LEFT,
    wordWrap="CJK"
)

address_style = ParagraphStyle(
    "address",
    fontSize=9,
    alignment=TA_CENTER,
    textColor=ADDRESS_BLUE
)

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_pdf():
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=140,
        leftMargin=30,
        rightMargin=30,
        bottomMargin=50
    )

    elements = []

    # ---------------- TRIP VOUCHER ----------------
    elements.append(Paragraph("Trip Voucher", heading_style))

    trip_table = Table([
        ["1. Trip ID", request.form.get("trip_id", "")],
        ["2. Arrival Date", request.form.get("arrival_date", "")],
        ["3. Departure", request.form.get("departure", "")],
        ["4. Duration", request.form.get("duration", "")],
        ["5. Guest Name", request.form.get("guest_name", "")],
        ["6. Phone", request.form.get("guest_phone", "")],
        ["7. Pax", request.form.get("pax", "")],
        ["8. Reference ID", request.form.get("reference_id", "")],
    ], colWidths=[150, 300])

    trip_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, GREY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold")
    ]))
    elements.append(trip_table)

    # ---------------- HOTELS ----------------
    elements.append(Paragraph("Hotels", heading_style))
    hotel_data = [["Hotel", "Check-In", "Check-Out", "Room Type"]]

    for h, ci, co, acc in zip(
        request.form.getlist("hotel_name[]"),
        request.form.getlist("check_in[]"),
        request.form.getlist("check_out[]"),
        request.form.getlist("accommodation[]")
    ):
        hotel_data.append([h, ci, co, acc])

    hotel_table = Table(hotel_data, colWidths=[160, 90, 90, 110])
    hotel_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, GREY),
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))
    elements.append(hotel_table)

    # ---------------- ACTIVITIES ----------------
    elements.append(Paragraph("Activities", heading_style))
    activity_data = [["Day", "Time", "Service", "Pax / Vehicle", "Remarks"]]

    for d, t, s, p, r in zip(
        request.form.getlist("day[]"),
        request.form.getlist("start_time[]"),
        request.form.getlist("service[]"),
        request.form.getlist("pax_or_vehicle[]"),
        request.form.getlist("remarks[]")
    ):
        activity_data.append([
            d,
            t,
            Paragraph(s, text_style),
            Paragraph(p, text_style),
            Paragraph(r, text_style)
        ])

    activity_table = Table(activity_data, colWidths=[40, 60, 160, 90, 100])
    activity_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, GREY),
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP")
    ]))
    elements.append(activity_table)

    # ---------------- INCLUSIONS ----------------
    elements.append(Paragraph("Inclusions", heading_style))
    elements.append(Table(
        [[f"✓ {i}"] for i in INCLUSIONS],
        colWidths=[450],
        style=[("GRID", (0, 0), (-1, -1), 0.5, GREY)]
    ))

    # ---------------- EXCLUSIONS ----------------
    elements.append(Paragraph("Exclusions", heading_style))
    elements.append(Table(
        [[f"• {e}"] for e in EXCLUSIONS],
        colWidths=[450],
        style=[("GRID", (0, 0), (-1, -1), 0.5, GREY)]
    ))

    # ---------------- TERMS & CONDITIONS ----------------
    elements.append(Paragraph("Terms & Conditions", heading_style))
    terms_table = Table(
        [[Paragraph(f"• {t}", text_style)] for t in TERMS],
        colWidths=[450]
    )
    terms_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, GREY),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(terms_table)

    # ---------------- ADDRESS ----------------
    elements.append(Spacer(1, 14))
    elements.append(Paragraph(ADDRESS, address_style))

    doc.build(
        elements,
        onFirstPage=draw_first_page_header,
        onLaterPages=draw_later_page_header
    )

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="TravelVoucher.pdf")

if __name__ == "__main__":
    app.run(debug=True)



