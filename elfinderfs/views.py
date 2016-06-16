# Copyright (C) 2014 Okami, okami@fuzetsu.info
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import base64
import itertools
import json
import os

from copy import copy

from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from wsgiref.util import FileWrapper

from .models import Node
from . import serializers


class ConnectorView(RetrieveAPIView):
    permission_classes = IsAdminUser,

    def parse_query(self, query):
        result = {}
        for k, v in query.lists():
            if not k.endswith('[]'):
                v = v[0]
            result[k] = v
        return result

    def get_serializer(self, *args, **kwargs):
        ''' response serializer '''
        data = self.request.data or self.request.query_params
        cmd = data.get('cmd')
        serializer = {
            'tree': serializers.TreeNodeSerializer,
            'parents': serializers.TreeNodeSerializer,
            'search': serializers.FilesNodeSerializer,
            'mkdir': serializers.AddedNodeSerializer,
            'mkfile': serializers.AddedNodeSerializer,
            'duplicate': serializers.AddedNodeSerializer,
            'rm': serializers.RemovedNodeSerializer,
            'resize': serializers.ChangedNodeSerializer,
            'put': serializers.ChangedNodeSerializer,
            'rename': serializers.AddedRemovedNodeSerializer,
            'paste': serializers.AddedRemovedNodeSerializer,
            'get': serializers.GetNodeSerializer,
            'open': serializers.OpenNodeSerializer,
        }.get(cmd)
        return serializer(*args, **kwargs)

    def get_cmd_serializer_class(self):
        data = self.request.data or self.request.query_params
        cmd = data.get('cmd')
        return {
            'ping': serializers.CmdSerializer,
            'search': serializers.SearchCmdSerializer,
            'tree': serializers.SingleTargetCmdSerializer,
            'parents': serializers.SingleTargetCmdSerializer,
            'get': serializers.SingleTargetCmdSerializer,
            'upload': serializers.SingleTargetCmdSerializer,
            'mkfile': serializers.SingleTargetOpCmdSerializer,
            'mkdir': serializers.SingleTargetOpCmdSerializer,
            'rename': serializers.SingleTargetOpCmdSerializer,
            'open': serializers.OpenCmdSerializer,
            'file': serializers.FileCmdSerializer,
            'put': serializers.PutCmdSerializer,
            'resize': serializers.ResizeCmdSerializer,
            'rm': serializers.MultipleTargetsCmdSerializer,
            'duplicate': serializers.MultipleTargetsCmdSerializer,
            'paste': serializers.PasteCmdSerializer,
        }.get(cmd, serializers.CmdSerializer)

    def get_cmd_serializer(self, data):
        ''' request serializer '''
        serializer = self.get_cmd_serializer_class()
        return serializer(data=data)

    def get_cmd_serializer_errors(self, serializer):
        return list(itertools.chain(*serializer.errors.values()))

    def get_object(self):
        data = self.parse_query(self.request.data or self.request.query_params)
        serializer = self.get_cmd_serializer(data=data)
        if serializer.is_valid():
            cmd = serializer.validated_data
            try:
                # OPEN #
                if cmd['cmd'] == 'open':
                    target = cmd.get('target') or Node()
                    files = target.files(tree=cmd.get('tree'))
                    response = {
                        'cwd': target,
                        'files': files,
                        'netDrivers': [],
                        'uplMaxSize': settings.ELFINDERFS.get(
                            'uplMaxSize', '32M'),
                    }
                    # if cmd.get('init'):
                    #     response['api'] = '2.0'
                    response['api'] = '2.0'
                    return response
                # TREE #
                if cmd['cmd'] == 'tree':
                    return {'tree': cmd['target'].files(tree=True)}
                # PARENTS #
                elif cmd['cmd'] == 'parents':
                    return {'tree': cmd['target'].parents()}
                # LS #
                # -- Not implemented --
                # TMB #
                # -- Not implemented --
                # SIZE #
                # -- Not implemented --
                # DIM #
                # -- Not implemented --
                # MKDIR #
                elif cmd['cmd'] == 'mkdir':
                    return {
                        'added': [cmd['target'].mkdir(cmd['name'])],
                    }
                # MKFILE #
                elif cmd['cmd'] == 'mkfile':
                    return {
                        'added': [cmd['target'].mkfile(cmd['name'])],
                    }
                # RM #
                elif cmd['cmd'] == 'rm':
                    removed = []
                    for target in cmd['targets[]']:
                        target.delete()
                        removed.append(target)
                    return {'removed': removed}
                # RENAME #
                elif cmd['cmd'] == 'rename':
                    return {
                        'added': [cmd['target'].rename(cmd['name'])],
                        'removed': [cmd['target']],
                    }
                # DUPLICATE #
                elif cmd['cmd'] == 'duplicate':
                    added = []
                    for target in cmd['targets[]']:
                        added.append(target.duplicate())
                    return {'added': added}
                # PASTE #
                elif cmd['cmd'] == 'paste':
                    added = []
                    removed = []
                    for target in cmd['targets[]']:
                        added.append(target.copy(cmd['dst'],
                                                 cut=cmd.get('cut')))
                        if cmd.get('cut'):
                            removed.append(target)
                    return {
                        'added': added,
                        'removed': removed,
                    }
                # GET #
                elif cmd['cmd'] == 'get':
                    return {'content': cmd['target'].open().read().decode('utf-8')}
                # ARCHIVE #
                # -- Not implemented --
                # EXTRACT #
                # -- Not implemented --
                # SEARCH #
                elif cmd['cmd'] == 'search':
                    return {'files': Node.search(cmd['q'])}
                # INFO #
                # -- Not implemented --
                # RESIZE #
                elif cmd['cmd'] == 'resize':
                    params = dict(filter(lambda x: x[0] in (
                        'x', 'y', 'width', 'height', 'mode'),
                        cmd.items()))
                    cmd['target'].resize(**params)
                    return {'changed': [cmd['target']]}
                # NETMOUNT #
                # -- Not implemented --
                # PUT #
                if cmd['cmd'] == 'put':
                    f = cmd['target'].open('w')
                    f.write(cmd['content'])
                    f.close()
                    return {'changed': [cmd['target']]}
            except PermissionError as e:
                raise PermissionDenied({'error': ['errPerm']})
            except FileNotFoundError as e:
                raise Http404({'error': ['errFileNotFound']})

    def upload(self, request, *args, **kwargs):
        response = {}
        data = self.parse_query(self.request.data)
        serializer = self.get_cmd_serializer(data=data)
        if serializer.is_valid():
            cmd = serializer.validated_data
            uploads = request.FILES.getlist('upload[]')
            added = []
            try:
                for upload in uploads:
                    new_node = cmd['target'].mkfile(upload.name)
                    f = new_node.open('wb')
                    f.write(upload.read())
                    f.close()
                    added.append(new_node)
            except PermissionError as e:
                response = {'error': ['errPerm']}
            except FileNotFoundError as e:
                response = {'error': ['errFileNotFound']}
            else:
                response = {'added': serializers.NodeSerializer(added, many=True).data}
        else:
            response = {
                'error': self.get_cmd_serializer_errors(serializer),
            }
        return HttpResponse(json.dumps(response),
                            content_type='application/json')

    def cmd(self, request, *args, **kwargs):
        data = self.parse_query(self.request.data or self.request.query_params)
        serializer = self.get_cmd_serializer(data=data)
        if serializer.is_valid():
            cmd = serializer.validated_data
            try:
                # FILE #
                if cmd['cmd'] == 'file':
                    if cmd.get('download'):
                        response = HttpResponse(
                            FileWrapper(cmd['target'].open()),
                            content_type=cmd['target'].mime)
                        response['Content-Disposition'] = (
                            'attachment; filename=%s' % cmd['target'].name)
                        return response
                    else:
                        return redirect(cmd['target'])
                # PING #
                elif cmd['cmd'] == 'ping':
                    response = HttpResponse()
                    response['Connection'] = 'close'
                    return response
                # UPLOAD #
                elif cmd['cmd'] == 'upload':
                    return self.upload(request, *args, **kwargs)
                else:
                    return self.retrieve(request, *args, **kwargs)
            except PermissionError as e:
                return Response({'error': ['errPerm']})
            except PermissionDenied as e:
                return Response({'error': ['errPerm']})
            except FileNotFoundError as e:
                return Response({'error': ['errFileNotFound']})
            except Http404 as e:
                return Response({'error': ['errFileNotFound']})
        else:
            return Response({
                'error': self.get_cmd_serializer_errors(serializer),
            })
        return Response({'error': ['errUnknownCmd']})

    def get(self, request, *args, **kwargs):
        return self.cmd(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.cmd(request, *args, **kwargs)
