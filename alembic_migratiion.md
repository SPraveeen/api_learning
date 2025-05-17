- alembic is used for database migration

- `pip install alembic`

- `alembic init alembic` - to create alembic folder, and alembic.ini file

- open env.py from alembic folder and add the following line

```
from app.database import Base, SQLALCHEMY_DATABASE_URL
from app.models import *

config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
target_metadata = Base.metadata

```



- `alembic revision --autogenerate -m "initial migration"` - to create a new migration file

- `alembic upgrade head` - to apply the migration