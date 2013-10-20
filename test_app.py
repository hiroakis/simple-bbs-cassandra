import app
import unittest

class TestApp(unittest.TestCase):

    def setUp(self):
        self.content = '<>\'"'
        self.lf = 'a\nb\n'
        self.url_string = 'http://jkjkj1231\'~+-=_.,/%?!;:@#*&()'

    def test_espape_special_chars(self):
        ret = app.escape_special_chars(self.content)
        self.assertEqual('&lt;&gt;&#39;&quot;', ret)

    def test_replace_lf_to_br_tag(self):
        ret = app.replace_lf_to_br_tag(self.lf)
        self.assertEqual('a<br>b<br>', ret)

    def test_insert_a_tag(self):
        ret = app.insert_a_tag(self.url_string)
        ok = '<a href="%s">%s</a>' % (self.url_string, self.url_string)
        self.assertEqual(ok, ret)
        
if __name__ == '__main__':
    unittest.main()
