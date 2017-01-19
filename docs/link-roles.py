# based on http://protips.readthedocs.io/link-roles.html

from docutils import nodes
import re
import os

def run_cmd_get_output(cmd):
    return re.sub('^v', '', os.popen(cmd).read().strip())

def get_github_url():
    path = run_cmd_get_output('git rev-parse --short HEAD')
    tag = run_cmd_get_output('git describe --exact-match')
    print 'Git commit ID: ', path
    if len(tag):
        print 'Git tag: ', tag
        path = tag
    return 'https://github.com/espressif/esp-idf/tree/%s/' % path


def setup(app):
    baseurl = get_github_url()
    app.add_role('tree', autolink(baseurl + '%s'))
    app.add_role('component', autolink(baseurl + 'components/%s'))
    app.add_role('example', autolink(baseurl + 'examples/%s'))

def autolink(pattern):
    def role(name, rawtext, text, lineno, inliner, options={}, content=[]):
        url = pattern % (text,)
        node = nodes.reference(rawtext, text, refuri=url, **options)
        return [node], []
    return role
