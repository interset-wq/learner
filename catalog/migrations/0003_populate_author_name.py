from django.db import migrations


def populate_author_name(apps, schema_editor):
    Author = apps.get_model("catalog", "Author")
    for author in Author.objects.all():
        if not author.name:
            author.name = f"{author.last_name}, {author.first_name}"
            author.save()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_alter_author_options_author_name_and_more"),
    ]

    operations = [
        migrations.RunPython(populate_author_name),
    ]
