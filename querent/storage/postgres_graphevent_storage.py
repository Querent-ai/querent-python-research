import psycopg2
from psycopg2 import sql


class DatabaseConnection:
    def __init__(self, dbname, user, password, host, port):
        self.conn = None
        try:
            self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
            self.conn.autocommit = True
        except Exception as e:
            raise("Unable to connect to the database.")

    def insert_graph_event(self, data):
        if self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    query = sql.SQL("""INSERT INTO graph_event (subject, subject_type, object, object_type, predicate, predicate_type, sentence, document_id)
                                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""")
                    cur.execute(query, (data['subject'], data['subject_type'], data['object'], data['object_type'], data['predicate'], data['predicate_type'], data['sentence'], data['document_id']))
            except Exception as e:
                raise("An error occurred while inserting the data:")

    def close(self):
        if self.conn is not None:
            self.conn.close()