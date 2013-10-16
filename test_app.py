import app
import unittest

class TestApp(unittest.TestCase):

    def setUp(self):
        self.content = '<>\'"\n'

    def test_espape_special_chars(self):
        ret = app.escape_special_chars(self.content)
        self.assertEqual('&lt;&gt;&#39;&quot;<br>', ret)
        
if __name__ == '__main__':
    unittest.main()
