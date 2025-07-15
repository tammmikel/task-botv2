import os
import boto3
import uuid
from datetime import datetime
from PIL import Image
import io
from botocore.exceptions import ClientError

class FileStorage:
    def __init__(self):
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.access_key = os.getenv('S3_ACCESS_KEY')
        self.secret_key = os.getenv('S3_SECRET_KEY')
        self.endpoint_url = os.getenv('S3_ENDPOINT', 'https://storage.yandexcloud.net')
        
        if not all([self.bucket_name, self.access_key, self.secret_key]):
            raise ValueError("S3 credentials not configured")
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint_url
        )
    
    def upload_file(self, file_data, file_name, content_type, task_id=None):
        """Загрузка файла в S3"""
        try:
            # Генерируем уникальное имя файла
            file_id = str(uuid.uuid4())
            file_extension = os.path.splitext(file_name)[1].lower()
            
            # Создаем путь к файлу
            folder = f"tasks/{task_id}" if task_id else "temp"
            s3_key = f"{folder}/{file_id}{file_extension}"
            
            # Загружаем файл
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_data,
                ContentType=content_type,
                Metadata={
                    'original_name': file_name,
                    'upload_time': datetime.now().isoformat()
                }
            )
            
            # Создаем превью для изображений
            thumbnail_key = None
            if self.is_image(content_type):
                thumbnail_key = self.create_thumbnail(file_data, s3_key)
            
            return {
                'file_id': file_id,
                's3_key': s3_key,
                'thumbnail_key': thumbnail_key,
                'original_name': file_name,
                'content_type': content_type,
                'size': len(file_data)
            }
            
        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")
            return None
    
    def create_thumbnail(self, file_data, original_key):
        """Создание превью для изображения"""
        try:
            # Открываем изображение
            image = Image.open(io.BytesIO(file_data))
            
            # Создаем превью (максимум 300x300)
            image.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Сохраняем в буфер
            buffer = io.BytesIO()
            format_map = {
                'image/jpeg': 'JPEG',
                'image/png': 'PNG',
                'image/gif': 'GIF',
                'image/webp': 'WEBP'
            }
            
            # Определяем формат
            if image.format in format_map.values():
                save_format = image.format
            else:
                save_format = 'JPEG'
            
            image.save(buffer, format=save_format, quality=85)
            buffer.seek(0)
            
            # Загружаем превью
            thumbnail_key = original_key.replace('.', '_thumb.')
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=thumbnail_key,
                Body=buffer.getvalue(),
                ContentType=f'image/{save_format.lower()}'
            )
            
            return thumbnail_key
            
        except Exception as e:
            print(f"Ошибка создания превью: {e}")
            return None
    
    def get_file_url(self, s3_key, expires_in=3600):
        """Получение временной ссылки на файл"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            print(f"Ошибка генерации URL: {e}")
            return None
    
    def delete_file(self, s3_key):
        """Удаление файла из S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except Exception as e:
            print(f"Ошибка удаления файла: {e}")
            return False
    
    def is_image(self, content_type):
        """Проверка, является ли файл изображением"""
        image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp']
        return content_type.lower() in image_types
    
    def validate_file_size(self, file_size):
        """Проверка размера файла (максимум 100 МБ)"""
        max_size = 100 * 1024 * 1024  # 100 МБ
        return file_size <= max_size
    
    def get_file_info(self, s3_key):
        """Получение информации о файле"""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return {
                'size': response['ContentLength'],
                'content_type': response['ContentType'],
                'last_modified': response['LastModified'],
                'metadata': response.get('Metadata', {})
            }
        except Exception as e:
            print(f"Ошибка получения информации о файле: {e}")
            return None

# Глобальный экземпляр для использования
file_storage = FileStorage()