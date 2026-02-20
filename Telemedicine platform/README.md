# Telemedicine Platform with Abena SDK Integration

A modern React-based telemedicine platform that provides a comprehensive solution for healthcare providers and patients to connect remotely, with full Abena SDK integration for secure, compliant healthcare operations.

## 🚀 Enhanced Features

### For Doctors (Providers)
- **Dashboard**: Overview of appointments, patient statistics, and recent activity
- **Patient Management**: View and manage patient information with Abena SDK security
- **Appointment Scheduling**: Schedule and manage patient appointments
- **Video Consultations**: Conduct secure video calls with patients
- **Prescription Management**: Create and send prescriptions to pharmacies via Abena SDK
- **Lab Request Management**: Send lab requests to laboratories via Abena SDK
- **Medical Records**: Access and update patient medical records with encryption
- **Lab Results**: View and manage laboratory test results
- **Document Management**: Upload and share documents with privacy controls
- **Messaging**: Communicate with patients through secure messaging
- **Settings**: Customize platform preferences

### For Patients
- **Dashboard**: Overview of upcoming appointments and health metrics
- **Appointment Booking**: Schedule appointments with healthcare providers
- **Video Consultations**: Join secure video calls with doctors
- **Prescriptions**: View and manage prescriptions received from providers
- **Lab Results**: View lab results and test reports
- **Medical Records**: View personal health records and history
- **Documents**: Access shared documents from healthcare providers
- **Messaging**: Communicate with healthcare providers
- **Vitals Tracking**: Monitor and track health vitals
- **Settings**: Manage account preferences

## 🔐 Abena SDK Integration

The platform now integrates with the Abena SDK to provide:

### **Security & Privacy**
- **Automatic Authentication**: Provider authentication handled by Abena SDK
- **Data Encryption**: All sensitive data automatically encrypted/decrypted
- **Privacy Controls**: Patient consent management and data access controls
- **Audit Logging**: Complete activity tracking and compliance reporting

### **Provider Workflow Integration**
- **Prescription Management**: Create and send prescriptions to pharmacies
- **Lab Request Management**: Send lab requests to laboratories
- **Document Sharing**: Secure document upload and sharing
- **Visit Summaries**: Create and send visit summaries to patients
- **Patient Data Access**: Secure access to patient records

### **Blockchain Integration**
- **Immutable Records**: All transactions recorded on blockchain
- **Audit Trail**: Complete history of all healthcare interactions
- **Data Integrity**: Tamper-proof medical records

## Technology Stack

- **Frontend**: React 18
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Build Tool**: Create React App
- **Healthcare SDK**: Abena SDK v1.0.0

## Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn
- Abena SDK access credentials

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd telemedicine-platform
```

2. Install dependencies:
```bash
npm install
```

3. Configure Abena SDK:
   - Update service URLs in `src/services/AbenaIntegration.js`
   - Add your Abena SDK credentials
   - Configure blockchain endpoints

4. Start the development server:
```bash
npm start
```

5. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## Project Structure

```
telemedicine-platform/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   └── ui/
│   │       └── card.jsx
│   ├── services/
│   │   └── AbenaIntegration.js
│   ├── App.js
│   ├── index.js
│   └── index.css
├── package.json
├── tailwind.config.js
├── postcss.config.js
└── README.md
```

## Abena SDK Services

### **Authentication Service** (`http://localhost:3001`)
- Provider authentication
- Permission management
- Session handling

### **Data Service** (`http://localhost:8001`)
- Patient data management
- Medical records
- Prescription and lab request data

### **Privacy Service** (`http://localhost:8002`)
- Data encryption/decryption
- Consent management
- Privacy controls

### **Blockchain Service** (`http://localhost:8003`)
- Transaction recording
- Audit trail management
- Data integrity verification

## Key Components

### AbenaIntegration Service
The core integration service that handles all Abena SDK interactions:

```javascript
import abenaIntegration from './services/AbenaIntegration';

// Create prescription
const prescription = await abenaIntegration.createPrescription(
  patientId, 
  prescriptionData, 
  providerId
);

// Send to pharmacy
await abenaIntegration.sendPrescriptionToPharmacy(
  prescription.id, 
  pharmacyId
);
```

### Enhanced Provider Workflow
- **Automatic Authentication**: Providers are automatically authenticated via Abena SDK
- **Secure Data Access**: All patient data access is handled through Abena SDK
- **Audit Logging**: All actions are automatically logged for compliance
- **Privacy Controls**: Patient consent and data access are managed automatically

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm test` - Launches the test runner
- `npm run build` - Builds the app for production
- `npm run eject` - Ejects from Create React App (one-way operation)

## Abena SDK Features

### **Provider Authentication**
```javascript
const authResult = await abenaIntegration.authenticateProvider({
  username: 'dr.smith',
  password: 'secure_password'
});
```

### **Prescription Management**
```javascript
// Create prescription
const prescription = await abenaIntegration.createPrescription(
  patientId, 
  prescriptionData, 
  providerId
);

// Send to pharmacy
await abenaIntegration.sendPrescriptionToPharmacy(
  prescription.id, 
  pharmacyId
);
```

### **Lab Request Management**
```javascript
// Create lab request
const labRequest = await abenaIntegration.createLabRequest(
  patientId, 
  labRequestData, 
  providerId
);

// Send to laboratory
await abenaIntegration.sendLabRequestToLaboratory(
  labRequest.id, 
  laboratoryId
);
```

### **Document Management**
```javascript
// Upload document
const document = await abenaIntegration.uploadDocument(
  patientId, 
  documentData, 
  documentType
);

// Share document
await abenaIntegration.shareDocument(
  document.id, 
  recipientId, 
  purpose
);
```

### **Visit Summary Management**
```javascript
// Create visit summary
const summary = await abenaIntegration.createVisitSummary(
  patientId, 
  summaryData, 
  providerId
);

// Send to patient
await abenaIntegration.sendVisitSummaryToPatient(
  summary.id, 
  patientId
);
```

## Security & Compliance

### **Data Protection**
- All sensitive data is automatically encrypted
- Patient consent is managed through Abena SDK
- Access controls are enforced at the SDK level

### **Audit Trail**
- All actions are logged automatically
- Blockchain recording for immutable audit trail
- Compliance reporting capabilities

### **Privacy Controls**
- Patient consent management
- Data access controls
- Privacy service integration

## Customization

### Switching User Types
To switch between doctor and patient views, modify the `userType` state in `App.js`:

```javascript
const [userType, setUserType] = useState('doctor'); // or 'patient'
```

### Adding New Abena SDK Features
1. Add new methods to `AbenaIntegration.js`
2. Update the UI components to use the new SDK methods
3. Ensure proper error handling and logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with Abena SDK
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.

## Abena SDK Documentation

For detailed information about the Abena SDK, please refer to the official documentation at [Abena SDK Docs](https://docs.abena.com). 