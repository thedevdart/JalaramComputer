from django.db import migrations, models
import django.core.validators
import shop.storage


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_product_video_alter_product_video_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image1_file',
            field=models.FileField(
                blank=True,
                default='',
                help_text='Upload primary image (JPG/PNG/WebP). Stored on Cloudinary when configured.',
                storage=shop.storage.select_image_storage,
                upload_to='product_images/',
                validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'gif', 'avif'])],
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='image2_file',
            field=models.FileField(
                blank=True,
                default='',
                help_text='Upload gallery image 2 (optional).',
                storage=shop.storage.select_image_storage,
                upload_to='product_images/',
                validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'gif', 'avif'])],
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='image3_file',
            field=models.FileField(
                blank=True,
                default='',
                help_text='Upload gallery image 3 (optional).',
                storage=shop.storage.select_image_storage,
                upload_to='product_images/',
                validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'gif', 'avif'])],
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='image4_file',
            field=models.FileField(
                blank=True,
                default='',
                help_text='Upload gallery image 4 (optional).',
                storage=shop.storage.select_image_storage,
                upload_to='product_images/',
                validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'gif', 'avif'])],
            ),
        ),
        migrations.AlterField(
            model_name='product',
            name='image_url',
            field=models.URLField(
                blank=True,
                default='',
                help_text='Fallback: external URL used only when no image file is uploaded above.',
                max_length=500,
            ),
        ),
        migrations.AlterField(
            model_name='product',
            name='image_url2',
            field=models.URLField(
                blank=True,
                default='',
                help_text='Fallback: external URL used only when no file is uploaded for image 2.',
                max_length=500,
            ),
        ),
        migrations.AlterField(
            model_name='product',
            name='image_url3',
            field=models.URLField(
                blank=True,
                default='',
                help_text='Fallback: external URL used only when no file is uploaded for image 3.',
                max_length=500,
            ),
        ),
        migrations.AlterField(
            model_name='product',
            name='image_url4',
            field=models.URLField(
                blank=True,
                default='',
                help_text='Fallback: external URL used only when no file is uploaded for image 4.',
                max_length=500,
            ),
        ),
    ]
