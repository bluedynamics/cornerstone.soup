# Copyright 2009-2010, BlueDynamics Alliance - http://bluedynamics.com
import uuid
import random
import tempfile
from copy import deepcopy
from zope.interface import implements
from zope.component import getUtility
from zope.annotation import IAnnotations
from zope.index.interfaces import IIndexSort
from zope.catalog.field import FieldIndex
from Acquisition import (
    aq_inner,
    aq_parent,
    aq_base,
)
from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree
from BTrees.Length import Length
from OFS.SimpleItem import SimpleItem
from cornerstone.soup.interfaces import (
    ISoupAnnotatable,
    ISoup,
    IRecord,
    ICatalogFactory
)

CACHE_PREFIX = 'soup_storage_%s'

class NoLongerSupported(Exception): pass

class StorageLocator(object):

    def __init__(self, context):
        self.context = context

    @property
    def root(self):
        obj = aq_inner(self.context)
        while True:
            if ISoupAnnotatable.providedBy(obj):
                return obj
            obj = aq_parent(obj)
            if not obj:
                raise AttributeError(u"Invalid soup context.")

    def storage(self, id):
        return self.locate(id)

    def path(self, id):
        annotations = IAnnotations(self.root)
        if isinstance(annotations[id], basestring):
            return annotations[id]
        return '/'

    def traverse(self, path):
        obj = self.root
        path = path.split('/')
        for name in path:
            try:
                obj = obj[name]
            except AttributeError, e:
                msg = u'Object at %s does not exist.' % '/'.join(path)
                raise ValueError(msg)
        return obj

    def annotated(self, obj, id):
        annotations = IAnnotations(obj)
        if not id in annotations:
            annotations[id] = SoupData()
        return annotations[id]

    def locate(self, sid):
        entity = self.annotated(self.root, sid)
        if isinstance(entity, basestring):
            entity = self.annotated(self.traverse(entity), sid)
        return entity

    def _invalidate_cache(self, id):
        key = CACHE_PREFIX % id
        if self.context.REQUEST.get(key):
            del self.context.REQUEST[key]

    def move(self, sid, target_path):
        target_context = self.traverse(target_path)
        target_annotations = IAnnotations(target_context)
        if sid in target_annotations:
            raise KeyError, 'Annotation-Key %s already used at %s' % \
                            (sid, target_path)
        root_annotations = IAnnotations(self.root)
        source_data = self.storage(sid).data
        root_ann_obj = root_annotations[sid]
        if not isinstance(root_ann_obj, SoupData):
            source_annotations = IAnnotations(self.traverse(root_ann_obj))
            del source_annotations[sid]
        root_annotations[sid] = target_path
        self._invalidate_cache(sid)
        target_soup = getSoup(self.context, sid)
        # access soup.storage once if empty soup is copied. annotation is
        # created on first storage access !!!
        target_soup.storage
        for key in source_data:
            target_soup.add(deepcopy(source_data[key]))

    def relocate(self, sid, target_path):
        target_context = self.traverse(target_path)
        target_annotations = IAnnotations(target_context)
        if sid not in target_annotations:
            raise KeyError, 'Annotation-Key %s must exist at %s' % \
                            (sid, target_path)
        root_annotations = IAnnotations(self.root)
        root_annotations[sid] = target_path
        self._invalidate_cache(sid)
        target_soup = getSoup(self.context, sid)

class SoupData(SimpleItem):

    def __init__(self):
        self.data = IOBTree()
        self.catalog = None
        self._length = Length()

    @property
    def length(self):
        if not hasattr(self, '_length'):
            # BBB
            self._length = Length()
        return self._length

    def __len__(self):
        return self.length()

def getSoup(context, id):
    return Soup(context, id)

