# Copyright 2009-2010, BlueDynamics Alliance - http://bluedynamics.com
from zope.interface import (
    Interface,
    Attribute,
)

class ISoupAnnotatable(Interface):
    """Marker for persisting soup data.
    """

class ISoup(Interface):
    """The Container Interface.
    """
    
    id = Attribute(u"The id of this Soup")
    
    nextrecordindex = Attribute(u"The next record index to use.")

    def add(record):
        """Add record to soup.
        
        @param record: IRecord implementation
        @return: intid for record
        """
                    
    def query(**kw):
        """Query Soup for Records.
        
        @param kw: Keyword arguments defining the query
        @return: list of records
        """
        
    def rebuild(self):
        """replaces the catalog and reindex all records."""
    
    def reindex(record=None):
        """Reindex the catalog for this soup.
        
        if record is None reindex all records, otherwise a list of records is
        expected. 
        """
    
    def __delitem__(record):
        """Delete Record from soup.
        
        If given record not contained in soup, raise ValueError.
        
        @param record: IRecord implementation
        @raise: ValueError if record not exists in this soup.
        """

class IRecord(Interface):
    """The record Interface.
    """
    
    id = Attribute(u"The id of this Record")
    
    intid = Attribute("The intid of this record. No longint!")
    
    data = Attribute(u"Dict like object representing the Record Data")

class ICatalogFactory(Interface):
    """Factory for the catalog used for Soup.
    """
    
    def __call__():
        """Create and return the Catalog.
        
        @param return: zope.app.catalog.catalog.Catalog instance
        """