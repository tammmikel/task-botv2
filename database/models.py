import uuid
from datetime import datetime, timezone, timedelta
from .connection import db_connection

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
        VALUES ('{user_id}', {telegram_id}, {username_val}, {first_name_val}, {last_name_val}, '{role}', CAST('{current_time.isoformat()}' AS Timestamp));
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
        """Получение списка исполнителей (админы, главный админ, директор, менеджер)"""
        query = """
        SELECT user_id, telegram_id, username, first_name, last_name, role
        FROM users
        WHERE role IN ('admin', 'main_admin', 'director', 'manager')
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
                   assignee_id, created_by, priority, deadline):
        """Создание новой задачи"""
        task_id = generate_uuid()
        current_time = get_current_time()
        
        # Подготовка значений для вставки
        description_val = f"'{description}'" if description else "NULL"
        
        query = f"""
        INSERT INTO tasks (task_id, title, description, company_id, initiator_name, 
                          initiator_phone, assignee_id, created_by, priority, status, 
                          deadline, created_at, updated_at)
        VALUES ('{task_id}', '{title}', {description_val}, '{company_id}', 
                '{initiator_name}', '{initiator_phone}', '{assignee_id}', 
                '{created_by}', '{priority}', 'new', 
                CAST('{deadline.isoformat()}' AS Timestamp),
                CAST('{current_time.isoformat()}' AS Timestamp),
                CAST('{current_time.isoformat()}' AS Timestamp));
        """
        
        try:
            db_connection.execute_query(query)
            return task_id
        except Exception as e:
            print(f"Ошибка создания задачи: {e}")
            return None

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
        VALUES ('{company_id}', '{name}', {description_val}, '{created_by}', CAST('{current_time.isoformat()}' AS Timestamp));
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