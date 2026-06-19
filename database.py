from config import settings
from typing import Final
from decimal import Decimal
from mysql.connector import connect




class FinanceDB:
    def __init__(self):
        self.conn: Final = connect(
            host=settings.DB_HOST,
            port=3306,
            user=settings.DB_USERNAME,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        self.cursor: Final = self.conn.cursor(dictionary=False)
        self.create_table()


    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS operations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                op_type ENUM('income', 'expense') NOT NULL,
                category VARCHAR(50) NOT NULL,
                amount DECIMAL(12,2) NOT NULL,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_user_id (user_id)
            )
        ''')
        self.conn.commit()


    def add_operation(self, user_id, op_type, category, amount, date):
        self.cursor.execute(
            "INSERT INTO operations (user_id, op_type, category, amount, date) VALUES (%s, %s, %s, %s, %s)",
            (user_id, op_type, category, amount, date)
        )
        self.conn.commit()


    def get_balance(self, user_id):
        ''' Balance through income and expenditure accounting '''
        
        self.cursor.execute("""
            SELECT
                COALESCE(SUM(
                    CASE
                        WHEN op_type='income' THEN amount
                        WHEN op_type='expense' THEN -amount
                    END
                ),0)
            FROM operations
            WHERE user_id=%s
        """, (user_id,))
        
        row = self.cursor.fetchone()
        if row is None:
            return Decimal("0")
        
        (balance,) = row
        return balance


    def delete_last_operation(self, user_id):
        ''' Delete the last user operation '''
        
        self.cursor.execute("""
            DELETE FROM operations
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT 1
        """, (user_id,))
        
        
    def clear_history(self, user_id):
        ''' Clear the user operation history completely '''
        
        self.cursor.execute(
            "DELETE FROM operations WHERE user_id = %s",
            (user_id,)
        )
        self.conn.commit()


    def get_history(self, user_id) -> list:
        ''' Receive the last 10 transactions '''
        self.cursor.execute("""
            SELECT
                category,
                amount,
                CASE
                    WHEN op_type = 'expense' THEN '-'
                    ELSE '+'
                END AS sign
            FROM operations
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT 10
        """, (user_id,))
        
        return self.cursor.fetchall() 


    def get_category_report(self, user_id):
        ''' Counts the amount of expenses separately for each category for a specific user. '''
        
        self.cursor.execute("""
            Select category, SUM(amount)
            FROM operations
            WHERE user_id = %s
            AND op_type = 'expense'
            GROUP BY category
        """, (user_id,))
        
        category_report = self.cursor.fetchall()                        
        return category_report
      


db: Final = FinanceDB()

