#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
#
# Copyright (c) 2008-2014 University of Dundee.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Aleksandra Tarkowska <A(dot)Tarkowska(at)dundee(dot)ac(dot)uk>, 2008.
#
# Version: 1.0
#

import os
import sys
import logging
from wsgiref.simple_server import WSGIServer

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omeroweb.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise

    import settings
    from omero.util import configure_logging

    if settings.DEBUG:
        configure_logging(settings.LOGDIR, "OMEROweb.log", loglevel=logging.DEBUG)

    logger.info("Application Starting...")

    # Monkeypatch Django development web server to always run in single thread
    # even if --nothreading is not specified on command line
    def force_nothreading(
        addr,
        port,
        wsgi_handler,
        ipv6=False,
        threading=False,
        on_bind=None,
        server_cls=WSGIServer,
    ):
        django_core_servers_basehttp_run(
            addr, port, wsgi_handler, ipv6, False, on_bind, server_cls
        )

    import django.core.servers.basehttp

    if django.core.servers.basehttp.run.__module__ != "settings":
        django_core_servers_basehttp_run = django.core.servers.basehttp.run
        django.core.servers.basehttp.run = force_nothreading

    execute_from_command_line(sys.argv)
