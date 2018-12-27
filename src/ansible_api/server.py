#!/usr/bin/env python
# coding: utf-8

# A restful HTTP API for ansible
# Base on ansible-runner and sanic
# Github <https://github.com/lfbear/ansible-api>
# Author: lfbear

import json

from sanic import Sanic
from sanic.response import text

from .tool import Tool
from .config import Config
from . import controller


class Server(object):

    def __init__(self):
        app = Sanic()

        app.add_route(controller.Main.as_view(), '/')
        app.add_route(controller.NonBlockTest.as_view(), '/test')
        app.add_route(controller.Command.as_view(), '/command')
        app.add_route(controller.Playbook.as_view(), '/playbook')
        app.add_route(controller.FileList.as_view(), '/filelist')
        app.add_route(controller.FileReadWrite.as_view(), '/fileitem')
        app.add_route(controller.FileExist.as_view(), '/filexist')
        app.add_route(controller.ParseVarsFromFile.as_view(), '/parsevars')
        app.add_websocket_route(controller.Message.websocket, '/message', subprotocols=['', 'remote'])

        @app.middleware('request')
        async def ip_ban(request):
            if len(Config.get('allow_ip')) and request.ip not in Config.get('allow_ip'):
                return text('Your IP (%s) is not allowed!' % request.ip, status=403)

        app.run(host=Config.get('host'), port=Config.get('port'), debug=True, workers=1)

        # print config contents
        config = Config().__dict__
        config['sign_key'] = len(config['sign_key']) * '*'  # mask signature key
        Tool.LOGGER.debug("Config at start: %s" % json.dumps(config))
