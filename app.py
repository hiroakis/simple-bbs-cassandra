from bottle import route, run, redirect, request, static_file, jinja2_template
import datetime

@route('/')
def bbs_top():
    bbs = Bbs()
    data = bbs.get_all_posts()
    settings_dict = {
        'autoescape': False,
        }
    return jinja2_template('bbs.html', data=data, template_settings=settings_dict)

@route('/add_post', method='POST')
def add_post():
    name = request.forms.get('name')
    if not name:
        name = 'nanashi'
    content = request.forms.get('content')
    content = escape_special_chars(content)

    bbs = Bbs()
    bbs.add_new_post(name, content)
    redirect('/', 302)

@route('/static/<filepath:path>')
def static(filepath):
    return static_file(filepath, root='./static')

def escape_special_chars(content):
    content = content.replace('<', '&lt;')
    content = content.replace('>', '&gt;')
    content = content.replace('\'', '&#39;')
    content = content.replace('"', '&quot;')
    content = content.replace('\n', '<br>')
    return content

from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily

class Bbs(object):

    def __init__(self):
        self.conn = ConnectionPool('bbs_ks', ['localhost:9160'], pool_size=1)

    def get_all_posts(self):
        col_fam = ColumnFamily(self.conn, 'bbs')

        # get all row keys
        row_keys = []
        ret = list(col_fam.get_range())
        for v in ret:
            row_keys.append(v[0])

        # get all row data
        result = []
        ret = col_fam.multiget(row_keys)
        for key in row_keys:
            row = {}
            row['key'] = int(key)
            row['name'] = ret[key]['name']
            row['content'] = ret[key]['content']
            row['post_time'] = ret[key]['post_time']
            result.append(row)

        result.sort(cmp=lambda x,y: cmp(x["key"], y["key"]))
        return result

    def add_new_post(self, name, content):
        col_fam = ColumnFamily(self.conn, 'bbs')

        ret = list(col_fam.get_range())
        key = len(ret) + 1
        key = '%s' % key

        dt = datetime.datetime.today()
        str_dt = '%s' % dt
        col_fam.insert(key, {'name': name, 'content': content, 'post_time': str_dt})

if __name__ == '__main__':
    run(host='0.0.0.0', port=8000, debug=True, reloader=True)
