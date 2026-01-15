from email_processor import EmailProcessor
from config import (
    EMAIL_ADDRESS, 
    EMAIL_PASSWORD, 
    IMAP_SERVER, 
    SMTP_SERVER, 
    GEMINI_API_KEY,
    CHECK_INTERVAL
)

def main():
    """Main function to run the email processor"""
    
    print("="*60)
    print("EMAIL PROCESSOR STARTING")
    print("="*60)
    print(f"Email: {EMAIL_ADDRESS}")
    print(f"IMAP Server: {IMAP_SERVER}")
    print(f"SMTP Server: {SMTP_SERVER}")
    print("="*60)
    
    # Initialize the email processor
    processor = EmailProcessor(
        email_address=EMAIL_ADDRESS,
        email_password=EMAIL_PASSWORD,
        imap_server=IMAP_SERVER,
        smtp_server=SMTP_SERVER,
        api_key=GEMINI_API_KEY
    )
    
    # Choose your mode:
    
    # MODE 1: Process emails once and exit
    print("\nMode: Process once\n")
    processor.process_emails()
    
    # MODE 2: Run continuously (uncomment to use)
    # print(f"\nMode: Continuous (checking every {CHECK_INTERVAL} seconds)\n")
    # processor.run_continuous(interval_seconds=CHECK_INTERVAL)

if __name__ == "__main__":
    main()