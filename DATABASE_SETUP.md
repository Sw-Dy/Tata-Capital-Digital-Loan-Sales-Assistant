# PostgreSQL Database Setup Guide

This guide will help you set up PostgreSQL and pgAdmin for the Tata Capital Loan Processing System.

## Prerequisites

- Docker and Docker Compose installed on your system
- Python 3.8+ installed
- The project repository cloned

## Quick Start

### 1. Start PostgreSQL and pgAdmin

From the project root directory, run:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432
- pgAdmin on port 5050

### 2. Initialize the Database

Run the database initialization script:

```bash
python init_db.py
```

This will:
- Create all necessary database tables
- Set up the database schema
- Test the database connection

### 3. Access pgAdmin

Open your browser and go to: http://localhost:5050

Login credentials:
- Email: admin@admin.com
- Password: admin

### 4. Connect to PostgreSQL in pgAdmin

1. Right-click on "Servers" in the left panel
2. Select "Create" → "Server"
3. In the "General" tab:
   - Name: Tata Capital Loans
4. In the "Connection" tab:
   - Host: postgres (or localhost if connecting from outside Docker)
   - Port: 5432
   - Database: tata_capital_loans
   - Username: postgres
   - Password: postgres
5. Click "Save"

## Database Schema

The database includes the following tables:

### Users Table
- `id` (UUID, Primary Key)
- `name` (String)
- `email` (String, Unique)
- `hashed_password` (String)
- `phone` (String, Optional)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

### Conversations Table
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key to Users)
- `stage` (String)
- `state` (JSON)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

### Messages Table
- `id` (UUID, Primary Key)
- `conversation_id` (UUID, Foreign Key to Conversations)
- `role` (String: user, assistant, system)
- `content` (Text)
- `timestamp` (Timestamp)

### Documents Table
- `id` (UUID, Primary Key)
- `conversation_id` (UUID, Foreign Key to Conversations)
- `document_type` (String)
- `file_name` (String)
- `file_path` (String)
- `status` (String: pending, processed, error)
- `processed_data` (JSON, Optional)
- `processed_at` (Timestamp, Optional)
- `created_at` (Timestamp)

### Sanction Letters Table
- `id` (UUID, Primary Key)
- `conversation_id` (UUID, Foreign Key to Conversations)
- `user_id` (UUID, Foreign Key to Users)
- `file_path` (String)
- `loan_amount` (Float, Optional)
- `interest_rate` (Float, Optional)
- `tenure` (Integer, Optional)
- `created_at` (Timestamp)

## Environment Variables

Make sure your `.env` file includes:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tata_capital_loans

# For Docker setup
POSTGRES_DB=tata_capital_loans
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin
```

## Troubleshooting

### PostgreSQL Connection Issues

1. **Port already in use**: Make sure no other PostgreSQL instance is running on port 5432
2. **Docker issues**: Try `docker-compose down` and then `docker-compose up -d`
3. **Connection refused**: Check if PostgreSQL container is running with `docker ps`

### Database Initialization Issues

1. **Import errors**: Make sure all Python dependencies are installed: `pip install -r requirements.txt`
2. **Table creation fails**: Check PostgreSQL logs with `docker-compose logs postgres`
3. **Permission errors**: Ensure the database user has proper permissions

### pgAdmin Access Issues

1. **Can't access pgAdmin**: Make sure port 5050 is not blocked by firewall
2. **Login fails**: Use the default credentials: admin@admin.com / admin
3. **Server connection fails**: Use "postgres" as hostname, not "localhost"

## Development Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs

# Reset database (WARNING: This will delete all data!)
docker-compose down -v
docker-compose up -d
python init_db.py
```

## Backup and Restore

### Backup Database
```bash
docker exec -t postgres pg_dump -U postgres tata_capital_loans > backup.sql
```

### Restore Database
```bash
docker exec -i postgres psql -U postgres tata_capital_loans < backup.sql
```

## Security Notes

- Change default passwords in production
- Use environment variables for sensitive data
- Ensure proper network security for database connections
- Regular backups are recommended

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Docker logs: `docker-compose logs`
3. Check PostgreSQL logs in pgAdmin
4. Ensure all environment variables are properly set