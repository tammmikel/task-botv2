import uuid
from datetime import datetime, timezone, timedelta
from .connection import db_connection

def parse_deadline(deadline_value):
    """Универсальная функция парсинга дедлайна из YDB"""
    if not deadline_value:
        return 'Без дедлайна'
    
    try:
        # Проверяем формат - если строка ISO (новый формат)
        if isinstance(deadline_value, str) and 'T' in deadline_value:
            deadline_dt = datetime.fromisoformat(deadline_value.replace('Z', '+00:00'))
        # Если число в микросекундах (старый формат)
        elif isinstance(deadline_value, int):
            deadline_timestamp = deadline_value / 1000000
            deadline_dt = datetime.fromtimestamp(deadline_timestamp)
        else:
            # Если уже datetime объект
            deadline_dt = deadline_value
        
        return deadline_dt.strftime('%d.%m.%Y %H:%M')
    except Exception as e:
        print(f"Ошибка парсинга даты {deadline_value}: {e}")
        return 'Дата некорректна'


# Часовой пояс UTC+5
TIMEZONE = timezone(timedelta(hours=5))

def generate_uuid():
    """Генерация UUID строки"""
    return str(uuid.uuid4())

def get_current_time():
    """Получение текущего времени в нужном часовом поясе"""
    return datetime.now(TIMEZONE)

class DatabaseManager:
    
    @staticmethod
    def create_tables():
        """Создание всех таблиц в базе данных"""
        
        # Таблица пользователей
        users_query = """
        CREATE TABLE users (
            user_id String NOT NULL,
            telegram_id Int64 NOT NULL,
            username String,
            first_name String,
            last_name String,
            role String,
            created_at Timestamp,
            PRIMARY KEY (user_id),
            INDEX idx_telegram_id GLOBAL ON (telegram_id)
        );
        """
        
        # Таблица компаний
        companies_query = """
        CREATE TABLE companies (
            company_id String NOT NULL,
            name String NOT NULL,
            description String,
            created_by String NOT NULL,
            created_at Timestamp,
            PRIMARY KEY (company_id)
        );
        """
        
        # Таблица задач
        tasks_query = """
        CREATE TABLE tasks (
            task_id String NOT NULL,
            title String NOT NULL,
            description String,
            company_id String NOT NULL,
            initiator_name String NOT NULL,
            initiator_phone String NOT NULL,
            assignee_id String NOT NULL,
            created_by String NOT NULL,
            priority String NOT NULL,
            status String,
            deadline Timestamp NOT NULL,
            created_at Timestamp,
            updated_at Timestamp,
            PRIMARY KEY (task_id)
        );
        """
        
        # Таблица комментариев
        comments_query = """
        CREATE TABLE task_comments (
            comment_id String NOT NULL,
            task_id String NOT NULL,
            user_id String NOT NULL,
            comment_text String NOT NULL,
            created_at Timestamp,
            PRIMARY KEY (comment_id)
        );
        """
        
        # Таблица файлов
        files_query = """
        CREATE TABLE task_files (
            file_id String NOT NULL,
            task_id String NOT NULL,
            user_id String NOT NULL,
            file_name String NOT NULL,
            file_path String NOT NULL,
            file_size Int64 NOT NULL,
            content_type String NOT NULL,
            thumbnail_path String,
            created_at Timestamp,
            PRIMARY KEY (file_id)
        );
        """
        
        queries = [
            ("users", users_query),
            ("companies", companies_query),
            ("tasks", tasks_query),
            ("task_comments", comments_query),
            ("task_files", files_query)
        ]
        
        for table_name, query in queries:
            try:
                db_connection.execute_query(query)
                print(f"Таблица {table_name} создана успешно")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"Таблица {table_name} уже существует")
                else:
                    print(f"Ошибка создания таблицы {table_name}: {e}")
                    raise e

