"""Declaring data models"""

import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy.orm import relationship

Base = sqlalchemy.ext.declarative.declarative_base()

# pylint: disable=R0903

class McServer(Base):
    """McServer representation."""

    __tablename__ = "mcserver"
    mcserver_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    uid = sqlalchemy.Column(sqlalchemy.Integer, unique=True, nullable=False)
    path = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String)
    port = sqlalchemy.Column(sqlalchemy.Integer)
    max_players = sqlalchemy.Column(sqlalchemy.Integer)
    ram = sqlalchemy.Column(sqlalchemy.String)
    jar = sqlalchemy.Column(sqlalchemy.String)
    whitelist = sqlalchemy.Column(sqlalchemy.String)
    batchfile = sqlalchemy.Column(sqlalchemy.String)
    javaversion_id = sqlalchemy.Column(sqlalchemy.Integer,
                                       sqlalchemy.ForeignKey("javaversion.javaversion_id"))
    discord = relationship("Discord", cascade="all,delete", uselist=False, backref="mcserver")

class Discord(Base):
    """Discord representation."""

    __tablename__ = "discord"
    discord_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    mcserver_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("mcserver.mcserver_id"))
    active = sqlalchemy.Column(sqlalchemy.Boolean)
    channel_id = sqlalchemy.Column(sqlalchemy.Integer)
    fulllog = sqlalchemy.Column(sqlalchemy.Boolean)

class JavaVersion(Base):
    """Java version representation."""

    __tablename__ = "javaversion"
    javaversion_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    path = sqlalchemy.Column(sqlalchemy.String, unique=True)
    mcserver = relationship("McServer")
