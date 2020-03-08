from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Table, DateTime
from sqlalchemy import event
from sqlalchemy.sql import functions
from sqlalchemy.ext.compiler import compiles


Base = declarative_base()

# establish a constraint naming convention.
# see http://docs.sqlalchemy.org/en/latest/core/constraints.html#configuring-constraint-naming-conventions # noqa


Base.metadata.naming_convention = {
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s"
}


class utcnow(functions.FunctionElement):
    key = 'utcnow'
    type = DateTime(timezone=True)


@compiles(utcnow)
def _default_utcnow(element, compiler, **kw):
    """default compilation handler.

    Note that there is no SQL "utcnow()" function; this is a
    "fake" string so that we can produce SQL strings that are dialect-agnostic,
    such as within tests.

    """
    return "utcnow()"


@compiles(utcnow, 'postgresql')
def _pg_utcnow(element, compiler, **kw):
    """Postgresql-specific compilation handler."""

    return "(CURRENT_TIMESTAMP AT TIME ZONE 'utc')::TIMESTAMP WITH TIME ZONE"


@event.listens_for(Table, "after_parent_attach")
def timestamp_cols(table, metadata):
    if metadata is Base.metadata:
        table.append_column(
            Column(
                'created_at', DateTime(timezone=True),
                nullable=False, default=utcnow())
        )

        table.append_column(
            Column(
                'updated_at', DateTime(timezone=True), nullable=False,
                default=utcnow(), onupdate=utcnow())
        )
