"""
Email utility functions for the application
Handles all email sending functionality including verification, password reset, etc.
"""

from django.core.mail import send_mail, EmailMessage
from django.conf import settings


def send_verification_email(user_email, verification_token):
    """
    Send email verification link to user

    Args:
        user_email (str): User's email address
        verification_token (str): Verification token generated for the user

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = "Verify Your Email - EasyTicket"

    # Create verification link
    verification_link = (
        f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
    )

    # HTML email content
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: white;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                margin: 20px 0;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
            .token {{
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                word-break: break-all;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to EasyTicket!</h1>
            </div>
            <div class="content">
                <h2>Email Verification</h2>
                <p>Thank you for registering with EasyTicket. Please verify your email address to activate your account.</p>
                
                <p>Click the button below to verify your email:</p>
                <div style="text-align: center;">
                    <a href="{verification_link}" class="button">Verify Email Address</a>
                </div>
                
                <p>Or copy and paste this link in your browser:</p>
                <div class="token">{verification_link}</div>
                
                <p><strong>Verification Token:</strong></p>
                <div class="token">{verification_token}</div>
                
                <p><strong>Note:</strong> This verification link will expire in 24 hours.</p>
                
                <p>If you didn't create an account with EasyTicket, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 EasyTicket. All rights reserved.</p>
                <p>This is an automated email, please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Plain text version (fallback)
    plain_message = f"""
    Welcome to EasyTicket!
    
    Thank you for registering. Please verify your email address to activate your account.
    
    Verification Link: {verification_link}
    
    Verification Token: {verification_token}
    
    This verification link will expire in 24 hours.
    
    If you didn't create an account with EasyTicket, please ignore this email.
    
    ---
    © 2025 EasyTicket. All rights reserved.
    This is an automated email, please do not reply.
    """

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending verification email to {user_email}: {e}")
        return False


def send_password_reset_email(user_email, reset_token):
    """
    Send password reset link to user

    Args:
        user_email (str): User's email address
        reset_token (str): Password reset token

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = "Reset Your Password - EasyTicket"

    # Create reset link
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    # HTML email content
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #FF6B6B;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: white;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                margin: 20px 0;
                background-color: #FF6B6B;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <h2>Reset Your Password</h2>
                <p>We received a request to reset your password for your EasyTicket account.</p>
                
                <p>Click the button below to reset your password:</p>
                <div style="text-align: center;">
                    <a href="{reset_link}" class="button">Reset Password</a>
                </div>
                
                <p>Or copy and paste this link in your browser:</p>
                <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; word-break: break-all;">
                    {reset_link}
                </div>
                
                <p><strong>Note:</strong> This reset link will expire in 1 hour.</p>
                
                <p>If you didn't request a password reset, please ignore this email or contact support if you have concerns.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 EasyTicket. All rights reserved.</p>
                <p>This is an automated email, please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Plain text version
    plain_message = f"""
    Password Reset Request - EasyTicket
    
    We received a request to reset your password.
    
    Reset Link: {reset_link}
    
    This reset link will expire in 1 hour.
    
    If you didn't request a password reset, please ignore this email.
    
    ---
    © 2025 EasyTicket. All rights reserved.
    """

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending password reset email to {user_email}: {e}")
        return False


