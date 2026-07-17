from ssh.client import SSHClient


def hostname(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute("hostname")

    ssh.close()

    return result["stdout"]


def os(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute("cat /etc/os-release")

    ssh.close()

    return result["stdout"]


def kernel(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute("uname -r")

    ssh.close()

    return result["stdout"]


def cpu(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute("nproc")

    ssh.close()

    return result["stdout"]


def memory(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute("free -h")

    ssh.close()

    return result["stdout"]