class UserManager:
    
    @staticmethod
    def create_user(telegram_id, username=None, first_name=None, last_name=None, role='admin'):
        """Создание нового пользователя"""
        user_id = generate_uuid()
        current_time = get_current_time()
        
        # Подготовка значений для вставки
        username_val = f"'{username}'" if username else "NULL"
        first_name_val = f"'{first_name}'" if first_name else "NULL"
        last_name_val = f"'{last_name}'" if last_name else "NULL"
        
        query = f"""
        INSERT INTO users (user_id, telegram_id, username, first_name, last_name, role, created_at)
        VALUES ('{user_id}', {telegram_id}, {username_val}, {first_name_val}, {last_name_val}, '{role}', Timestamp('{current_time.isoformat()}'));
        """
        
        try:
            db_connection.execute_query(query)
            return user_id
        except Exception as e:
            print(f"Ошибка создания пользователя: {e}")
            return None
    
    @staticmethod
    def get_user_by_telegram_id(telegram_id):
        """Получение пользователя по telegram_id"""
        query = f"""
        SELECT user_id, telegram_id, username, first_name, last_name, role, created_at
        FROM users
        WHERE telegram_id = {telegram_id};
        """
        
        try:
            result = db_connection.execute_query(query)
            if result[0].rows:
                row = result[0].rows[0]
                
                # Декодируем bytes в строки
                def decode_if_bytes(value):
                    if isinstance(value, bytes):
                        return value.decode('utf-8')
                    return value
                
                return {
                    'user_id': decode_if_bytes(row.user_id),
                    'telegram_id': row.telegram_id,
                    'username': decode_if_bytes(row.username),
                    'first_name': decode_if_bytes(row.first_name),
                    'last_name': decode_if_bytes(row.last_name),
                    'role': decode_if_bytes(row.role),
                    'created_at': row.created_at
                }
            return None
        except Exception as e:
            print(f"Ошибка получения пользователя: {e}")
            return None
    
    @staticmethod
    def get_users_count():
        """Получение общего количества пользователей"""
        query = "SELECT COUNT(*) as count FROM users;"
        
        try:
            result = db_connection.execute_query(query)
            if result[0].rows:
                return result[0].rows[0].count
            return 0
        except Exception as e:
            print(f"Ошибка получения количества пользователей: {e}")
            return 0
    
    @staticmethod
    def update_user_role(user_id, new_role):
        """Изменение роли пользователя"""
        query = f"""
        UPDATE users
        SET role = '{new_role}'
        WHERE user_id = '{user_id}';
        """
        
        try:
            db_connection.execute_query(query)
            return True
        except Exception as e:
            print(f"Ошибка изменения роли пользователя: {e}")
            return False
    
    @staticmethod
    def get_assignees():
        """Получение списка исполнителей (все роли могут быть исполнителями)"""
        query = """
        SELECT user_id, telegram_id, username, first_name, last_name, role
        FROM users
        WHERE role IN ('director', 'manager', 'main_admin', 'admin')
        ORDER BY first_name, last_name;
        """
        
        try:
            result = db_connection.execute_query(query)
            assignees = []
            
            if result[0].rows:
                for row in result[0].rows:
                    def decode_if_bytes(value):
                        if isinstance(value, bytes):
                            return value.decode('utf-8')
                        return value
                    
                    assignees.append({
                        'user_id': decode_if_bytes(row.user_id),
                        'telegram_id': row.telegram_id,
                        'username': decode_if_bytes(row.username),
                        'first_name': decode_if_bytes(row.first_name),
                        'last_name': decode_if_bytes(row.last_name),
                        'role': decode_if_bytes(row.role)
                    })
            
            return assignees
        except Exception as e:
            print(f"Ошибка получения исполнителей: {e}")
            return []

