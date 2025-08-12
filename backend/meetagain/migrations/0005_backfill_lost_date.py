# meetagain/migrations/0005_backfill_lost_date.py
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('meetagain', '0003_add_lost_date_columns_sql'),  # 컬럼 추가 후에 실행!
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                UPDATE meetagain_lostitem
                SET
                  lost_date_start = COALESCE(lost_date_start, lost_date),
                  lost_date_end   = COALESCE(lost_date_end,   lost_date)
                WHERE lost_date IS NOT NULL;
            """,
            reverse_sql="""
                -- 굳이 되돌릴 필요 없지만 형식상 둠
                SELECT 1;
            """
        ),
    ]