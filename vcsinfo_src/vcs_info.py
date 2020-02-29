import argparse
import json

import paramiko


GIT_VCS_TYPE = "GIT"
SVN_VCS_TYPE = "SVN"


class DecodeException(Exception):
    pass


class VCSInfo:
    project_path = None
    users_connect_data = None

    def __init__(self, user_file_path="users.json", project_path="~/bw"):
        self.project_path = project_path
        self.users_connect_data = self.get_users_from_file(user_file_path)

    def collect_data(self):
        result = {}
        for user in self.users_connect_data:
            ssh_connect = self.connect_ssh(
                user.get("hostname"), user.get("user"), user.get("user"), key_filename=user.get("key_path")
            )

            try:
                vcs_type = self.get_type_of_vcs(ssh_connect)
            except Exception as e:
                result[user.get("user")] = {
                    "vcs_type": None,
                    "vcs_type_error": str(e),
                    "auth_type": "KEY FILE" if user.get("key_path") else "PASSWORD",
                }
                ssh_connect.close()
                continue

            if vcs_type == GIT_VCS_TYPE:
                vcs_data = self.get_git_vcs_data(ssh_connect)
            else:
                vcs_data = self.get_svn_vcs_data(ssh_connect)

            result.update(
                {
                    user.get("user"): {
                        "vcs_type": vcs_type,
                        "auth_type": "KEY FILE" if user.get("key_path") else "PASSWORD",
                        **vcs_data,
                    }
                }
            )
            ssh_connect.close()

        return result

    def get_git_vcs_data(self, ssh_connect):
        try:
            return dict(
                revision=self.send_command(ssh_connect, f"cd {self.project_path}; git rev-parse HEAD"),
                branch_name=self.send_command(
                    ssh_connect, f"cd {self.project_path}; git rev-parse --abbrev-ref HEAD"
                ),
            )
        except Exception as e:
            return dict(error=str(e))

    def get_svn_vcs_data(self, ssh_connect):
        try:
            return dict(
                revision=self.send_command(
                    ssh_connect, f"cd {self.project_path}; svn info | grep 'Revision' | awk '{{print $2}}'"
                ),
                branch=self.send_command(
                    ssh_connect,
                    f"cd {self.project_path}; svn info | grep '^URL:' | egrep -o '(tags|branches)/[^/]+|trunk' "
                    f"| egrep -o '[^/]+$'",
                ),
            )
        except Exception as e:
            return dict(error=str(e))

    def get_users_from_file(self, file_path: str) -> list:
        with open(file_path, "r") as file:
            try:
                return json.loads(file.read())
            except json.JSONDecodeError:
                raise DecodeException("Bad file content! Must be json!")

    def connect_ssh(self, host, username, password=None, key_filename=None):
        if not (password or key_filename):
            raise Exception("Need password or path to key")

        ssh_connect = paramiko.SSHClient()
        ssh_connect.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_connect.connect(host, username=username, password=password, key_filename=key_filename)
        return ssh_connect

    def send_command(self, ssh_connect, command):
        stdin, stdout, stderr = ssh_connect.exec_command(command)
        errors = stderr.read().decode()
        if errors:
            raise Exception(errors)
        return stdout.read().decode().rstrip()

    def get_type_of_vcs(self, ssh_connect) -> str:
        command_result = self.send_command(ssh_connect, f"cd {self.project_path}; ls -la")
        if ".git" in command_result:
            return GIT_VCS_TYPE
        elif ".svn" in command_result:
            return SVN_VCS_TYPE
        raise Exception(f"Not found VCS in path: {self.project_path}")


def main():
    parser = argparse.ArgumentParser(description="Find vcs info of users work directories")
    parser.add_argument(
        "--users-file",
        required=True,
        help="Path for file with user credits. Example: --user_file_path users.json ",
    )
    parser.add_argument("--project-path", default="~/bw", help="Path for work directory on server")

    args = parser.parse_args()

    data_parser = VCSInfo(user_file_path=args.users_file.strip(), project_path=args.project_path.strip())
    response = data_parser.collect_data()
    print(json.dumps(response, indent=4))


if __name__ == "__main__":
    main()
