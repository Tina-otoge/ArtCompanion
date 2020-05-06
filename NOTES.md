disco-py requires gevent, however it asks for gevent 1.4.0, which does not
support Python 3.8 or something

a workaround for this is to manually install gevent, a change the import in
disco-py/bot/bot.py from
```py
from gevent.wsgi
```
to
```py
from gevent.pywsgi
```
