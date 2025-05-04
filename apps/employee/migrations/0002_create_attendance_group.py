from django.db import migrations

def create_attendance_group(apps, schema_editor):
    """
    Create attendance account group if not exists `settings.ATTENDANCE_ACCOUNT_GROUP`
    with add_attendance permission.
    """
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission') 
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    # Get or create the group
    attendance_group_name = 'attendance_account_group'  # Use direct string instead of settings
    attendance_group, created = Group.objects.get_or_create(name=attendance_group_name)
    
    # Get the content type for the Attendance model
    try:
        attendance_content_type = ContentType.objects.get(app_label='attendance', model='attendance')
        # Get or create the permission
        add_permission, created = Permission.objects.get_or_create(
            codename='add_attendance',
            name='Can add attendance',
            content_type=attendance_content_type,
        )
        # Add permission to group
        attendance_group.permissions.add(add_permission)
    except ContentType.DoesNotExist:
        # Handle the case where the content type doesn't exist yet
        print("Content type for attendance model does not exist yet.")
        pass

def reverse_func(apps, schema_editor):
    # Delete the group if needed
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='attendance_account_group').delete()

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('employee', '0001_initial'),
        ('attendance', '0001_initial'),  # Add dependency on attendance app's initial migration
        ('contenttypes', '0002_remove_content_type_name'),  # Add dependency on contenttypes
    ]

    operations = [
        migrations.RunPython(create_attendance_group, reverse_func),
    ]