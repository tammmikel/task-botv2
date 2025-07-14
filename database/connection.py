import os
import ydb

class YDBConnection:
    def __init__(self):
        self.endpoint = 'grpcs://ydb.serverless.yandexcloud.net:2135'
        self.database = os.getenv('YDB_DATABASE')
        
        if not self.database:
            raise ValueError("YDB_DATABASE environment variable is required")
        
        self.driver = None
        self.session_pool = None
    
    def connect(self):
        """Создание подключения к YDB"""
        try:
            self.driver = ydb.Driver(
                endpoint=self.endpoint,
                database=self.database,
                credentials=ydb.iam.MetadataUrlCredentials()
            )
            
            # Ожидание готовности драйвера
            self.driver.wait(fail_fast=True, timeout=5)
            
            # Создание пула сессий
            self.session_pool = ydb.SessionPool(self.driver, size=10)
            
            return True
            
        except Exception as e:
            print(f"Ошибка подключения к YDB: {e}")
            return False
    
    def execute_query(self, query, parameters=None):
        """Выполнение запроса к базе данных"""
        if not self.session_pool:
            raise Exception("Нет подключения к базе данных")
        
        def callee(session):
            if parameters:
                prepared_query = session.prepare(query)
                return session.transaction().execute(
                    prepared_query,
                    parameters,
                    commit_tx=True
                )
            else:
                return session.transaction().execute(
                    query,
                    commit_tx=True
                )
        
        return self.session_pool.retry_operation_sync(callee)
    
    def close(self):
        """Закрытие подключения"""
        if self.driver:
            self.driver.stop()

# Глобальная переменная для подключения
db_connection = YDBConnection()