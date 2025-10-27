# Fix for Email Subscription Error

## Error Fixed
**Problem:** UUID type mismatch when querying email_subscribers table  
**Solution:** Changed ID column type from `UUID(as_uuid=False)` to `String(36)`

## What Was Changed
**File:** `backend/app/database/models.py`  
**Line 130:** Changed `id` column definition

**Before:**
```python
id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=default_uuid, index=True)
```

**After:**
```python
id: Mapped[str] = mapped_column(String(36), primary_key=True, default=default_uuid, index=True)
```

## Next Steps

### 1. Restart Backend
The backend needs to be restarted to apply the fix:
```powershell
# In the backend terminal:
# Press Ctrl+C to stop
# Then restart:
cd backend
uvicorn app.main:app --reload
```

### 2. If Database Needs Update (Optional)
If the error persists, you may need to update the database schema:

```powershell
cd backend
python -c "from app.database.connection import SessionLocal, engine; from app.database.models import EmailSubscriber; from sqlalchemy import text; db = SessionLocal(); db.execute(text('ALTER TABLE email_subscribers ALTER COLUMN id TYPE VARCHAR(36)')); db.commit()"
```

Or simply recreate the table (if test data):
```powershell
cd backend
python -c "from app.database.connection import engine; from app.database.models import Base; Base.metadata.drop_all(bind=engine, tables=[Base.metadata.tables['email_subscribers']]); Base.metadata.create_all(bind=engine, tables=[Base.metadata.tables['email_subscribers']])"
```

### 3. Test the Fix
After restarting, test the subscription:

```powershell
$body = @{
    email = "hinahanan003@gmail.com"
    high_risk_threshold = 60.0
    medium_risk_threshold = 35.0
    notify_on_high = $true
    notify_on_medium = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/email-alerts/subscribe" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

## Why This Fix Works

The PostgreSQL database has the `id` column stored as `character varying` (VARCHAR), but SQLAlchemy was trying to cast it to UUID for comparison. This caused the error:

```
operator does not exist: character varying = uuid
```

By changing the model to use `String(36)` instead of `UUID(as_uuid=False)`, SQLAlchemy will now treat the column correctly as a string, matching what's actually in the database.

**Note:** UUIDs in string format are stored as 36-character strings (including dashes), so `String(36)` is the correct type.

## Alternative: Update Database Instead

If you prefer to keep UUIDs, you can change the database instead:

```sql
ALTER TABLE email_subscribers ALTER COLUMN id TYPE UUID USING id::uuid;
```

Then revert the model change to use `UUID(as_uuid=False)`.

But the simpler solution is what we implemented - storing UUIDs as strings (which they already are in your database).

