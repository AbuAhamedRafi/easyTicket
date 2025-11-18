"""
PDF generation utilities for EasyTicket
Generates ticket PDFs with QR codes
"""

import io
import qrcode
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.conf import settings


def generate_qr_code_image(qr_data):
    """
    Generate QR code image from data

    Args:
        qr_data (str): Data to encode in QR code

    Returns:
        BytesIO: QR code image buffer
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save to BytesIO buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


def generate_ticket_pdf_page(ticket, canvas_obj, page_width, page_height):
    """
    Generate a single ticket on a PDF canvas page

    Args:
        ticket: Ticket model instance
        canvas_obj: ReportLab canvas object
        page_width: Width of the page
        page_height: Height of the page
    """
    # Define margins and positions
    margin = 0.5 * inch
    center_x = page_width / 2

    # Current Y position (start from top)
    y_pos = page_height - margin

    # ========== HEADER ==========
    canvas_obj.setFont("Helvetica-Bold", 24)
    canvas_obj.drawCentredString(center_x, y_pos, "EasyTicket")
    y_pos -= 0.5 * inch

    # Event title
    canvas_obj.setFont("Helvetica-Bold", 20)
    canvas_obj.drawCentredString(center_x, y_pos, str(ticket.event.title))
    y_pos -= 0.4 * inch

    # ========== TICKET INFO ==========
    canvas_obj.setFont("Helvetica", 12)

    # Ticket type
    canvas_obj.drawCentredString(center_x, y_pos, f"{ticket.full_ticket_name}")
    y_pos -= 0.3 * inch

    # Event date and venue
    event_date_str = ticket.event_date.strftime("%B %d, %Y at %I:%M %p")
    canvas_obj.drawCentredString(center_x, y_pos, event_date_str)
    y_pos -= 0.25 * inch

    canvas_obj.drawCentredString(
        center_x, y_pos, f"{ticket.event.venue_name}, {ticket.event.venue_city}"
    )
    y_pos -= 0.5 * inch

    # ========== QR CODE ==========
    # Generate QR code
    qr_buffer = generate_qr_code_image(ticket.qr_code_data)

    # Create Image object and draw centered
    qr_size = 3 * inch
    qr_x = center_x - (qr_size / 2)
    y_pos -= qr_size

    qr_image = Image(qr_buffer, width=qr_size, height=qr_size)
    qr_image.drawOn(canvas_obj, qr_x, y_pos)

    y_pos -= 0.5 * inch

    # ========== TICKET NUMBER ==========
    canvas_obj.setFont("Helvetica-Bold", 14)
    canvas_obj.drawCentredString(center_x, y_pos, f"Ticket: {ticket.ticket_number}")
    y_pos -= 0.3 * inch

    # ========== PRICE ==========
    canvas_obj.setFont("Helvetica", 12)
    canvas_obj.drawCentredString(center_x, y_pos, f"Price: ${ticket.price}")
    y_pos -= 0.5 * inch

    # ========== ATTENDEE INFO (if available) ==========
    if ticket.attendee_name:
        canvas_obj.setFont("Helvetica", 10)
        canvas_obj.drawCentredString(
            center_x, y_pos, f"Attendee: {ticket.attendee_name}"
        )
        y_pos -= 0.2 * inch

    # ========== FOOTER / TERMS ==========
    y_pos = margin + 0.5 * inch
    canvas_obj.setFont("Helvetica", 8)

    terms = [
        "Please present this ticket (digital or printed) at the event entrance.",
        "This ticket is valid for one entry only. QR code will be scanned upon entry.",
        "No refunds or exchanges. For support, contact support@easyticket.com",
    ]

    for term in terms:
        canvas_obj.drawCentredString(center_x, y_pos, term)
        y_pos -= 0.15 * inch


def group_tickets_by_type(order):
    """
    Group tickets by Event, Date, and Tier for smart PDF generation

    Args:
        order: Order model instance

    Returns:
        list: List of grouped tickets
        [
            {
                'event': Event object,
                'date': datetime,
                'tier_name': str,
                'day_name': str,
                'tickets': [Ticket objects],
                'filename': str
            },
            ...
        ]
    """
    from Tickets.models import Ticket
    from collections import defaultdict

    # Get all tickets for this order
    tickets = (
        Ticket.objects.filter(order_item__order=order)
        .select_related(
            "event",
            "ticket_type",
            "ticket_tier",
            "day_pass",
            "day_tier_price",
            "order_item",
        )
        .order_by("event_date", "ticket_name", "tier_name", "day_name")
    )

    # Group by (event_id, event_date, tier_name, day_name)
    groups_dict = defaultdict(list)

    for ticket in tickets:
        # Create unique key for grouping
        group_key = (
            str(ticket.event.id),
            ticket.event_date.date().isoformat(),
            ticket.tier_name or "",
            ticket.day_name or "",
        )
        groups_dict[group_key].append(ticket)

    # Convert to list of dicts with metadata
    groups = []
    for (event_id, date_str, tier_name, day_name), ticket_list in groups_dict.items():
        first_ticket = ticket_list[0]

        # Generate smart filename
        event_slug = (
            first_ticket.event.slug
            if hasattr(first_ticket.event, "slug")
            else first_ticket.event.title.replace(" ", "_")
        )
        date_part = datetime.fromisoformat(date_str).strftime("%b%d")

        filename_parts = [event_slug, date_part]
        if tier_name:
            filename_parts.append(tier_name.replace(" ", "_"))
        if day_name:
            filename_parts.append(day_name.replace(" ", "_"))

        filename = f"{'_'.join(filename_parts)}.pdf"

        groups.append(
            {
                "event": first_ticket.event,
                "date": first_ticket.event_date,
                "tier_name": tier_name,
                "day_name": day_name,
                "ticket_type": first_ticket.ticket_name,
                "tickets": ticket_list,
                "filename": filename,
                "quantity": len(ticket_list),
            }
        )

    return groups


def generate_grouped_ticket_pdf(ticket_group):
    """
    Generate a multi-page PDF for a group of tickets
    Each page = one ticket

    Args:
        ticket_group (dict): Dictionary with 'tickets' list and metadata

    Returns:
        BytesIO: PDF file buffer
    """
    buffer = io.BytesIO()

    # Create PDF with ReportLab
    pdf = canvas.Canvas(buffer, pagesize=letter)
    page_width, page_height = letter

    # Generate a page for each ticket in the group
    for ticket in ticket_group["tickets"]:
        generate_ticket_pdf_page(ticket, pdf, page_width, page_height)
        pdf.showPage()  # New page for next ticket

    # Finalize PDF
    pdf.save()
    buffer.seek(0)

    return buffer


def generate_order_ticket_pdfs(order):
    """
    Generate all ticket PDFs for an order
    Groups tickets intelligently and creates separate PDFs

    Args:
        order: Order model instance

    Returns:
        list: List of tuples (filename, pdf_buffer)
        [
            ('EventName_Nov05_VIP.pdf', BytesIO),
            ('EventName_Nov06_GA.pdf', BytesIO),
            ...
        ]
    """
    # Group tickets
    groups = group_tickets_by_type(order)

    # Generate PDF for each group
    pdf_attachments = []
    for group in groups:
        pdf_buffer = generate_grouped_ticket_pdf(group)
        pdf_attachments.append((group["filename"], pdf_buffer))

    return pdf_attachments


def generate_summary_table_html(ticket_groups):
    """
    Generate HTML summary table for email

    Args:
        ticket_groups: List of ticket groups from group_tickets_by_type()

    Returns:
        str: HTML table
    """
    table_html = """
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <thead>
            <tr style="background-color: #4CAF50; color: white;">
                <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Event</th>
                <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Date</th>
                <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Ticket Type</th>
                <th style="padding: 12px; text-align: center; border: 1px solid #ddd;">Quantity</th>
            </tr>
        </thead>
        <tbody>
    """

    total_tickets = 0
    for group in ticket_groups:
        date_str = group["date"].strftime("%a, %b %d")
        ticket_type = group["ticket_type"]
        if group["tier_name"]:
            ticket_type += f" - {group['tier_name']}"
        if group["day_name"]:
            ticket_type += f" - {group['day_name']}"

        table_html += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">{group['event'].title}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{date_str}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{ticket_type}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{group['quantity']}</td>
            </tr>
        """
        total_tickets += group["quantity"]

    table_html += f"""
        </tbody>
        <tfoot>
            <tr style="background-color: #f0f0f0; font-weight: bold;">
                <td colspan="3" style="padding: 12px; border: 1px solid #ddd; text-align: right;">Total Tickets:</td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">{total_tickets}</td>
            </tr>
        </tfoot>
    </table>
    """

    return table_html


def generate_pdf_attachment_list_html(ticket_groups):
    """
    Generate HTML list of PDF attachments for email

    Args:
        ticket_groups: List of ticket groups

    Returns:
        str: HTML list
    """
    html = "<ul style='list-style-type: none; padding: 0;'>"

    for group in ticket_groups:
        ticket_count = group["quantity"]
        ticket_word = "ticket" if ticket_count == 1 else "tickets"
        html += f"<li style='padding: 5px 0;'>📎 <strong>{group['filename']}</strong> (Contains {ticket_count} {ticket_word})</li>"

    html += "</ul>"

    return html
