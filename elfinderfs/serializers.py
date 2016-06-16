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

from rest_framework import serializers

from .models import Node


# FIELDS


class NodeField(serializers.Field):
    def to_internal_value(self, data):
        return Node(hash_=data)


class HashesField(serializers.Field):
    def to_representation(self, obj):
        return map(lambda x: getattr(x, 'hash'), obj)


# REQUEST (CMD) SERIALIZERS


class CmdSerializer(serializers.Serializer):
    cmd = serializers.CharField(max_length=32)

    def validate_cmd(self, value):
        if value not in ('open', 'file', 'tree', 'parents',
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
        return value


class SearchCmdSerializer(CmdSerializer):
    q = serializers.CharField(max_length=4096)


class SingleTargetCmdSerializer(CmdSerializer):
    target = NodeField()

    def validate_target(self, value):
        if not value.exists():
            raise serializers.ValidationError('errFileNotFound')
        return value


class OpenCmdSerializer(CmdSerializer):
    target = NodeField(required=False)
    init = serializers.BooleanField(required=False)
    tree = serializers.BooleanField(required=False)

    def validate_target(self, value):
        ''' target is required if init is false '''
        init = self.initial_data.get('init')
        if init not in ('true', '1') and not value:
            raise serializers.ValidationError('errFileNotFound')
        if not value.exists():
            raise serializers.ValidationError('errFileNotFound')
        return value


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

    def validate_mode(self, value):
        if value not in ('resize', 'crop'):
            raise serializers.ValidationError('errResize')
        return value


class MultipleTargetsCmdSerializer(CmdSerializer):
    def get_fields(self):
        fields = super().get_fields()
        fields['targets[]'] = serializers.ListField(child=NodeField())
        return fields


class PasteCmdSerializer(MultipleTargetsCmdSerializer):
    dst = NodeField()
    cut = serializers.BooleanField(required=False)

    def validate_dst(self, value):
        if not value.exists():
            raise serializers.ValidationError('errFileNotFound')
        return value


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
    absolute_url = serializers.CharField(max_length=4096)


class NetDriverSerializer(serializers.Serializer):
    pass


class TreeNodeSerializer(serializers.Serializer):
    tree = NodeSerializer(many=True)


class FilesNodeSerializer(serializers.Serializer):
    files = NodeSerializer(many=True)


class AddedNodeSerializer(serializers.Serializer):
    added = NodeSerializer(many=True)


class RemovedNodeSerializer(serializers.Serializer):
    removed = HashesField()


class ChangedNodeSerializer(serializers.Serializer):
    changed = NodeSerializer(many=True)


class AddedRemovedNodeSerializer(AddedNodeSerializer, RemovedNodeSerializer):
    pass


class GetNodeSerializer(serializers.Serializer):
    content = serializers.CharField()


class OpenNodeSerializer(serializers.Serializer):
    cwd = NodeSerializer()
    files = NodeSerializer(many=True)
    netDrivers = NetDriverSerializer(many=True)
    uplMaxSize = serializers.CharField(max_length=32)
    api = serializers.CharField(max_length=8, required=False)
