from pymongo import TEXT
from pymongo.operations import IndexModel
from pymodm import fields, MongoModel, EmbeddedMongoModel


class ASN(MongoModel):
    as_number = fields.CharField(blank=True, default='')
    company = fields.CharField()
    ip_prefix = fields.CharField(default='')
    prefix_url = fields.CharField()
    class Meta:
        connection_alias = 'bgp'
        collection_name = 'asn'

class Domain(MongoModel):
    domain = fields.CharField()
    ip = fields.CharField()
    record_type = fields.CharField()
    keyword = fields.CharField()
    checked = fields.BooleanField(default=False)
    as_number = fields.CharField()
    ipv4_prefix = fields.CharField(default='')
    ipv6_prefix = fields.CharField(default='')
    add_date = fields.DateTimeField()
    last_update = fields.DateTimeField()

    class Meta:
        connection_alias = 'bgp'
        collection_name = 'domain'
