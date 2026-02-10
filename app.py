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
LOGO_PATH = "static/Untitles-1.png"
DUBAI_LOGO_PATH = "static/dubai_no_bg.png"

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
    "Tel: +97 155 4739783 | Fax: 04-5752879 | "
    "Email: info@triplegend.com<br/>www.triplegend.com"
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

    # LEFT LOGO (Dubai logo above text)
    if os.path.exists(DUBAI_LOGO_PATH):
        canvas.drawImage(
            DUBAI_LOGO_PATH,
            30,
            h - 90,
            60,
            50,
            preserveAspectRatio=True,
            mask="auto"
        )

    # LEFT TEXT (Welcome to Dubai under logo)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(DARK_BLUE)
    canvas.drawString(30, h - 105, "Welcome to Dubai")

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
    padding=8
)

text_style = ParagraphStyle(
    "text",
    fontSize=9,
    leading=13,
    alignment=TA_LEFT,
    wordWrap="CJK"
)

normal_style = styles["Normal"]

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
        ["1. Guest Name", request.form.get("guest_name", ""),
         "2. Trip ID", request.form.get("trip_id", "")],

        ["3. Arrival Date", request.form.get("arrival_date", ""),
         "4. Departure", request.form.get("departure", "")],

        ["5. Pax", request.form.get("pax", ""),
         "6. Duration", request.form.get("duration", "")],

        ["7. Phone", request.form.get("guest_phone", ""),
         "8. Reference ID", request.form.get("reference_id", "")],
    ], colWidths=[130, 170, 130, 170])

    trip_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, GREY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(trip_table)

    # ---------------- HOTELS ----------------
    elements.append(Paragraph("Hotels", heading_style))

    hotel_data = []

    for i, (h, ci, co, acc) in enumerate(zip(
        request.form.getlist("hotel_name[]"),
        request.form.getlist("check_in[]"),
        request.form.getlist("check_out[]"),
        request.form.getlist("accommodation[]")
    ), start=1):
        hotel_data.extend([
            [f"Hotel {i}", Paragraph(h, normal_style)],
            ["Check-In", ci],
            ["Check-Out", co],
            ["Accommodation", Paragraph(acc, normal_style)],
            ["", ""],  # spacing row
        ])

    hotel_table = Table(hotel_data, colWidths=[150, 250])
    hotel_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, GREY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
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

    # ---------------- INCLUSIONS & EXCLUSIONS ----------------
    # Get dynamic points from the form (all user-added inputs)
    inclusions_list = [i.strip() for i in request.form.getlist("inclusions[]") if i.strip()]
    exclusions_list = [e.strip() for e in request.form.getlist("exclusions[]") if e.strip()]

    # Determine max number of rows needed
    max_rows = max(len(inclusions_list), len(exclusions_list))

    # Fill shorter list with empty strings so both columns align
    while len(inclusions_list) < max_rows:
        inclusions_list.append("")
    while len(exclusions_list) < max_rows:
        exclusions_list.append("")

    # Build table data row by row
    two_column_data = []
    for i in range(max_rows):
        two_column_data.append([
            f"✓ {inclusions_list[i]}" if inclusions_list[i] else "",
            f"• {exclusions_list[i]}" if exclusions_list[i] else ""
        ])

    # Add heading before table
    elements.append(Paragraph("Inclusions & Exclusions", heading_style))

    # Create PDF table side by side
    two_column_table = Table(two_column_data, colWidths=[225, 225])
    two_column_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, GREY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    elements.append(two_column_table)

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

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