class TaskManager:    

    @staticmethod
    def create_task(title, description, company_id, initiator_name, initiator_phone,
                assignee_id, created_by, is_urgent, deadline):
        """Создание новой задачи"""
        task_id = generate_uuid()
        current_time = get_current_time()
        
        # Подготовка значений для вставки
        description_val = f"'{description}'" if description else "NULL"
        
        # Форматируем даты в ISO формат для YDB
        deadline_str = deadline.strftime('%Y-%m-%dT%H:%M:%SZ')
        current_str = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        query = f"""
        INSERT INTO tasks (task_id, title, description, company_id, initiator_name,
                        initiator_phone, assignee_id, created_by, is_urgent, status,
                        deadline, created_at, updated_at)
        VALUES ('{task_id}', '{title}', {description_val}, '{company_id}',
                '{initiator_name}', '{initiator_phone}', '{assignee_id}',
                '{created_by}', {is_urgent}, 'new',
                Timestamp('{deadline_str}'),
                Timestamp('{current_str}'),
                Timestamp('{current_str}'));
        """
        
        try:
            db_connection.execute_query(query)
            return task_id
        except Exception as e:
            print(f"Ошибка создания задачи: {e}")
            return None
    @staticmethod
    def get_user_tasks(user_id, role):
        """Получение задач пользователя в зависимости от роли"""
        if role in ['director', 'manager']:
            query = """
            SELECT t.task_id, t.title, t.description, t.is_urgent, t.status, t.deadline, t.created_at,
                   c.name as company_name
            FROM tasks AS t
            INNER JOIN companies AS c ON t.company_id = c.company_id
            ORDER BY t.created_at DESC;
            """
        else:
            query = f"""
            SELECT t.task_id, t.title, t.description, t.priority, t.status, t.deadline, t.created_at,
                   c.name as company_name
            FROM tasks AS t
            INNER JOIN companies AS c ON t.company_id = c.company_id
            WHERE t.assignee_id = '{user_id}'
            ORDER BY t.created_at DESC;
            """
        
        try:
            result = db_connection.execute_query(query)
            tasks = []

            status_emoji = {
                'new': '🆕',
                'in_progress': '⏳', 
                'completed': '✅',
                'overdue': '⚠️',
                'cancelled': '❌'
            }
            
            if result[0].rows:
                for row in result[0].rows:
                    def decode_if_bytes(value):
                        if isinstance(value, bytes):
                            return value.decode('utf-8')
                        return value
                    
                    deadline_str = parse_deadline(row['t.deadline'])
                    
                    # Форматируем для отображения в списке (только дата)
                    try:
                        if isinstance(row['t.deadline'], str) and 'T' in row['t.deadline']:
                            deadline_dt = datetime.fromisoformat(row['t.deadline'].replace('Z', '+00:00'))
                        elif isinstance(row['t.deadline'], int):
                            deadline_timestamp = row['t.deadline'] / 1000000
                            deadline_dt = datetime.fromtimestamp(deadline_timestamp)
                        else:
                            deadline_dt = row['t.deadline']
                        
                        deadline_short = deadline_dt.strftime('%d.%m')
                    except:
                        deadline_short = deadline_str
                    
                    tasks.append({
                        'task_id': decode_if_bytes(row['t.task_id']),
                        'title': decode_if_bytes(row['t.title']),
                        'description': decode_if_bytes(row['t.description']),
                        'is_urgent': row['t.is_urgent'],
                        'deadline_short': deadline_short,
                        'status': decode_if_bytes(row['t.status']),
                        'deadline_str': deadline_str,
                        'deadline_short': deadline_short,
                        'created_at': row['t.created_at'],
                        'deadline_short': deadline_short,
                        'company_name': decode_if_bytes(row['company_name']),
                        'status_emoji': status_emoji.get(decode_if_bytes(row['t.status']), '❓')
                    })
            
            return tasks
        except Exception as e:
            print(f"Ошибка получения задач: {e}")
            return []

    @staticmethod
    def get_companies_with_tasks(user_id, role):
        """Получение компаний с количеством задач"""
        if role in ['director', 'manager']:
            query = """
            SELECT c.company_id, c.name, COUNT(t.task_id) as task_count
            FROM companies c
            LEFT JOIN tasks t ON c.company_id = t.company_id
            GROUP BY c.company_id, c.name
            HAVING task_count > 0
            ORDER BY c.name;
            """
        else:
            query = f"""
            SELECT c.company_id, c.name, COUNT(t.task_id) as task_count
            FROM companies c
            LEFT JOIN tasks t ON c.company_id = t.company_id
            WHERE t.assignee_id = '{user_id}'
            GROUP BY c.company_id, c.name
            HAVING task_count > 0
            ORDER BY c.name;
            """
        
        try:
            result = db_connection.execute_query(query)
            companies = []
            
            if result[0].rows:
                for row in result[0].rows:
                    def decode_if_bytes(value):
                        if isinstance(value, bytes):
                            return value.decode('utf-8')
                        return value
                    
                    companies.append({
                        'company_id': decode_if_bytes(row.company_id),
                        'name': decode_if_bytes(row.name),
                        'task_count': row.task_count
                    })
            
            return companies
        except Exception as e:
            print(f"Ошибка получения компаний: {e}")
            return []

    @staticmethod
    def get_task_by_id(task_id):
        """Получение подробной информации о задаче"""
        query = f"""
        SELECT t.task_id, t.title, t.description, t.is_urgent, t.status, t.deadline, t.created_at,
               c.name as company_name, t.initiator_name, t.initiator_phone
        FROM tasks AS t
        INNER JOIN companies AS c ON t.company_id = c.company_id
        WHERE t.task_id = '{task_id}';
        """
        
        try:
            result = db_connection.execute_query(query)
            if result[0].rows:
                row = result[0].rows[0]
                
                def decode_if_bytes(value):
                    if isinstance(value, bytes):
                        return value.decode('utf-8')
                    return value
                
                # Парсим дедлайн
                deadline_str = parse_deadline(row['t.deadline'])
                
                return {
                    'task_id': decode_if_bytes(row['t.task_id']),
                    'title': decode_if_bytes(row['t.title']),
                    'description': decode_if_bytes(row['t.description']),
                    'is_urgent': row['t.is_urgent'],
                    'status': decode_if_bytes(row['t.status']),
                    'deadline_str': parse_deadline(row['t.deadline']),
                    'created_at': row['t.created_at'],
                    'company_name': decode_if_bytes(row['company_name']),
                    'initiator_name': decode_if_bytes(row['t.initiator_name']),
                    'initiator_phone': decode_if_bytes(row['t.initiator_phone'])
                }
            return None
        except Exception as e:
            print(f"Ошибка получения задачи: {e}")
            return None

    @staticmethod
    def update_task_status(task_id, new_status):
        """Изменение статуса задачи"""
        current_time = get_current_time()
        current_str = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        query = f"""
        UPDATE tasks
        SET status = '{new_status}', updated_at = Timestamp('{current_str}')
        WHERE task_id = '{task_id}';
        """
        
        try:
            db_connection.execute_query(query)
            return True
        except Exception as e:
            print(f"Ошибка изменения статуса задачи: {e}")
            return False

