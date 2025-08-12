from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('meetagain', '0005_alter_lostitem_lost_date_end_and_more'),
        ('meetagain', '0005_backfill_lost_date'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE meetagain_lostitem DROP COLUMN IF EXISTS lost_date;",
            reverse_sql="ALTER TABLE meetagain_lostitem ADD COLUMN lost_date date;"
        ),
    ]
