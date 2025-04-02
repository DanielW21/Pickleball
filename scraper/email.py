import smtplib
from email.message import EmailMessage

class EmailNotifier:
    def __init__(self, sender, password, recipient, smtp_server="smtp.gmail.com", smtp_port=587):
        self.sender = sender
        self.password = password
        self.recipient = recipient
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_notification(self, available_events):
        """Send email notification about available events"""
        if not available_events:
            return False

        msg = EmailMessage()
        msg['Subject'] = f"🎉 {len(available_events)} Events Available!"
        msg['From'] = self.sender
        msg['To'] = self.recipient
        
        email_body = self._generate_email_body(available_events)
        msg.set_content(email_body, subtype='html')
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

    def _generate_email_body(self, events):
        """Generate HTML email content"""
        email_body = ["<h2>Available Events:</h2><ul>"]
        
        for event in events:
            email_body.append(
                f"""<li>
                <strong>{event['name']}</strong><br>
                📅 {event['date']} ⏰ {event['time']}<br>
                🏟️ {event['location']}<br>
                🟢 {event['spots_left']}<br>
                <a href="{event['booking_link']}">Book Now</a>
                </li>"""
            )
        
        email_body.append("</ul>")
        return "\n".join(email_body)