from osm_validator.validators.base import register
from osm_validator.validators.helpers import TagsValidator


@register
class NameBeXOldObsoleteValidator(TagsValidator):

    handle = 'name_be_x_old_obsolete'

    def check_tags_in_db(self, table):
        return table.__table__.c.tags.has_key('name:be-x-old')  # noqa

    def check_tags_in_change(self, element):
        return 'name:be-x-old' in element.tags
