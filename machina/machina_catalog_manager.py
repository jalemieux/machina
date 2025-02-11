import sqlite3
from typing import List
from machina import Machina  # Ensure this import is correct based on your project structure

class MachinaCatalogManager:
    def __init__(self, db_path='machina_catalog.db'):
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS machina_instances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                tools TEXT NOT NULL,
                prompt TEXT NOT NULL,
                catalog_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def add_machina(self, name, tools, prompt, catalog_description):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO machina_instances (name, tools, prompt, catalog_description)
            VALUES (?, ?, ?, ?)
        ''', (name, tools, prompt, catalog_description))
        conn.commit()
        conn.close()

    def get_machina_by_name(self, name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM machina_instances WHERE name = ?
        ''', (name,))
        result = cursor.fetchone()
        conn.close()
        return result

    def get_all_machinas(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM machina_instances')
        results = cursor.fetchall()
        conn.close()
        return results

    def catalog_machinas(self, machinas: List[Machina]) -> dict:
        question = """
        Based on the initial prompt and the tools available to you, please provide a detailed response covering the following points:
            1. Purpose:
            • What is your overall purpose as a language model?
            • What are the primary goals you are designed to achieve?
            2. Capabilities:
            • What tasks or operations can you perform using the available tools?
            • How can these tools assist in executing your functions?
            • Please give examples if applicable.
            3. Limitations:
            • What actions or tasks are outside your scope or beyond what you are allowed to do?
            • Are there any specific constraints or rules that restrict your functionality?

            Provide your explanation in a clear and structured manner.
        """
        responses = {}
        for machina in machinas:
            response = machina.ask(question)
            responses[machina.name] = response.parts[0].text
            self.add_machina(machina.name, str([tool.__class__.__name__ for tool in machina.tools]), machina.system_prompt, responses[machina.name])
        return responses 