#class Soup(object): XXX TODO: for version 3.0 make Soup simple object derived
class Soup(SimpleItem):
    implements(ISoup)

    def __init__(self, context, id):
        self.context = context
        self.id = id

    @property
    def _cachekey(self):
        return CACHE_PREFIX % self.id

    @property
    def storage(self):
        if not hasattr(self, 'context'):
            error = u'Using ISoup as utility is no longer supported. ' + \
                    u'Register your Soup as adapter instead and change the ' + \
                    u'soup lookups in your code.'
            raise NoLongerSupported(error)
        request = self.context.REQUEST
        cachekey = self._cachekey
        if request.get(cachekey):
            return request[cachekey]
        storage = StorageLocator(self.context).storage(self.id)
        request[cachekey] = storage
        return storage

    @property
    def data(self):
        return self.storage.data

    @property
    def catalog(self):
        storage = self.storage
        if not storage.catalog:
            storage.catalog = getUtility(ICatalogFactory, name=self.id)()
        return storage.catalog

    def add(self, record):
        record.intid = self._generateid()
        self.data[record.intid] = record
        self.storage.length.change(1)
        record = self.data[record.intid] # ?
        self.catalog.index_doc(record.intid, record)
        # XXX: notify subscribers here if not done by OFS, check this.
        return record.intid

    def _query(self, **kw):
        sort_index = kw.pop('_sort_index', None)
        limit = kw.pop('_limit', None)
        reverse = kw.pop('_reverse', False)
        catalog = self.catalog
        querykw = {}
        for key in kw:
            # XXX: remove special case in later version
            if isinstance(catalog[key], FieldIndex) \
              and not isinstance(kw[key], tuple) \
              and not isinstance(kw[key], list):
                querykw[key] = (kw[key], kw[key])
            else:
                querykw[key] = kw[key]
        results = catalog.apply(querykw)
        if results is not None:
            if sort_index is not None:
                index = catalog[sort_index]
                if not IIndexSort.providedBy(index):
                    msg = 'Index %s does not support sorting.' % sort_index
                    raise ValueError(msg)
                results = list(index.sort(results,
                                          limit=limit,
                                          reverse=reverse))
        return results

    def query(self, **kw):
        ids = self._query(**kw)
        for id in ids:
            yield self.data[id]

    def lazy(self, **kw):
        ids = self._query(**kw)
        for id in ids:
            yield LazyRecord(id, self)

    def clear(self):
        self.storage.__init__()
        request = self.context.REQUEST
        cachekey = self._cachekey
        if cachekey in request:
            request[cachekey] = None
        self.rebuild()

    def rebuild(self):
        self.storage.catalog = getUtility(ICatalogFactory, name=self.id)()
        self.reindex()

    def reindex(self, records=None):
        if records is None:
            records = self.data.values()
        for record in records:
            self.catalog.index_doc(record.intid, record)

    def __delitem__(self, record):
        try:
            del self.data[record.intid]
            self.storage.length.change(-1)
        except Exception, e:
            raise e
        self.catalog.unindex_doc(record.intid)

    _v_nextid = None
    _randrange = random.randrange

    def _generateid(self):
        # Stolen from zope.app.intid.
        while True:
            if self._v_nextid is None:
                self._v_nextid = self._randrange(0, 2 ** 31)
            uid = self._v_nextid
            self._v_nextid += 1
            if uid not in self.data:
                return uid
            self._v_nextid = None

class LazyRecord(object):

    def __init__(self, intid, soup):
        self.intid = intid
        self.soup = soup

    def __call__(self):
        return self.soup.data[self.intid]

EMPTY_MARKER = object()

class Record(SimpleItem):
    implements(IRecord)

    def __init__(self, **kw):
        self.id = uuid.uuid4().hex
        self.intid = None
        self.data = OOBTree()
        for key in kw.keys():
            self.data[key] = kw[key]
        self._p_changed = True

    def __getattribute__(self, name):
        try:
            attr = SimpleItem.__getattribute__(self, 'data').get(name,
                                                                 EMPTY_MARKER)
            if attr is not EMPTY_MARKER:
                return attr
        except AttributeError, e:
            pass
        return SimpleItem.__getattribute__(self, name)

    def __deepcopy__(self, memo):
        rec = self.__class__()
        rec.id = self.id
        rec.intid = self.intid
        for key in self.data:
            rec.data[key] = deepcopy(self.data[key])
        return rec
