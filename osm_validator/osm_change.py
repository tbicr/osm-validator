from datetime import datetime
from io import BytesIO

from lxml import etree


class Node(object):
    __slots__ = ('id', 'version', 'timestamp', 'uid', 'user', 'changeset', 'lat', 'lon', 'tags')

    def __init__(self, *, id, version, timestamp, uid, user, changeset, lat, lon, tags):
        self.id = id
        self.version = version
        self.timestamp = timestamp
        self.uid = uid
        self.user = user
        self.changeset = changeset
        self.lat = lat
        self.lon = lon
        self.tags = tags

    def __eq__(self, other):
        return self.id, self.version == other.id, other.version

    def __hash__(self):
        return hash((self.id, self.version))

    @staticmethod
    def from_xml(item):
        id = int(item.attrib['id'])
        version = int(item.attrib['version'])
        timestamp = datetime.strptime(item.attrib['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
        uid = int(item.attrib['uid'])
        user = item.attrib['user']
        changeset = int(item.attrib['changeset'])
        lat = float(item.attrib['lat'])
        lon = float(item.attrib['lon'])
        tags = {x.attrib['k']: x.attrib['v'] for x in item.getchildren()}

        return Node(
            id=id,
            version=version,
            timestamp=timestamp,
            uid=uid,
            user=user,
            changeset=changeset,
            lat=lat,
            lon=lon,
            tags=tags,
        )


class Way(object):
    __slots__ = ('id', 'version', 'timestamp', 'uid', 'user', 'changeset', 'nodes', 'tags')

    def __init__(self, *, id, version, timestamp, uid, user, changeset, nodes, tags):
        self.id = id
        self.version = version
        self.timestamp = timestamp
        self.uid = uid
        self.user = user
        self.changeset = changeset
        self.nodes = nodes
        self.tags = tags

    def __eq__(self, other):
        return self.id, self.version == other.id, other.version

    def __hash__(self):
        return hash((self.id, self.version))

    @staticmethod
    def from_xml(item):
        id = int(item.attrib['id'])
        version = int(item.attrib['version'])
        timestamp = datetime.strptime(item.attrib['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
        uid = int(item.attrib['uid'])
        user = item.attrib['user']
        changeset = int(item.attrib['changeset'])
        nodes = []
        tags = {}
        for x in item.getchildren():
            if x.tag == 'nd':
                nodes.append(int(x.attrib['ref']))
            else:
                tags[x.attrib['k']] = x.attrib['v']
        return Way(
            id=id,
            version=version,
            timestamp=timestamp,
            uid=uid,
            user=user,
            changeset=changeset,
            nodes=tuple(nodes),
            tags=tags,
        )


class Member(object):
    __slots__ = ('type', 'ref', 'role')

    def __init__(self, *, type, ref, role):
        self.type = type
        self.ref = ref
        self.role = role

    def __eq__(self, other):
        return self.type, self.ref, self.role == other.type, other.id, other.role

    def __hash__(self):
        return hash((self.type, self.ref, self.role))


class Relation(object):
    __slots__ = ('id', 'version', 'timestamp', 'uid', 'user', 'changeset', 'members', 'tags')

    def __init__(self, *, id, version, timestamp, uid, user, changeset, members, tags):
        self.id = id
        self.version = version
        self.timestamp = timestamp
        self.uid = uid
        self.user = user
        self.changeset = changeset
        self.members = members
        self.tags = tags

    def __eq__(self, other):
        return self.id, self.version == other.id, other.version

    def __hash__(self):
        return hash((self.id, self.version))

    @staticmethod
    def from_xml(item):
        id = int(item.attrib['id'])
        version = int(item.attrib['version'])
        timestamp = datetime.strptime(item.attrib['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
        uid = int(item.attrib['uid'])
        user = item.attrib['user']
        changeset = int(item.attrib['changeset'])
        members = []
        tags = {}
        for x in item.getchildren():
            if x.tag == 'member':
                members.append(Member(
                    type=x.attrib['type'],
                    ref=int(x.attrib['ref']),
                    role=x.attrib['role'],
                ))
            else:
                tags[x.attrib['k']] = x.attrib['v']
        return Relation(
            id=id,
            version=version,
            timestamp=timestamp,
            uid=uid,
            user=user,
            changeset=changeset,
            members=tuple(members),
            tags=tags,
        )


class OsmChange(object):
    __slots__ = ('changeset',
                 'created_nodes', 'created_ways', 'created_relations',
                 'deleted_nodes', 'deleted_ways', 'deleted_relations',
                 'modified_nodes', 'modified_ways', 'modified_relations')

    def __init__(self, changeset):
        self.changeset = changeset
        self.created_nodes = set()
        self.created_ways = set()
        self.created_relations = set()
        self.deleted_nodes = set()
        self.deleted_ways = set()
        self.deleted_relations = set()
        self.modified_nodes = set()
        self.modified_ways = set()
        self.modified_relations = set()

    def __eq__(self, other):
        return self.changeset == other.changeset

    def __hash__(self):
        return hash(self.changeset)


class OsmChangeList(object):

    def __init__(self, changes, affected_node_ids, affected_way_ids, affected_rel_ids):
        self.changes = changes
        self.affected_node_ids = affected_node_ids
        self.affected_way_ids = affected_way_ids
        self.affected_rel_ids = affected_rel_ids


def parse_osc(file):
    match_type = {
        'node': Node,
        'way': Way,
        'relation': Relation,
    }
    match_path = {
        ('create', 'node'): 'created_nodes',
        ('create', 'way'): 'created_ways',
        ('create', 'relation'): 'created_relations',
        ('delete', 'node'): 'deleted_nodes',
        ('delete', 'way'): 'deleted_ways',
        ('delete', 'relation'): 'deleted_relations',
        ('modify', 'node'): 'modified_nodes',
        ('modify', 'way'): 'modified_ways',
        ('modify', 'relation'): 'modified_relations',
    }
    changes = {}
    affected_ids = {
        'node': set(),
        'way': set(),
        'relation': set(),
    }
    for event, element in etree.iterparse(BytesIO(file)):
        if element.tag not in ['modify', 'delete', 'create']:
            continue
        for item in element.getchildren():
            instance = match_type[item.tag].from_xml(item)
            if instance.changeset not in changes:
                changes[instance.changeset] = OsmChange(instance.changeset)
            getattr(changes[instance.changeset], match_path[(element.tag, item.tag)]).add(instance)
            affected_ids[item.tag].add(instance.id)
    return OsmChangeList(
        tuple(sorted(changes.values(), key=lambda c: c.changeset)),
        affected_ids['node'], affected_ids['way'], affected_ids['relation'],
    )
