from core.manager import Manager
from database.db_manager import DBManager

if __name__ == "__main__":
    DBManager.INSTANCE.add_javaversion("Java 17", "java")

    man = Manager()
    man.setup()
    if False:
        man.add_server("testsrv1", "C:/Users/emanu/source/repos/mcserver-tools/mcservermanager/servers/testsrv1/")
        man.add_server("testsrv2", "C:/Users/emanu/source/repos/mcserver-tools/mcservermanager/servers/testsrv2/")
        man.add_server("testsrv3", "C:/Users/emanu/source/repos/mcserver-tools/mcservermanager/servers/testsrv3/")
        man.add_server("TestServer", "C:/Minecraft/TestServer/")
    man.run()
