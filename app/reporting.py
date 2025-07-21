import os
import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import AnalysisResult
from app.learning_agent import LearningAgent

load_dotenv()

def generate_weekly_report():
    """
    Generates a summary of the week's activities.
    """
    db = SessionLocal()
    agent = LearningAgent()

    # Get analyses from the last 7 days
    one_week_ago = datetime.now() - timedelta(days=7)
    recent_analyses = db.query(AnalysisResult).filter(AnalysisResult.analysis_date >= one_week_ago).all()

    report_content = "<h2>خلاصه فعالیت‌های هفته گذشته</h2>"

    if recent_analyses:
        report_content += f"<p>در هفته گذشته، <strong>{len(recent_analyses)}</strong> تحلیل جدید از رقبا ثبت شده است.</p>"
        report_content += "<h3>آخرین تحلیل‌ها:</h3><ul>"
        for analysis in recent_analyses[:3]: # Show top 3
            report_content += f"<li><strong>{analysis.competitor.url}:</strong> {analysis.description[:100]}...</li>"
        report_content += "</ul>"

        # Get some high-level advice
        advice = agent.get_advice(recent_analyses)
        report_content += "<h3>💡 یک مشورت دوستانه از چی‌چی:</h3>"
        report_content += f"<p>{advice.replace('\n', '<br>')}</p>"
    else:
        report_content += "<p>در هفته گذشته هیچ تحلیل جدیدی ثبت نشده. بهتره یه نگاهی به رقبا بندازیم!</p>"

    db.close()
    return report_content

def send_email(subject, html_content):
    """
    Sends an email using SMTP credentials from .env file.
    """
    sender_email = os.getenv("SMTP_EMAIL")
    receiver_email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("SMTP_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT", 587)

    if not all([sender_email, receiver_email, password, smtp_server]):
        print("SMTP credentials are not fully set in the .env file. Cannot send email.")
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Attach the HTML content
    message.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"Weekly report sent successfully to {receiver_email}!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def job():
    print("Generating and sending weekly report...")
    report = generate_weekly_report()
    send_email("گزارش هفتگی دستیار هوشمند شما", report)

def start_scheduler():
    """
    Starts the scheduler to run the job weekly.
    """
    # Schedule the job to run every Sunday at 9 AM
    schedule.every().sunday.at("09:00").do(job)

    print("Scheduler started. Weekly reports will be sent every Sunday at 9 AM.")

    # Run the scheduler in a loop
    while True:
        schedule.run_pending()
        time.sleep(60) # Check every minute

if __name__ == "__main__":
    # For testing the email sending directly
    job()
