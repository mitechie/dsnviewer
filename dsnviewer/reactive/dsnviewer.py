import os

from charms.reactive import (
    when,
    when_not,
    set_flag
)

from charmhelpers import fetch
from charmhelpers.core import hookenv as env


HTMLFILE = '/var/www/html/index.html'
HTMLTPL = "<html><head></head><body><h2>{}</h2></body></html>"


@when_not('dsnviewer.installed')
def install_dsnviewer():
    env.status_set('maintenance', 'Installing webserver')
    fetch.apt_install(['nginx'])
    set_flag('dsnviewer.installed')
    env.open_port(80)


@when('db.available')
def setup_mysql(mysql):
    env.log('Writing DB Info')
    env.log(mysql.host())
    # [username[:password]@][protocol[(address)]]/dbname
    dsn = "{0}:{1}@{2}:{3}/{4}".format(
        mysql.user(),
        mysql.password(),
        mysql.host(),
        mysql.port(),
        mysql.database(),
    )

    # Writing our configuration file to 'example.cfg'
    with open(HTMLFILE, 'w') as config:
        config.write(HTMLTPL.format(dsn))

    env.log('{} written'.format(HTMLFILE))
    ipaddr = env.unit_get('public-address')
    env.log(ipaddr)
    env.status_set('ready', 'http://{}/index.html'.format(ipaddr))


@when_not('db.available')
def remove_mysql():
    """If the relation is broken remove the db connection info."""
    if os.path.isfile(HTMLFILE):
        env.log('Removing {}'.format(HTMLFILE))
        os.remove(HTMLFILE)
    else:
        env.log('{} does not exist'.format(HTMLFILE))

    env.status_set('blocked',
                   'Missing required relation to MySQL')
