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

from rest_framework import fields, serializers

from .models import Node


# FIELDS


class NodeField(fields.WritableField):
    def field_from_native(self, data, files, field_name, into):
        into[field_name] = Node(hash_=data[field_name])

    def field_to_native(self, obj, field_name):
        pass


class NodesField(fields.WritableField):
    def field_from_native(self, data, files, field_name, into):
        into[field_name] = map(lambda x: Node(hash_=x),
                               data.getlist(field_name + '[]'))

    def field_to_native(self, obj, field_name):
        pass


class HashesField(serializers.WritableField):
    def field_from_native(self, data, files, field_name, into):
        pass

    def field_to_native(self, obj, field_name):
        if hasattr(obj, field_name):
            field = getattr(obj, field_name)
        else:
            field = obj[field_name]
        return map(lambda x: getattr(x, 'hash'), field)


# REQUEST (CMD) SERIALIZERS


class CmdSerializer(serializers.Serializer):
    cmd = serializers.CharField(max_length=32)

    def validate_cmd(self, attrs, source):
        cmd = attrs.get(source)
        if cmd not in ('open', 'file', 'tree', 'parents',
                       # 'ls',
                       # 'tmb',
                       # 'size',
                       # 'dim',
                       'mkdir', 'mkfile', 'rm', 'rename',
                       'duplicate', 'paste', 'upload', 'get', 'put',
                       # 'archive',
                       # 'extract',
                       'search',
                       # 'info',
                       'resize',
                       # 'netmount',
                ):
            raise serializers.ValidationError('errUnknownCmd')
        return attrs


class SearchCmdSerializer(CmdSerializer):
    q = serializers.CharField(max_length=4096)


class SingleTargetCmdSerializer(CmdSerializer):
    target = NodeField()

    def validate_target(self, attrs, source):
        target = attrs.get(source)
        if not target.exists():
            raise serializers.ValidationError('errFileNotFound')
        return attrs


class OpenCmdSerializer(CmdSerializer):
    target = NodeField(required=False)
    init = serializers.BooleanField(required=False)
    tree = serializers.BooleanField(required=False)

    def validate_target(self, attrs, source):
        ''' target is required if init is false '''
        target = attrs.get(source)
        init = attrs.get('init')
        if init not in ('true', '1') and not target:
            raise serializers.ValidationError('errFileNotFound')
        if not target.exists():
            raise serializers.ValidationError('errFileNotFound')
        return attrs


class SingleTargetOpCmdSerializer(SingleTargetCmdSerializer):
    name = serializers.CharField(max_length=4096)


class FileCmdSerializer(SingleTargetCmdSerializer):
    download = serializers.BooleanField(required=False)


class PutCmdSerializer(SingleTargetCmdSerializer):
    content = serializers.CharField()


class ResizeCmdSerializer(SingleTargetCmdSerializer):
    x = serializers.IntegerField(default=0, required=False)
    y = serializers.IntegerField(default=0, required=False)
    width = serializers.IntegerField()
    height = serializers.IntegerField()
    mode = serializers.CharField(max_length=32)

    def validate_mode(self, attrs, source):
        mode = attrs.get(source)
        if mode not in ('resize', 'crop'):
            raise serializers.ValidationError('errResize')
        return attrs


class MultipleTargetsCmdSerializer(CmdSerializer):
    targets = NodesField()


class PasteCmdSerializer(MultipleTargetsCmdSerializer):
    dst = NodeField()
    cut = serializers.BooleanField(required=False)

    def validate_dst(self, attrs, source):
        dst = attrs.get(source)
        if not dst.exists():
            raise serializers.ValidationError('errFileNotFound')
        return attrs


# RESPONSE (NODE) SERIALIZERS


class NodeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=4096)
    hash = serializers.CharField(max_length=4096)
    phash = serializers.CharField(max_length=4096)
    mime = serializers.CharField(max_length=255)
    ts = serializers.IntegerField()
    date = serializers.CharField(max_length=255)
    size = serializers.IntegerField()
    dirs = serializers.IntegerField()
    read = serializers.IntegerField()
    write = serializers.IntegerField()
    locked = serializers.IntegerField()
    tmb = serializers.CharField(max_length=4096)
    alias = serializers.CharField(max_length=4096)
    thash = serializers.CharField(max_length=4096)
    dim = serializers.CharField(max_length=32)
    volumeid = serializers.CharField(max_length=64)


class NetDriverSerializer(serializers.Serializer):
    pass


class TreeNodeSerializer(serializers.Serializer):
    tree = NodeSerializer()


class FilesNodeSerializer(serializers.Serializer):
    files = NodeSerializer()


class AddedNodeSerializer(serializers.Serializer):
    added = NodeSerializer()


class RemovedNodeSerializer(serializers.Serializer):
    removed = HashesField()


class ChangedNodeSerializer(serializers.Serializer):
    changed = NodeSerializer()


class AddedRemovedNodeSerializer(AddedNodeSerializer, RemovedNodeSerializer):
    pass


class GetNodeSerializer(serializers.Serializer):
    content = serializers.CharField()


class OpenNodeSerializer(serializers.Serializer):
    cwd = NodeSerializer()
    files = NodeSerializer()
    netDrivers = NetDriverSerializer()
    uplMaxSize = serializers.CharField(max_length=32)
    api = serializers.CharField(max_length=8, required=False)
