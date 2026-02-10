import os
from typing import Optional

class EmailConfig:
    """Email configuration for SMTP"""
    
    # SMTP Settings
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    # Sender credentials
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password")
    
    # Email templates
    PRESCRIPTION_EMAIL_SUBJECT = "New Prescription - {patient_name}"
    
    PRESCRIPTION_EMAIL_BODY = """
Dear {pharmacy_name},

A new prescription has been sent to your pharmacy.

**Patient Information:**
- Name: {patient_name}
- Patient ID: {patient_id}

**Prescription Details:**
- Medication: {medication_name}
- Dosage: {dosage}
- Frequency: {frequency}
- Prescribing Physician: {prescribing_physician}
- Prescription Date: {prescription_date}

**Instructions:**
Please prepare this prescription for pickup by the patient.

This prescription was sent electronically from the Abena IHR Telemedicine Platform.

Best regards,
Abena IHR System
    """
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if email is properly configured"""
        return (
            cls.SENDER_EMAIL != "your-email@gmail.com" and 
            cls.SENDER_PASSWORD != "your-app-password"
        )
    
    @classmethod
    def get_smtp_config(cls) -> dict:
        """Get SMTP configuration"""
        return {
            "server": cls.SMTP_SERVER,
            "port": cls.SMTP_PORT,
            "use_tls": cls.SMTP_USE_TLS,
            "username": cls.SENDER_EMAIL,
            "password": cls.SENDER_PASSWORD
        }
