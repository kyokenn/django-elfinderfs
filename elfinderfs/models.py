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
import datetime
import os
import mimetypes
import re
import shutil

from hashlib import md5
from PIL import Image

from django.conf import settings
from django.contrib.sites.models import Site


mimetypes.init()


class AbstractNode(object):
    _root = None
    _path = None

    @staticmethod
    def encode(s):
        data = s.encode('utf8')
        data = base64.urlsafe_b64encode(data)
        return data.decode('utf8').rstrip('==')

    @staticmethod
    def decode(s):
        data = (s + '==').encode('utf8')
        data = base64.urlsafe_b64decode(data)
        return data.decode('utf8')

    def __init__(self, hash_=None, root=None, path=None):
        '''
        Usage:

        Node(hash_='abc_def')
        Node(root='Media', path='share/icons')
        '''
        if hash_:
            root_hash, path_hash = hash_.split('_')
            self._root = AbstractNode.decode(root_hash)
            self._path = AbstractNode.decode(path_hash)
        elif root and path:
            self._root, self._path = root, os.path.normpath(path)
        else:
            fallback_root = list(settings.ELFINDERFS['roots'].keys())[0]
            self._root = settings.ELFINDERFS.get('default_root', fallback_root)
            self._path = os.sep

    def __str__(self):
        return '%s:%s' % (self._root, self._path)

    def __unicode__(self):
        return '%s:%s' % (self._root, self._path)

    def __repr__(self):
        return '<Node "%s:%s">' % (self._root, self._path)

    @property
    def _config(self):
        return settings.ELFINDERFS['roots'][self._root]

    @property
    def _rpath(self):
        ''' real path '''
        return os.path.join(self._config['root'], self._path.lstrip(os.sep))

    @property
    def _is_root(self):
        return self._path == os.sep

    @property
    def _is_dir(self):
        return os.path.isdir(self._rpath)

    @property
    def _parent(self):
        if not self._is_root:
            return Node(root=self._root, path=os.path.dirname(self._path))

    def _listdir(self):
        def allowed(file_):
            path = os.path.join(self._rpath, file_)
            return not file_.startswith('.') and not os.path.islink(path)
        files = os.listdir(self._rpath)
        if not settings.ELFINDERFS.get('show_hidden'):
            files = list(filter(allowed, files))
        return files


class InfoNode(AbstractNode):
    @property
    def name(self):
        ''' Name of file/dir '''
        if self._is_root:
            return self._root
        else:
            return os.path.basename(self._path)

    @property
    def hash(self):
        '''
        Hash of current file/dir path, first symbol must be letter,
        symbols before _underline_ - volume id
        '''
        return '%s%s' % (
            self.volumeid,
            Node.encode(self._path))

    @property
    def phash(self):
        ''' Hash of parent directory. Required except roots dirs '''
        return self._parent and self._parent.hash

    @property
    def mime(self):
        ''' mime type '''
        if os.path.isdir(self._rpath):
            return 'directory'
        else:
            return mimetypes.guess_type(self._rpath)[0] or 'file'

    @property
    def ts(self):
        ''' File modification time in unix timestamp '''
        return int(os.path.getmtime(self._rpath))

    @property
    def date(self):
        '''
        Last modification time (mime). Depricated but yet supported.
        Use ts instead.
        '''
        return datetime.datetime.utcfromtimestamp(self.ts).strftime('%c')

    @property
    def size(self):
        ''' File size in bytes '''
        return os.path.getsize(self._rpath)

    @property
    def dirs(self):
        '''
        Only for directories. Marks if directory has child directories
        inside it. 0 (or not set) - no, 1 - yes.
        Do not need to calculate amount.
        '''
        if not self._is_dir:
            return 0
        try:
            children = map(lambda x: os.path.join(self._rpath, x), self._listdir())
        except OSError:
            return 0
        else:
            return 1 if any(map(os.path.isdir, children)) else 0

    @property
    def read(self):
        ''' Is readable '''
        condition = os.access(self._rpath, os.R_OK)
        if self._is_dir:
            condition = condition and os.access(self._rpath, os.X_OK)
        return 1 if condition else 0

    @property
    def write(self):
        ''' Is writable '''
        condition = os.access(self._rpath, os.W_OK)
        if self._is_dir:
            condition = condition and os.access(self._rpath, os.X_OK)
        return 1 if condition else 0

    @property
    def locked(self):
        '''
        Is file locked. If locked that object cannot be deleted,
        renamed or moved
        '''
        return 0 if os.access(os.path.dirname(self._rpath), os.W_OK) else 1

    @property
    def tmb(self):
        '''
        Only for images. Thumbnail file name, if file do not have
        thumbnail yet, but it can be generated than it must have value "1"
        '''
        pass

    @property
    def alias(self):
        ''' For symlinks only. Symlink target path '''
        pass

    @property
    def thash(self):
        ''' For symlinks only. Symlink target hash '''
        pass

    @property
    def dim(self):
        ''' For images - file dimensions. Optionally '''
        pass

    @property
    def volumeid(self):
        ''' Volume id. For root dir only. '''
        return Node.encode(self._root) + '_'


