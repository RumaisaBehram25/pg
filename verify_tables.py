from sqlalchemy import create_engine, inspect
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)
tables = sorted(inspector.get_table_names())

print('\n✅ Tables created:')
for i, table in enumerate(tables, 1):
    print(f'   {i:2d}. {table}')

print(f'\n✅ Total: {len(tables)} tables')

# Check RLS on users table
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT tablename, policyname 
        FROM pg_policies 
        WHERE schemaname = 'public'
        ORDER BY tablename
    '''))
    policies = result.fetchall()
    
    print('\n✅ RLS Policies:')
    for table, policy in policies:
        print(f'   - {table}: {policy}')
