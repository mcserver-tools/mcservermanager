if __name__ == "__main__":
    from database.db_manager import DBManager
    DBManager()

    from core.manager import Manager
    Manager()

    import core.instances as instances

    instances.DBManager.add_javaversion("Java 17", "java")
    instances.Manager.setup()
    instances.Manager.run()