class ManagedNode(InfoNode):
    @staticmethod
    def roots():
        return map(lambda x: Node(root=x[0], path=os.sep),
                   settings.ELFINDERFS['roots'].items())

    @staticmethod
    def search(q):
        found = []
        for root in Node.roots():
            for parent, dirs, files in os.walk(root._rpath):
                for i in dirs + files:
                    if q in i:
                        rpath = os.path.join(parent, i)
                        path = os.path.relpath(rpath, root._rpath)
                        node = Node(root=root._root, path=path)
                        found.append(node)
        return found

    def exists(self):
        return os.path.exists(self._rpath)

    def files(self, root=True, tree=False):
        files = []
        if self._is_root and root:
            for root in Node.roots():
                files += root.files(root=False, tree=True)
        else:
            files = list(map(lambda x: Node(root=self._root,
                                            path=os.path.join(self._path, x)),
                             self._listdir()))
            if tree:
                files.append(self)
        return files

    def parents(self):
        files = []
        node = self
        while node:
            files += node.files(tree=True)
            node = node._parent
        return files

    def get_absolute_url(self):
        return self._config['url'] + self._path.lstrip(os.sep)

    @property
    def absolute_url(self):
        return self.get_absolute_url()

    def open(self, mode='rb'):
        return open(self._rpath, mode)

    def mkdir(self, name):
        new_path = os.path.join(self._path, name)
        new_rpath = os.path.join(self._rpath, name)
        os.mkdir(new_rpath)
        return Node(root=self._root, path=new_path)

    def mkfile(self, name):
        new_path = os.path.join(self._path, name)
        new_rpath = os.path.join(self._rpath, name)
        f = open(new_rpath, 'w')
        f.close()
        return Node(root=self._root, path=new_path)

    def rename(self, name):
        new_path = os.path.join(os.path.dirname(self._path), name)
        new_rpath = os.path.join(os.path.dirname(self._rpath), name)
        os.rename(self._rpath, new_rpath)
        return Node(root=self._root, path=new_path)

    def delete(self):
        if self._rpath != os.sep:
            if os.path.isdir(self._rpath):
                shutil.rmtree(self._rpath)
            else:
                os.remove(self._rpath)

    def duplicate(self):
        if not self._is_root:
            name = re.sub(' copy \d+', '', self.name)

            def get_name(name, i):
                ext = None
                if '.' in name:
                    ext = name.split('.')[-1]
                    name = '.'.join(name.split('.')[:-1])
                new_name = '%s copy %s' % (name, i)
                if ext is not None:
                    new_name = '%s.%s' % (new_name, ext)
                return new_name

            i = 1
            while os.path.exists(os.path.join(os.path.dirname(self._rpath),
                                              get_name(name, i))):
                i += 1
            new_name = get_name(name, i)
            new_path = os.path.join(os.path.dirname(self._path), new_name)
            new_rpath = os.path.join(os.path.dirname(self._rpath), new_name)
            if self._is_dir:
                shutil.copytree(self._rpath, new_rpath)
            else:
                shutil.copyfile(self._rpath, new_rpath)
            return Node(root=self._root, path=new_path)

    def copy(self, dst_node, cut=False):
        if not self._is_root:
            new_path = os.path.join(dst_node._path, self.name)
            new_rpath = os.path.join(dst_node._rpath, self.name)
            if self._is_dir:
                shutil.copytree(self._rpath, new_rpath)
                if cut:
                    shutil.rmtree(self._rpath, ignore_errors=False)
            else:
                shutil.copyfile(self._rpath, new_rpath)
                if cut:
                    os.remove(self._rpath)
            return Node(root=dst_node._root, path=new_path)


class ImageNodeMixin(object):
    @property
    def _is_image(self):
        return self.mime in (
            'image/jpeg', 'image/png', 'image/gif',
            'image/vnd.microsoft.icon')

    def _get_thumbnail(self, force_update=False):
        troot = os.path.join(self._config['root'],
                             self._config['thumbnails_prefix'])
        if not os.path.exists(troot):
            os.mkdir(troot)

        tfile = md5(self.hash.encode('utf-8')).hexdigest() + '.png'
        tpath = os.path.join(troot, tfile)

        if not os.path.exists(tpath) or force_update:
            image = Image.open(self._rpath)
            size = (50, 50)
            image.thumbnail(size, Image.ANTIALIAS)
            thumbnail = Image.new('RGBA', size, (255, 255, 255, 0))
            thumbnail.paste(image, (
                int((size[0] - image.size[0]) / 2),
                int((size[1] - image.size[1]) / 2)))
            thumbnail.save(tpath)
        return tfile

    @property
    def _tpath(self):
        ''' thumbnail path '''
        return self._get_thumbnail()

    @property
    def tmb(self):
        if self._is_image:
            path = os.path.join(self._config['thumbnails_prefix'],
                                self._tpath)
            return self._config['url'] + path

    @property
    def dim(self):
        if self._is_image:
            image = Image.open(self._rpath)
            return '%sx%s' % image.size

    def resize(self, width, height, x=0, y=0, mode='resize'):
        image = Image.open(self._rpath)
        new_image = image
        if mode == 'resize':
            new_image = image.resize((width, height), Image.ANTIALIAS)
            self._get_thumbnail(force_update=True)
        elif mode == 'crop':
            new_image = image.crop((x, y, width + x, height + y))
            self._get_thumbnail(force_update=True)
        new_image.save(self._rpath)


class Node(ImageNodeMixin, ManagedNode):
    ''' Virtual model which represents file/dir. '''


class SiteFiles(Site):
    class Meta(object):
        proxy = True
        verbose_name = 'Site Files'
        verbose_name_plural = 'Site Files'
