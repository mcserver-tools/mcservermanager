from manager import Manager

if __name__ == "__main__":
    man = Manager()
    man.setup()
    man.add_server("testsrv", "C:/Users/emanu/source/repos/mcserver-tools/mcservermanager/servers/testsrv2/")
    man.run()
