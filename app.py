from bottle import route, run, redirect, request, static_file, jinja2_template

@route('/')
def bbs_top():
    bbs = Bbs()
    data = bbs.get_all_threads()
    settings_dict = {
        'autoescape': False,
        }
    return jinja2_template('bbs.html', data=data, template_settings=settings_dict)

@route('/create_thread', method='POST')
def create_thread():
    thread_name = request.forms.get('thread_name')
    thread_name = escape_special_chars(thread_name)
    name = request.forms.get('name')
    if not name:
        name = 'nanashi'
    else:
        name = escape_special_chars(name)
    content = request.forms.get('content')
    content = escape_special_chars(content)

    bbs = Bbs()
    thread_id = bbs.create_new_thread(thread_name)
    if bbs.add_new_post(thread_id, name, content) == False:
        redirect('/')

    redirect('/', 302)

@route('/<thread_id:int>/')
def thread(thread_id):
    bbs = Bbs()
    data = bbs.get_all_posts_in_thread(thread_id)
    title = bbs.get_thread_title(thread_id)
    settings_dict = {
        'autoescape': False,
        }
    return jinja2_template('thread.html', title=title, data=data, thread_id=thread_id, template_settings=settings_dict)

@route('/add_post', method='POST')
def add_post():
    thread_id = request.forms.get('thread_id')
    name = request.forms.get('name')
    if not name:
        name = 'nanashi'
    else:
        name = escape_special_chars(name)
    content = request.forms.get('content')
    content = escape_special_chars(content)

    bbs = Bbs()
    if bbs.add_new_post(thread_id, name, content) == False:
        redirect('/')

    bbs.update_thread_status(thread_id)
    redirect_path = '/%s/' % thread_id
    redirect(redirect_path, 302)

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
from pycassa.system_manager import SystemManager, UTF8_TYPE
import sys, random, datetime

class Bbs(object):

    def __init__(self):
        self.conn = ConnectionPool('bbs', ['localhost:9160'], pool_size=1)

    def _create_cf(self, cf_name):
        sys_mng = SystemManager('localhost:9160')
        validators = {'name': UTF8_TYPE, 'content': UTF8_TYPE, 'post_time': UTF8_TYPE}
        sys_mng.create_column_family(
            'bbs',
            cf_name,
            super=False, 
            comparator_type=UTF8_TYPE,
            key_validation_class=UTF8_TYPE, 
            column_validation_classes=validators
        )
        sys_mng.close()

    def _drop_cf(self, cf_name):
        sys_mng = SystemManager('localhost:9160')
        sys_mng.drop_column_family('bbs',cf_name)
        sys_mng.close()

    def _get_oldest_thread(self):
        threads = ColumnFamily(self.conn, 'threads')

        # get all row keys
        row_keys = []
        ret = list(threads.get_range())
        for v in ret:
            row_keys.append(v[0])

        result = []
        ret = threads.multiget(row_keys)
        for key in row_keys:
            row = {}
            row['thread_id'] = int(key)
            row['thread_name'] = int(key)
            row['post_count'] = ret[key]['post_count']
            row['create_time'] = ret[key]['create_time']
            row['update_time'] = ret[key]['update_time']
            result.append(row)

        result.sort(cmp=lambda x,y: cmp(x['update_time'], y['update_time']))
        return result[0]

    def create_new_thread(self, thread_name):
        threads = ColumnFamily(self.conn, 'threads')

        ret = list(threads.get_range())
        if len(ret) > 99:
            oldest_thread = self._get_oldest_thread()
            oldest_thread_id = str(oldest_thread['thread_id'])
            threads.remove(oldest_thread_id)
            self._drop_cf(oldest_thread_id)

        thread_id = '%s' % random.randint(1,sys.maxint)

        dt = datetime.datetime.today()
        str_dt = dt.strftime('%Y-%m-%d %H:%M:%S')
        threads.insert(thread_id, {'thread_name': thread_name, 'post_count': '1', 'create_time': str_dt, 'update_time': str_dt})

        self._create_cf(thread_id)
        return thread_id

    def add_new_post(self, thread_id, name, content):
        post = ColumnFamily(self.conn, thread_id)

        ret = list(post.get_range())
        if len(ret) > 1000:
            return False

        key = len(ret) + 1
        key = '%s' % key

        dt = datetime.datetime.today()
        str_dt = dt.strftime('%Y-%m-%d %H:%M:%S')
        post.insert(key, {'name': name, 'content': content, 'post_time': str_dt})

        return True

    def get_all_threads(self):
        threads = ColumnFamily(self.conn, 'threads')

        # get all row keys
        row_keys = []
        ret = list(threads.get_range())
        for v in ret:
            row_keys.append(v[0])

        # get all row data
        result = []
        ret = threads.multiget(row_keys)
        for key in row_keys:
            row = {}
            row['thread_id'] = int(key)
            row['thread_name'] = ret[key]['thread_name']
            row['post_count'] = ret[key]['post_count']
            row['create_time'] = ret[key]['create_time']
            row['update_time'] = ret[key]['update_time']
            result.append(row)

        result.sort(cmp=lambda x,y: cmp(y['update_time'], x['update_time']))
        return result

    def get_all_posts_in_thread(self, thread_id):
        posts = ColumnFamily(self.conn, str(thread_id))

        # get all row keys
        row_keys = []
        ret = list(posts.get_range())
        for v in ret:
            row_keys.append(v[0])

        # get all row data
        result = []
        ret = posts.multiget(row_keys)
        for key in row_keys:
            row = {}
            row['key'] = int(key)
            row['name'] = ret[key]['name']
            row['content'] = ret[key]['content']
            row['post_time'] = ret[key]['post_time']
            result.append(row)

        result.sort(cmp=lambda x,y: cmp(x['key'], y['key']))
        return result

    def update_thread_status(self, thread_id):
        threads = ColumnFamily(self.conn, 'threads')

        dt = datetime.datetime.today()
        str_dt = dt.strftime('%Y-%m-%d %H:%M:%S')

        ret = threads.get(str(thread_id), columns=['post_count'])
        post_count = int(ret['post_count']) + 1

        threads.insert(thread_id, {'post_count': str(post_count), 'update_time': str_dt})

    def get_thread_title(self, thread_id):
        threads = ColumnFamily(self.conn, 'threads')

        ret = threads.get(str(thread_id), columns=['thread_name'])
        return ret['thread_name']

if __name__ == '__main__':
    run(host='0.0.0.0', port=8000, debug=True, reloader=True)
