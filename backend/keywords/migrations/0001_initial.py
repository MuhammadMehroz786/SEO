from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("stores", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Keyword",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("keyword", models.CharField(max_length=500)),
                ("search_volume", models.IntegerField(default=0)),
                ("difficulty", models.IntegerField(default=0)),
                ("cpc", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("intent", models.CharField(blank=True, default="", max_length=50)),
                ("is_tracked", models.BooleanField(default=True)),
                ("cluster_name", models.CharField(blank=True, default="", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("store", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="keywords", to="stores.store")),
            ],
            options={
                "ordering": ["-search_volume"],
            },
        ),
        migrations.CreateModel(
            name="RankHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("position", models.IntegerField(default=0)),
                ("serp_url", models.URLField(blank=True, default="", max_length=2000)),
                ("serp_features", models.JSONField(blank=True, default=list)),
                ("keyword", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rank_history", to="keywords.keyword")),
            ],
            options={
                "ordering": ["-date"],
                "unique_together": {("keyword", "date")},
            },
        ),
    ]
