import os
import unittest
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash

os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog.database import Base, engine, session, User, Entry

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.client = app.test_client()
        
        Base.metadata.create_all(engine)
        
        self.user = User(name="Alice", email="alice@example.com", password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()
    
    def tearDown(self):
        """ Test teardown """
        session.close()
        
        Base.metadata.drop_all(engine)
        
    def simulate_login(self):
        with self.client.session_translate() as http_session:
            http_session["user_id"] = str(self.user.id)
            http_session["_fresh"] = True
            
    def test_add_entry(self):
        self.simulate_login()
        
        response = self.client.post("/entry/add", data={
            "title": "Test Entry",
            "content": "Test content"
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        entries = session.query(Entry).all()
        self.assertEqual(len(entries), 1)
        
        entry = entries[0]
        self.assertEqual(entry.title, "Test Entry")
        self.assertEqual(entry.content, "Test content")
        self.assertEqual(entry.author, self.user)
        
if __name__ == "__main__":
    unittest.main()