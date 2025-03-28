# -*- coding: utf-8 -*-
"""

    Copyright (C) 2014-2016 bromix (plugin.video.youtube)
    Copyright (C) 2016-2018 plugin.video.youtube

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""

from __future__ import absolute_import, division, unicode_literals

from datetime import datetime

from .context import Context
from .constants import TEMP_PATH
from .utils import PlayerMonitor, ServiceMonitor, rm_dir
from ..youtube.provider import Provider


def run():
    context = Context()
    context.log_debug('YouTube service initialization...')
    context.get_ui().clear_property('abort_requested')

    monitor = ServiceMonitor()
    player = PlayerMonitor(provider=Provider(), context=context)

    # wipe add-on temp folder on updates/restarts (subtitles, and mpd files)
    rm_dir(TEMP_PATH)

    sleep_time = 10
    ping_delay = 60
    ping_time = None
    while not monitor.abortRequested():
        now = datetime.now()
        if not ping_time or (ping_time - now).total_seconds() >= ping_delay:
            ping_time = now

            if monitor.httpd and not monitor.ping_httpd():
                monitor.restart_httpd()

        if monitor.waitForAbort(sleep_time):
            break

    context.get_ui().set_property('abort_requested', 'true')

    # clean up any/all playback monitoring threads
    player.cleanup_threads(only_ended=False)

    if monitor.httpd:
        monitor.shutdown_httpd()  # shutdown http server
