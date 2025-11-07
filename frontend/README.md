# Tata Capital Digital Loan Sales Assistant - React Frontend

This is the React frontend for the Tata Capital Digital Loan Sales Assistant with authentication system.

## Features

- **User Authentication**: Secure login and registration system
- **Loan Assistant Chat**: Interactive chat interface for loan processing
- **Document Upload**: Secure document upload functionality
- **Loan Status Tracking**: Real-time loan application status
- **Sanction Letter Generation**: Automated sanction letter processing
- **Responsive Design**: Mobile-friendly interface

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Backend API running on http://localhost:8000

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the frontend directory:
```env
REACT_APP_API_URL=http://localhost:8000/api
```

4. Start the development server:
```bash
npm start
```

The application will open in your browser at `http://localhost:3000`.

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/       # Reusable UI components
│   ├── contexts/        # React contexts (AuthContext)
│   ├── hooks/           # Custom React hooks
│   ├── pages/           # Page components
│   ├── services/        # API service functions
│   ├── App.js           # Main application component
│   ├── App.css          # Global styles
│   └── index.js         # Application entry point
├── package.json
└── README.md
```

## Available Scripts

- `npm start`: Runs the app in development mode
- `npm test`: Launches the test runner
- `npm run build`: Builds the app for production
- `npm run eject`: Ejects from Create React App (irreversible)

## Authentication Flow

1. **Registration**: Users can create a new account with name, email, password, and phone
2. **Login**: Existing users can log in with email and password
3. **Token Management**: JWT tokens are stored in localStorage and automatically attached to API requests
4. **Protected Routes**: Dashboard and loan features require authentication
5. **Auto-logout**: Tokens expire after 30 minutes

## API Integration

The frontend integrates with the FastAPI backend through the following endpoints:

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info
- `POST /api/protected/message` - Send chat message
- `GET /api/protected/conversation-state` - Get conversation state
- `POST /api/protected/upload-document` - Upload documents
- `POST /api/protected/reset-conversation` - Reset conversation

## Environment Variables

- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8000/api)

## Production Build

To create a production build:

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## Troubleshooting

1. **API Connection Issues**: Ensure the backend is running on port 8000
2. **CORS Errors**: Check CORS configuration in the backend
3. **Authentication Issues**: Clear localStorage and try logging in again
4. **Build Issues**: Delete `node_modules` and `package-lock.json`, then run `npm install` again

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Protected API routes
- Automatic token expiration
- Secure document upload handling