# TiDB Cloud Setup

This project can use TiDB Cloud Serverless as a cloud SQL database while keeping the existing MySQL protocol stack:

- SQLAlchemy
- PyMySQL
- `mysql+pymysql://...` connection URL

## 1. Create A TiDB Cloud Serverless Cluster

1. Open TiDB Cloud and create a Serverless cluster.
2. Choose the nearest region to the backend runtime.
3. Create a database, for example:

```sql
CREATE DATABASE IF NOT EXISTS intelligent_maintenance
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

## 2. Copy Connection Information

In the TiDB Cloud console, open the cluster connection panel and copy:

- host
- port, usually `4000`
- user
- password
- database name
- SSL options

Use `backend/.env.tidb.example` as the template.

Example shape:

```env
DATABASE_URL=mysql+pymysql://<tidb_user>:<tidb_password>@<tidb_host>:4000/intelligent_maintenance?charset=utf8mb4&ssl_verify_cert=true&ssl_verify_identity=true
```

If TiDB Cloud shows a different connection string, prefer the official string from the console.

## 3. Initialize Tables

From the backend directory:

```powershell
cd backend
python -m app.init_db
```

The script creates tables and default roles/users.

Default account:

```text
admin / admin123456
```

## 4. Verify Connection

Start the backend:

```powershell
uvicorn main:app --reload
```

Then check:

```text
GET http://127.0.0.1:8000/api/health/db
```

## Notes For Demo Use

- Do not commit real `.env` credentials.
- Keep using PyMySQL for LoongArch friendliness.
- Prepare demo data before the competition day.
- Export a backup JSON from the admin backup page before the demo.
- If connection fails, first check TiDB Cloud password, host, SSL options, and network access policy.