class CompanyManager:
    
    @staticmethod
    def create_company(name, description=None, created_by=None):
        """Создание новой компании"""
        company_id = generate_uuid()
        current_time = get_current_time()
        
        # Подготовка значений для вставки
        description_val = f"'{description}'" if description else "NULL"
        
        query = f"""
        INSERT INTO companies (company_id, name, description, created_by, created_at)
        VALUES ('{company_id}', '{name}', {description_val}, '{created_by}', Timestamp('{current_time.isoformat()}'));
        """
        
        try:
            db_connection.execute_query(query)
            return company_id
        except Exception as e:
            print(f"Ошибка создания компании: {e}")
            return None
    
    @staticmethod
    def get_all_companies():
        """Получение всех компаний"""
        query = """
        SELECT company_id, name, description, created_by, created_at
        FROM companies
        ORDER BY created_at DESC;
        """
        
        try:
            result = db_connection.execute_query(query)
            companies = []
            
            if result[0].rows:
                for row in result[0].rows:
                    # Декодируем bytes в строки
                    def decode_if_bytes(value):
                        if isinstance(value, bytes):
                            return value.decode('utf-8')
                        return value
                    
                    companies.append({
                        'company_id': decode_if_bytes(row.company_id),
                        'name': decode_if_bytes(row.name),
                        'description': decode_if_bytes(row.description),
                        'created_by': decode_if_bytes(row.created_by),
                        'created_at': row.created_at
                    })
            
            return companies
        except Exception as e:
            print(f"Ошибка получения компаний: {e}")
            return []
    
    @staticmethod
    def get_company_by_id(company_id):
        """Получение компании по ID"""
        query = f"""
        SELECT company_id, name, description, created_by, created_at
        FROM companies
        WHERE company_id = '{company_id}';
        """
        
        try:
            result = db_connection.execute_query(query)
            if result[0].rows:
                row = result[0].rows[0]
                
                def decode_if_bytes(value):
                    if isinstance(value, bytes):
                        return value.decode('utf-8')
                    return value
                
                return {
                    'company_id': decode_if_bytes(row.company_id),
                    'name': decode_if_bytes(row.name),
                    'description': decode_if_bytes(row.description),
                    'created_by': decode_if_bytes(row.created_by),
                    'created_at': row.created_at
                }
            return None
        except Exception as e:
            print(f"Ошибка получения компании: {e}")
            return None

