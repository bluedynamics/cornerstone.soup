# Copyright 2009-2010, BlueDynamics Alliance - http://bluedynamics.com
from zope.interface import implements
from zope.catalog.catalog import Catalog
from zope.catalog.field import FieldIndex
from zope.catalog.text import TextIndex
from zope.catalog.keyword import KeywordIndex
from cornerstone.soup.interfaces import ICatalogFactory
from cornerstone.soup.ting import TingIndex

class MyCatalogFactory(object):
    """ICatalogFactory implementation used for testing.
    """
    implements(ICatalogFactory)
    
    def create_catalog(self):
        catalog = Catalog()
        catalog[u'user'] = FieldIndex(field_name='user', field_callable=False)
        catalog[u'text'] = TextIndex(field_name='text', field_callable=False)
        catalog[u'keywords'] = KeywordIndex(field_name='keywords',
                                            field_callable=False)
        return catalog

    def __call__(self):
        self.catalog = self.create_catalog()
        return self.catalog

class TingCatalogFactory(object):
    """ICatalogFactory implementation for testing textindex NG integration to
    soup.
    """
    implements(ICatalogFactory)
    
    def create_catalog(self):
        catalog = Catalog()
        catalog[u'ting'] = TingIndex(field_name=('foo', 'bar', 'baz'),
                                     field_callable=False)
        return catalog
    
    def __call__(self):
        self.catalog = self.create_catalog()
        return self.catalog

class SortCatalogFactory(object):
    """ICatalogFactory implementation for testing sorting in soup.
    """
    implements(ICatalogFactory)
    
    def __call__(self):
        catalog = Catalog()
        catalog[u'date'] = FieldIndex(field_name='date',
                                      field_callable=False)
        return catalog