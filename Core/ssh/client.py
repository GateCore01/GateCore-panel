import paramiko


class SSHClient:

    def __init__(self, server):

        self.server = server
        self.client = None

    def connect(self):

        self.client = paramiko.SSHClient()

        self.client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy()
        )

        self.client.connect(
            hostname=self.server["host"],
            port=self.server["port"],
            username=self.server["username"],
            password=self.server["password"],
            timeout=10
        )

    def execute(self, command):

        stdin, stdout, stderr = self.client.exec_command(command)

        return {
            "stdout": stdout.read().decode().strip(),
            "stderr": stderr.read().decode().strip()
        }

    def close(self):

        if self.client:
            self.client.close()