class FileManager:
    
    @staticmethod
    def save_file_info(task_id, user_id, file_id, file_name, file_path, file_size, content_type, thumbnail_path=None):
        """Сохранение информации о файле в БД"""
        current_time = get_current_time()
        
        # Подготовка значений для вставки
        thumbnail_val = f"'{thumbnail_path}'" if thumbnail_path else "NULL"
        
        query = f"""
        INSERT INTO task_files (file_id, task_id, user_id, file_name, file_path, 
                               file_size, content_type, thumbnail_path, created_at)
        VALUES ('{file_id}', '{task_id}', '{user_id}', '{file_name}', '{file_path}', 
                {file_size}, '{content_type}', {thumbnail_val}, 
                Timestamp('{current_time.strftime('%Y-%m-%dT%H:%M:%SZ')}'));
        """
        
        try:
            db_connection.execute_query(query)
            return True
        except Exception as e:
            print(f"Ошибка сохранения файла: {e}")
            return False
    
    @staticmethod
    def get_task_files(task_id):
        """Получение всех файлов задачи"""
        query = f"""
        SELECT f.file_id, f.file_name, f.file_path, f.file_size, f.content_type, 
           f.thumbnail_path, f.created_at,
           u.first_name as first_name, u.last_name as last_name, u.username as username
        FROM task_files f
        JOIN users u ON f.user_id = u.user_id
        WHERE f.task_id = '{task_id}'
        ORDER BY f.created_at DESC;
        """
        
        try:
            result = db_connection.execute_query(query)
            files = []
            
            if result[0].rows:
                for row in result[0].rows:
                    def decode_if_bytes(value):
                        if isinstance(value, bytes):
                            return value.decode('utf-8')
                        return value
                    
                    uploader_name = f"{decode_if_bytes(row.first_name) or ''} {decode_if_bytes(row.last_name) or ''}".strip()
                    if not uploader_name:
                        uploader_name = decode_if_bytes(row.username) or "Неизвестный"
                    
                    files.append({
                        'file_id': decode_if_bytes(row.file_id),
                        'file_name': decode_if_bytes(row.file_name),
                        'file_path': decode_if_bytes(row.file_path),
                        'file_size': row.file_size,
                        'content_type': decode_if_bytes(row.content_type),
                        'thumbnail_path': decode_if_bytes(row.thumbnail_path),
                        'created_at': row.created_at,
                        'uploader_name': uploader_name
                    })
            
            return files
        except Exception as e:
            print(f"Ошибка получения файлов: {e}")
            return []