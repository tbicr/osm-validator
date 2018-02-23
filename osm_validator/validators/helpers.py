from sqlalchemy import ARRAY, BigInteger, and_, cast
from sqlalchemy.dialects.postgresql import array

from osm_validator.models import Issue, OSMLine, OSMPoint, OSMPolygon
from osm_validator.validators.base import BaseValidator


class TagsValidator(BaseValidator):

    handle = None

    def __init__(self, conn):
        super().__init__()
        self.conn = conn

    def check_tags_in_db(self, table):
        raise NotImplementedError()

    def check_tags_in_change(self, element):
        raise NotImplementedError()

    async def init(self):
        points = await (await self.conn.execute(OSMPoint.__table__.select().where(
            self.check_tags_in_db(OSMPoint)
        ))).fetchall()
        lines = await (await self.conn.execute(OSMLine.__table__.select().where(
            self.check_tags_in_db(OSMLine)
        ))).fetchall()
        polygons = await (await self.conn.execute(OSMPolygon.__table__.select().where(
            self.check_tags_in_db(OSMPolygon)
        ))).fetchall()

        return [
            Issue(
                handle=self.handle,
                affected_node_ids=[point.osm_id],
            ) for point in points
        ] + [
            Issue(
                handle=self.handle,
                affected_way_ids=[line.osm_id],
            ) for line in lines
        ] + [
            Issue(
                handle=self.handle,
                affected_way_ids=[polygon.osm_id],
            ) for polygon in polygons if polygon.osm_id > 0
        ] + [
            Issue(
                handle=self.handle,
                affected_rel_ids=[-polygon.osm_id],
            ) for polygon in polygons if polygon.osm_id < 0
        ]

    async def _get_osm_objects_with_issues(self, changes):
        node_issues_set = {Issue(**i) for i in (await (await self.conn.execute(
            Issue.__table__.select().where(and_(
                Issue.__table__.c.handle == self.handle,
                Issue.__table__.c.date_closed is not None,
                Issue.__table__.c.affected_node_ids.overlap(
                    cast(array(changes.affected_node_ids), ARRAY(BigInteger))),
            ))
        )).fetchall())}
        way_issues_set = {Issue(**i) for i in (await (await self.conn.execute(
            Issue.__table__.select().where(and_(
                Issue.__table__.c.handle == self.handle,
                Issue.__table__.c.date_closed is not None,
                Issue.__table__.c.affected_way_ids.overlap(
                    cast(array(changes.affected_way_ids), ARRAY(BigInteger))),
            ))
        )).fetchall())}
        rel_issues_set = {Issue(**i) for i in (await (await self.conn.execute(
            Issue.__table__.select().where(and_(
                Issue.__table__.c.handle == self.handle,
                Issue.__table__.c.date_closed is not None,
                Issue.__table__.c.affected_rel_ids.overlap(
                    cast(array(changes.affected_rel_ids), ARRAY(BigInteger))),
            ))
        )).fetchall())}
        node_issues = {n: i for i in node_issues_set for n in i.affected_node_ids}
        way_issues = {w: i for i in way_issues_set for w in i.affected_way_ids}
        rel_issues = {r: i for i in rel_issues_set for r in i.affected_rel_ids}

        return node_issues, way_issues, rel_issues

    def _new_issues_for_created_objects(self, changed_objects, affected_type):
        for element in changed_objects:
            if self.check_tags_in_change(element):
                issue = Issue(
                    handle=self.handle,
                    changeset_created_id=element.changeset,
                    user_created_id=element.uid,
                    date_created=element.timestamp,
                    **{affected_type: [element.id]},
                )
                yield issue

    def _new_issues_for_updated_objects(self, changed_objects, object_issue_map, affected_type):
        for element in changed_objects:
            if self.check_tags_in_change(element) and element.id not in object_issue_map:
                issue = Issue(
                    handle=self.handle,
                    changeset_created_id=element.changeset,
                    user_created_id=element.uid,
                    date_created=element.timestamp,
                    **{affected_type: [element.id]},
                )
                yield issue

    def _closed_issues_for_updated_objects(self, changed_objects, object_issue_map):
        for element in changed_objects:
            if not self.check_tags_in_change(element) and element.id in object_issue_map:
                issue = object_issue_map[element.id]
                issue.changeset_closed_id = element.changeset
                issue.user_closed_id = element.uid
                issue.date_closed = element.timestamp
                yield issue

    def _closed_issues_for_deleted_objects(self, changed_objects, object_issue_map):
        for element in changed_objects:
            if element.id in object_issue_map:
                issue = object_issue_map[element.id]
                issue.changeset_closed_id = element.changeset
                issue.user_closed_id = element.uid
                issue.date_closed = element.timestamp
                yield issue

    async def check(self, changes):
        new = []
        closed = []

        node_issues, way_issues, rel_issues = await self._get_osm_objects_with_issues(changes)

        for change in changes.changes:
            new.extend(self._new_issues_for_created_objects(
                change.created_nodes, 'affected_node_ids'))
            new.extend(self._new_issues_for_created_objects(
                change.created_ways, 'affected_way_ids'))
            new.extend(self._new_issues_for_created_objects(
                change.created_relations, 'affected_rel_ids'))

            new.extend(self._new_issues_for_updated_objects(
                change.modified_nodes, node_issues, 'affected_node_ids'))
            new.extend(self._new_issues_for_updated_objects(
                change.modified_ways, way_issues, 'affected_way_ids'))
            new.extend(self._new_issues_for_updated_objects(
                change.modified_relations, rel_issues, 'affected_rel_ids'))

            closed.extend(self._closed_issues_for_updated_objects(
                change.modified_nodes, node_issues))
            closed.extend(self._closed_issues_for_updated_objects(
                change.modified_ways, way_issues))
            closed.extend(self._closed_issues_for_updated_objects(
                change.modified_relations, rel_issues))

            closed.extend(self._closed_issues_for_deleted_objects(
                change.deleted_nodes, node_issues))
            closed.extend(self._closed_issues_for_deleted_objects(
                change.deleted_ways, way_issues))
            closed.extend(self._closed_issues_for_deleted_objects(
                change.deleted_relations, rel_issues))

        return new, closed
