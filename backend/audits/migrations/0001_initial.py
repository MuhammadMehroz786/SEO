import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stores', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('pages_crawled', models.IntegerField(default=0)),
                ('issues_found', models.IntegerField(default=0)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='audit_runs', to='stores.store')),
            ],
            options={
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='AuditIssue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_type', models.CharField(choices=[('missing_title', 'Missing Title'), ('missing_meta_description', 'Missing Meta Description'), ('title_too_long', 'Title Too Long'), ('title_too_short', 'Title Too Short'), ('meta_desc_too_long', 'Meta Description Too Long'), ('meta_desc_too_short', 'Meta Description Too Short'), ('missing_h1', 'Missing H1'), ('duplicate_title', 'Duplicate Title'), ('duplicate_meta_description', 'Duplicate Meta Description'), ('missing_alt_text', 'Missing Image Alt Text'), ('broken_link', 'Broken Link'), ('slow_page', 'Slow Page'), ('missing_schema', 'Missing Schema Markup'), ('redirect_chain', 'Redirect Chain'), ('missing_canonical', 'Missing Canonical')], max_length=50)),
                ('severity', models.CharField(choices=[('critical', 'Critical'), ('warning', 'Warning'), ('info', 'Info')], max_length=10)),
                ('description', models.TextField()),
                ('fix_suggestion', models.TextField(blank=True, default='')),
                ('audit_run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issues', to='audits.auditrun')),
                ('page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='audit_issues', to='stores.page')),
            ],
            options={
                'ordering': ['severity', 'issue_type'],
            },
        ),
    ]
