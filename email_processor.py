import imaplib
import email
from email.header import decode_header
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

from google import genai

class EmailProcessor:
    def __init__(self, email_address, email_password, imap_server, smtp_server, api_key, smtp_port=587):
        """
        Initialize email processor with IMAP/SMTP (works with any email provider)
        
        For Gmail: 
        - imap_server='imap.gmail.com'
        - smtp_server='smtp.gmail.com'
        - Use App Password, not regular password
        
        For Outlook/Hotmail:
        - imap_server='outlook.office365.com'
        - smtp_server='smtp.office365.com'
        """
        self.email_address = email_address
        self.email_password = email_password
        self.imap_server = imap_server
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.0-flash"
        self.processed_ids = set()

    def connect_imap(self):
        # Connect to email via IMAP
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_address, self.email_password)
            return mail
        except Exception as e:
            print(f"Error connecting to IMAP: {e}")
            return None
        
    def get_unread_emails(self):
        # Fetch unread emails
        mail = self.connect_imap()
        if not mail:
            return []
        
        try:
            mail.select('inbox')
            _, messages = mail.search(None, 'UNSEEN')
            
            email_ids = messages[0].split()
            emails = []
            
            for email_id in email_ids:
                if email_id in self.processed_ids:
                    continue
                    
                _, msg_data = mail.fetch(email_id, '(RFC822)')
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Decode subject
                        subject = decode_header(msg['subject'])[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode()
                        
                        # Get sender
                        sender = msg.get('from')
                        
                        # Get body
                        body = self.get_email_body(msg)
                        
                        emails.append({
                            'id': email_id.decode(),
                            'subject': subject,
                            'sender': sender,
                            'body': body,
                            'msg': msg
                        })
                
                self.processed_ids.add(email_id)
            
            mail.close()
            mail.logout()
            return emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
        
    def get_email_body(self, msg):
        # Extract email body
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode()
            except:
                body = str(msg.get_payload())
        
        return body
    
    def categorize_email(self, email_data):
        # LLM for email categorization
        prompt = f"""Analyze this email and categorize it into ONE of these categories:
- URGENT: Requires immediate attention
- CUSTOMER_INQUIRY: Customer question or support request
- SALES: Sales inquiry or business opportunity
- NEWSLETTER: Marketing or informational content
- SPAM: Unwanted or suspicious content
- PERSONAL: Personal communication
- OTHER: Doesn't fit other categories

Email Subject: {email_data['subject']}
Email Sender: {email_data['sender']}
Email Body: {email_data['body'][:500]}

Respond with ONLY the category name on the first line, then a brief reason on the second line.
Example:
CUSTOMER_INQUIRY
Customer asking about product shipping times"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            result = response.text.strip()
            
            lines = result.split('\n', 1)
            category = lines[0].strip()
            reason = lines[1].strip() if len(lines) > 1 else "No reason provided"
            
            return category, reason
        except Exception as e:
            print(f"Error categorizing: {e}")
            return "OTHER", "Error in categorization"
    
    def draft_response(self, email_data, category):
        # LLM for draft response
        prompt = f"""Draft a professional email response based on this information:

Category: {category}
Original Email Subject: {email_data['subject']}
Original Email From: {email_data['sender']}
Original Email Body: {email_data['body'][:1000]}

Requirements:
- Be professional and helpful
- Address the main points in the email
- Keep it concise (2-3 paragraphs max)
- Start with a greeting
- End with a professional closing

Draft the complete email:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error drafting response: {e}")
            return "Thank you for your email. We'll get back to you shortly."
        
    def save_draft_locally(self, email_data, response):
        """Save draft to local file (since we can't create server drafts easily via IMAP)"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"draft_{timestamp}_{email_data['id']}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"TO: {email_data['sender']}\n")
                f.write(f"SUBJECT: Re: {email_data['subject']}\n")
                f.write(f"CATEGORY: {email_data.get('category', 'N/A')}\n")
                f.write(f"\n{'-'*60}\n\n")
                f.write(response)
            
            print(f"✓ Draft saved to: {filename}")
            return filename
        except Exception as e:
            print(f"Error saving draft: {e}")
            return None
        
    def send_email(self, to_address, subject, body):
        """Send email via SMTP (use this if you want to auto-send)"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_address
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)
            server.quit()
            
            print("✓ Email sent successfully")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
        
    def mark_as_read(self, email_id):
        """Mark email as read"""
        mail = self.connect_imap()
        if not mail:
            return False
        
        try:
            mail.select('inbox')
            mail.store(email_id.encode(), '+FLAGS', '\\Seen')
            mail.close()
            mail.logout()
            return True
        except Exception as e:
            print(f"Error marking as read: {e}")
            return False

    def process_emails(self):
        """Main processing loop"""
        print(f"\n{'='*60}")
        print(f"Processing emails at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        emails = self.get_unread_emails()
        
        if not emails:
            print("No new unread emails found.")
            return
        
        print(f"Found {len(emails)} new unread email(s)\n")
        
        for email_data in emails:
            print(f"Processing: {email_data['subject']}")
            print(f"From: {email_data['sender']}")
            
            # Categorize
            category, reason = self.categorize_email(email_data)
            email_data['category'] = category
            print(f"Category: {category}")
            print(f"Reason: {reason}")
            
            # Draft response
            response = self.draft_response(email_data, category)
            print(f"Response drafted (preview): {response[:100]}...")
            
            # Save draft locally
            draft_file = self.save_draft_locally(email_data, response)
            
            # Optional: Auto-send for certain categories
            # if category in ['NEWSLETTER', 'SPAM']:
            #     self.send_email(email_data['sender'], f"Re: {email_data['subject']}", response)
            
            # Mark as read
            self.mark_as_read(email_data['id'])
            print("✓ Email marked as read")
            
            print(f"{'-'*60}\n")

    def run_continuous(self, interval_seconds=300):
        """Run continuously, checking emails at specified interval"""
        print(f"Starting email processor...")
        print(f"Checking every {interval_seconds} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.process_emails()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nEmail processor stopped.")