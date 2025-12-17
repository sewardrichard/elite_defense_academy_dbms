# Database Setup Guide: Elite Defense Academy

## Option A: Quick Start (Docker)
If you have Docker Desktop installed, this is the fastest method.

1. Open a terminal in the project root.
2. Run:
   ```powershell
   docker-compose up -d
   ```
3. This will:
   - Start a PostgreSQL 15 container.
   - Automatically create the `elite_defense_academy` database.
   - Automatically run `sql/01_schema.sql` to create all tables.
   - Expose the database on `localhost:5432`.

**Credentials:**
- **User:** `admin`
- **Password:** `password123`
- **Database:** `elite_defense_academy`

---

## Option B: Manual Installation (Windows)

1. **Download**: Go to [postgresql.org/download/windows](https://www.postgresql.org/download/windows/) and install the latest version (15+).
2. **Install**: Follow the wizard (remember the password you set for the `postgres` superuser!).
3. **Add to Path**: Ensure the "Command Line Tools" component is selected so you can use `psql`.
4. **Verify**:
   ```powershell
   psql --version
   ```
5. **Create Database**:
   Open "SQL Shell (psql)" or a terminal and run:
   ```sql
   CREATE DATABASE elite_defense_academy;
   ```
6. **Run Schema**:
   In your terminal, navigate to the project folder and run:
   ```powershell
   psql -U postgres -d elite_defense_academy -f sql/01_schema.sql
   ```
   *(You may need to enter your password)*.

---

## Verification
To check if the tables exist:
```powershell
# If using Docker:
docker exec -it elite_defense_db psql -U admin -d elite_defense_academy -c "\dt"
```
Or use a GUI tool like **pgAdmin** or **DBeaver** to connect to `localhost:5432`.
