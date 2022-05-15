"""Module for managing the database"""

from threading import Lock

import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker

import core.instances as instances
from database.model import Base, McServer, Discord, JavaVersion
from dataclass.mcserver import McServer as McServerObj

# pylint: disable=R0801

class DBManager():
    """Class that manages the database"""

    def __init__(self):
        if instances.DBManager is not None:
            raise Exception("There can only be one instance at a time")

        db_connection = sqlalchemy.create_engine("sqlite:///database.db",
                                                 connect_args={'check_same_thread': False})
        Base.metadata.create_all(db_connection)

        session_factory = sessionmaker(db_connection, autoflush=False)
        _session = scoped_session(session_factory)
        self.session = _session()

        self.lock = Lock()

        instances.DBManager = self

    def add_mcserver(self, mcserver_obj: McServerObj):
        """Add a McServer object to the database"""

        with self.lock:
            discord = Discord(active=mcserver_obj.dc_active, channel_id=mcserver_obj.dc_id, fulllog=mcserver_obj.dc_full)
            new_mcserver = McServer(uid=mcserver_obj.uid, path=mcserver_obj.path, name=mcserver_obj.name, port=mcserver_obj.port, max_players=mcserver_obj.max_players, ram=mcserver_obj.ram, jar=mcserver_obj.jar, whitelist=mcserver_obj.whitelist, discord=discord)
            java_version = self.session.query(JavaVersion).filter(JavaVersion.javaversion_id==1).first()
            java_version.mcserver.append(new_mcserver)
            self.session.add(discord)
            self.session.add(new_mcserver)

        self.commit()

    def add_javaversion(self, name: str, path: str):
        with self.lock:
            new_javaversion = JavaVersion(name=name, path=path)
            self.session.add(new_javaversion)
        self.commit()

    def commit(self):
        """Commits changes to database"""

        with self.lock:
            try:
                self.session.commit()
            except sqlalchemy.exc.IntegrityError:
                self.session.rollback()

    def get_mcserver(self, uid: int):
        with self.lock:
            saved = self.session.query(McServer).filter(McServer.uid==uid).first()
            if saved is None:
                raise KeyError(f"McServer database entry with uid '{uid}' can't be found")
            javapath = self.session.query(JavaVersion).filter(JavaVersion.javaversion_id==saved.javaversion_id).first().path
            return McServerObj(uid=saved.uid, name=saved.name, path=saved.path, port=saved.port, max_players=saved.max_players, ram=saved.ram, jar=saved.jar, whitelist=saved.whitelist, javapath=javapath, dc_active=saved.discord.active, dc_id=saved.discord.channel_id, dc_full=saved.discord.fulllog)

    def get_mcservers(self):
        """Returns all McServer objects in the database"""

        with self.lock:
            ret_list = [McServerObj(saved.uid, saved.name, saved.path, saved.port, saved.max_players, saved.ram, saved.jar, saved.whitelist, self.session.query(JavaVersion).filter(JavaVersion.javaversion_id==saved.javaversion_id).first().path, saved.discord.active, saved.discord.channel_id, saved.discord.fulllog) for saved in self.session.query(McServer).all()]
        return ret_list

    def get_number_of_mcservers(self):
        """Returns the number of McServer objects in the database"""

        return self.session.query(McServer).count()

    def get_new_uid(self):
        if self.get_number_of_mcservers() == 0:
            return 1
        return self.session.query(McServer).order_by(McServer.mcserver_id.desc()).first().mcserver_id + 1

    def remove_mcserver(self, uid: int):
        with self.lock:
            self.session.query(McServer).filter(McServer.uid==uid).delete()
        self.commit()

    def save_mcserver(self, mcserver_obj: McServerObj):
        with self.lock:
            db_srv: McServer = self.session.query(McServer).filter(McServer.uid==mcserver_obj.uid).first()
            if db_srv is None:
                self.lock.release()
                return self.add_mcserver(mcserver_obj)
            db_srv.name = mcserver_obj.name
            db_srv.port = mcserver_obj.path
            db_srv.port = mcserver_obj.port
            db_srv.jar = mcserver_obj.jar
            db_srv.max_players = mcserver_obj.max_players
            db_srv.ram = mcserver_obj.ram
            db_srv.whitelist = mcserver_obj.whitelist
            db_discord: Discord = db_srv.discord
            db_discord.active = mcserver_obj.dc_active
            db_discord.channel_id = mcserver_obj.dc_id
            db_discord.fulllog = mcserver_obj.dc_full
        self.commit()
