# Email Configuration for Prescription Sending

## Overview
The Abena IHR system now supports sending prescriptions to pharmacies via email using SMTP.

## Current Status
- ✅ **Backend API**: Working and tested
- ✅ **Frontend Interface**: Working with contact input modal
- ✅ **Email Templates**: Configured with professional formatting
- 🔄 **SMTP Configuration**: Ready for real email sending

## How It Works

### Frontend Flow
1. User clicks "Send to Pharmacy" on a prescription
2. Modal opens asking for pharmacy contact information
3. User selects Email/Phone and enters contact details
4. System sends prescription to pharmacy

### Backend Flow
1. Updates prescription status to "sent_to_pharmacy"
2. Creates professional email with prescription details
3. Sends email via SMTP (or logs in mock mode)
4. Returns success response

## Email Template
The system sends a professional email containing:
- Patient information
- Prescription details (medication, dosage, frequency)
- Prescribing physician
- Instructions for pharmacy

## Configuration

### For Real Email Sending (Production)

Set these environment variables in your Docker container:

```bash
# Gmail SMTP (recommended for testing)
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true

# Or for other SMTP providers
SENDER_EMAIL=your-email@yourdomain.com
SENDER_PASSWORD=your-password
SMTP_SERVER=smtp.yourdomain.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

### Gmail App Password Setup
1. Enable 2-factor authentication on your Gmail account
2. Generate an "App Password" for this application
3. Use the app password instead of your regular password

### Docker Environment Variables
Add to your `docker-compose.simple.yml`:

```yaml
services:
  abena-ihr:
    environment:
      - SENDER_EMAIL=your-email@gmail.com
      - SENDER_PASSWORD=your-app-password
      - SMTP_SERVER=smtp.gmail.com
      - SMTP_PORT=587
      - SMTP_USE_TLS=true
```

## Testing

### Current Mode: Mock Email
- System logs email content instead of sending
- Perfect for development and testing
- No email credentials required

### Real Email Mode
- Set environment variables as above
- System will send actual emails
- Check logs for delivery confirmation

## API Endpoint
```
POST /api/v1/prescriptions/{prescription_id}/send
Content-Type: application/json

{
  "pharmacyName": "Pharmacy Name",
  "pharmacyContact": "pharmacy@example.com",
  "contactType": "email"
}
```

## Security Notes
- Never commit email credentials to version control
- Use environment variables for sensitive data
- Consider using a dedicated email service for production
- Implement rate limiting for email sending

## Future Enhancements
- SMS integration for phone contacts
- Email delivery tracking
- Pharmacy response handling
- Bulk prescription sending
- Email templates customization