def send_welcome_email(user_email, user_name):
    """
    Send welcome email after successful email verification

    Args:
        user_email (str): User's email address
        user_name (str): User's name

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = "Welcome to EasyTicket!"

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: white;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to EasyTicket!</h1>
            </div>
            <div class="content">
                <h2>Hi {user_name}!</h2>
                <p>Your email has been successfully verified. You can now access all features of EasyTicket.</p>
                
                <p><strong>What you can do now:</strong></p>
                <ul>
                    <li>Browse and search for events</li>
                    <li>Purchase tickets for your favorite events</li>
                    <li>Manage your bookings</li>
                    <li>Update your profile</li>
                </ul>
                
                <p>If you have any questions or need assistance, feel free to contact our support team.</p>
                
                <p>Happy ticketing!</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 EasyTicket. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    plain_message = f"""
    Welcome to EasyTicket!
    
    Hi {user_name}!
    
    Your email has been successfully verified. You can now access all features of EasyTicket.
    
    What you can do now:
    - Browse and search for events
    - Purchase tickets for your favorite events
    - Manage your bookings
    - Update your profile
    
    If you have any questions, feel free to contact our support team.
    
    Happy ticketing!
    
    ---
    © 2025 EasyTicket. All rights reserved.
    """

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email to {user_email}: {e}")
        return False


def send_order_confirmation_email(order):
    """
    Send order confirmation email with ticket PDF attachments

    Enhanced version that:
    - Groups tickets smartly (by event, date, tier)
    - Generates separate PDFs for each group
    - Attaches all PDFs to one email
    - Includes summary table

    Args:
        order: Order instance

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    from Common.pdf_utils import (
        generate_order_ticket_pdfs,
        group_tickets_by_type,
        generate_summary_table_html,
        generate_pdf_attachment_list_html,
    )

    subject = f"✓ Your Tickets for {order.event.title}! (Order #{order.order_number})"

    try:
        # Generate ticket PDFs
        ticket_groups = group_tickets_by_type(order)
        pdf_attachments = generate_order_ticket_pdfs(order)

        # Generate summary table HTML
        summary_table = generate_summary_table_html(ticket_groups)

        # Generate PDF attachment list HTML
        pdf_list = generate_pdf_attachment_list_html(ticket_groups)

        # Total ticket count
        total_tickets = sum(group["quantity"] for group in ticket_groups)

        # HTML email template
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 700px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border: 1px solid #ddd;
                    border-top: none;
                }}
                .order-summary {{
                    background-color: white;
                    padding: 25px;
                    margin: 25px 0;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                }}
                .section-title {{
                    color: #4CAF50;
                    font-size: 20px;
                    margin-top: 25px;
                    margin-bottom: 15px;
                    border-bottom: 2px solid #4CAF50;
                    padding-bottom: 8px;
                }}
                .info-box {{
                    background-color: #e8f5e9;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 15px 0;
                    border-left: 4px solid #4CAF50;
                }}
                .ticket-section {{
                    background-color: white;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                }}
                .footer {{
                    text-align: center;
                    padding: 25px;
                    color: #666;
                    font-size: 0.9em;
                    background-color: #f0f0f0;
                    border-radius: 0 0 8px 8px;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 35px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎉 Order Confirmed!</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">Thank you for your purchase, {order.buyer_name or 'valued customer'}!</p>
            </div>

            <div class="content">
                <p style="font-size: 16px;">Your order has been confirmed and your tickets are attached to this email.</p>

                <div class="order-summary">
                    <h3 style="margin-top: 0; color: #333;">Order Summary</h3>
                    <p><strong>Order Number:</strong> {order.order_number}</p>
                    <p><strong>Event:</strong> {order.event.title}</p>
                    <p><strong>Date:</strong> {order.event.start_date.strftime('%A, %B %d, %Y at %I:%M %p')}</p>
                    <p><strong>Venue:</strong> {order.event.venue_name}, {order.event.venue_city}</p>
                    <p style="margin-bottom: 0;"><strong>Total Tickets:</strong> {total_tickets}</p>
                </div>

                <h3 class="section-title">📋 Ticket Breakdown</h3>
                {summary_table}

                <div style="margin: 20px 0; padding: 15px; background-color: white; border-radius: 5px; border: 1px solid #e0e0e0;">
                    <p style="margin: 0 0 10px 0;"><strong>Subtotal:</strong> ${order.subtotal}</p>
                    <p style="margin: 0 0 10px 0;"><strong>Service Fee:</strong> ${order.service_fee}</p>
                    {f'<p style="margin: 0 0 10px 0;"><strong>Discount:</strong> -${order.discount_amount}</p>' if order.discount_amount > 0 else ''}
                    <p style="margin: 15px 0 0 0; padding-top: 15px; border-top: 2px solid #4CAF50; font-size: 18px; font-weight: bold; color: #4CAF50;">
                        Total Paid: ${order.total_amount}
                    </p>
                </div>

                <h3 class="section-title">🎫 Your Tickets</h3>
                <div class="info-box">
                    <p style="margin: 0 0 10px 0;"><strong>Your tickets are attached to this email as PDF files.</strong></p>
                    <p style="margin: 0;">Please present the QR code on each ticket for scanning at the event entrance.</p>
                </div>

                <div class="ticket-section">
                    <h4 style="margin-top: 0;">Attached PDF Files:</h4>
                    {pdf_list}
                    <p style="margin-top: 20px; font-size: 13px; color: #666;">
                        💡 <strong>Tip:</strong> You can print these tickets or show them on your mobile device at the event.
                        Each ticket has a unique QR code that will be scanned once upon entry.
                    </p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/orders/{order.id}" class="button">View Order Details</a>
                </div>

                <div class="info-box">
                    <p style="margin: 0;"><strong>Important Reminders:</strong></p>
                    <ul style="margin: 10px 0 0 0; padding-left: 20px;">
                        <li>Bring a valid ID to the event</li>
                        <li>Arrive early to avoid queues</li>
                        <li>Each ticket is valid for one entry only</li>
                        <li>Screenshots of QR codes are accepted</li>
                    </ul>
                </div>

                <p style="margin-top: 25px; font-size: 14px; color: #666;">
                    <strong>Payment Confirmation:</strong><br>
                    Payment Method: {order.payment_method.title()}<br>
                    Transaction ID: {order.payment_id}<br>
                    Paid At: {order.paid_at.strftime('%B %d, %Y at %I:%M %p') if order.paid_at else 'N/A'}
                </p>
            </div>

            <div class="footer">
                <p style="margin: 0 0 10px 0;">Have questions? We're here to help!</p>
                <p style="margin: 0 0 15px 0;">📧 Email: support@easyticket.com | 📞 Phone: 1-800-EASYTICKET</p>
                <p style="margin: 0; font-size: 12px;">&copy; 2025 EasyTicket. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

        # Plain text fallback
        plain_message = f"""
🎉 Order Confirmed! (Order #{order.order_number})

Hi {order.buyer_name or 'valued customer'},

Thank you for your purchase! Your tickets for {order.event.title} are attached to this email.

ORDER SUMMARY
=============
Order Number: {order.order_number}
Event: {order.event.title}
Date: {order.event.start_date.strftime('%A, %B %d, %Y at %I:%M %p')}
Venue: {order.event.venue_name}, {order.event.venue_city}

TICKET BREAKDOWN
================
"""
        for group in ticket_groups:
            date_str = group["date"].strftime("%a, %b %d")
            ticket_type = group["ticket_type"]
            if group["tier_name"]:
                ticket_type += f" - {group['tier_name']}"
            if group["day_name"]:
                ticket_type += f" - {group['day_name']}"
            plain_message += (
                f"{ticket_type} ({date_str}): {group['quantity']} ticket(s)\n"
            )

        plain_message += f"""
TOTAL TICKETS: {total_tickets}

PAYMENT DETAILS
===============
Subtotal: ${order.subtotal}
Service Fee: ${order.service_fee}
"""
        if order.discount_amount > 0:
            plain_message += f"Discount: -${order.discount_amount}\n"

        plain_message += f"""Total Paid: ${order.total_amount}

Payment Method: {order.payment_method.title()}
Transaction ID: {order.payment_id}

YOUR TICKETS
============
Your tickets are attached as PDF files. Each PDF is named for easy identification:
"""
        for group in ticket_groups:
            plain_message += (
                f"- {group['filename']} (Contains {group['quantity']} ticket(s))\n"
            )

        plain_message += f"""
IMPORTANT REMINDERS
===================
- Present the QR code on each ticket at the event entrance
- Bring a valid ID
- Each ticket is valid for one entry only
- Arrive early to avoid queues

View your order online: {settings.FRONTEND_URL}/orders/{order.id}

Questions? Contact us:
Email: support@easyticket.com
Phone: 1-800-EASYTICKET

© 2025 EasyTicket. All rights reserved.
        """

        # Create email with attachments
        email = EmailMessage(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.buyer_email],
        )

        # Set HTML content
        email.content_subtype = "html"
        email.body = html_message

        # Attach all PDF files
        for filename, pdf_buffer in pdf_attachments:
            email.attach(filename, pdf_buffer.read(), "application/pdf")

        # Send email
        email.send(fail_silently=False)

        return True

    except Exception as e:
        print(f"Error sending order confirmation email to {order.buyer_email}: {e}")
        import traceback

        traceback.print_exc()
        return False


def send_order_cancelled_email(order):
    """
    Send order cancellation/refund email with inline HTML template

    Args:
        order: Order instance

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = f"Order Cancelled: {order.order_number}"

    # HTML email template
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #f44336;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f9f9f9;
                padding: 30px;
                border: 1px solid #ddd;
            }}
            .order-details {{
                background-color: white;
                padding: 20px;
                margin: 20px 0;
                border-radius: 5px;
                border: 1px solid #e0e0e0;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Order Cancelled</h1>
        </div>

        <div class="content">
            <h2>Your order has been cancelled</h2>

            <div class="order-details">
                <p><strong>Order Number:</strong> {order.order_number}</p>
                <p><strong>Event:</strong> {order.event.title}</p>
                <p><strong>Amount:</strong> ${order.total_amount}</p>
                {f'<p><strong>Reason:</strong> {order.cancellation_reason}</p>' if order.cancellation_reason else ''}
            </div>

            {f'<p>A refund has been initiated and will be processed within 5-10 business days.</p>' if order.status == 'refunded' else ''}

            <p>If you have any questions, please contact our support team.</p>
        </div>

        <div class="footer">
            <p>Contact us at support@easyticket.com</p>
            <p>&copy; 2025 EasyTicket. All rights reserved.</p>
        </div>
    </body>
    </html>
    """

    # Plain text fallback
    plain_message = f"""
Order Cancelled

Your order has been cancelled.

Order Number: {order.order_number}
Event: {order.event.title}
Amount: ${order.total_amount}
{f'Reason: {order.cancellation_reason}' if order.cancellation_reason else ''}

{f'A refund has been initiated and will be processed within 5-10 business days.' if order.status == 'refunded' else ''}

If you have any questions, contact us at support@easyticket.com

© 2025 EasyTicket. All rights reserved.
    """

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.buyer_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order cancellation email to {order.buyer_email}: {e}")
        return False
