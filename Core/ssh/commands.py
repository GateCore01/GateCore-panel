from ssh.client import SSHClient


def run(server, command):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(command)

    ssh.close()

    return result