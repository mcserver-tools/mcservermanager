from core.manager import Manager

if __name__ == "__main__":
    man = Manager()
    man.setup()
    man.add_server("testsrv1", "C:/Users/emanu/source/repos/mcserver-tools/mcservermanager/servers/testsrv1/")
    man.add_server("testsrv2", "C:/Users/emanu/source/repos/mcserver-tools/mcservermanager/servers/testsrv2/")
    man.add_server("testsrv3", "C:/Users/emanu/source/repos/mcserver-tools/mcservermanager/servers/testsrv3/")
    man.run()
