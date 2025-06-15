import os
import uuid
from datetime import datetime, timedelta
import requests
from requests_ntlm2 import HttpNtlmAuth


class IterationBuilder:
    """Create PI and sprint iterations on Azure DevOps."""

    def __init__(self, username: str, password: str, domain: str = "aas") -> None:
        self.auth = HttpNtlmAuth(f"{domain}\\{username}", password)

    def _post_iteration(self, url: str, name: str, start: datetime, finish: datetime) -> requests.Response:
        data = {
            "name": name,
            "attributes": {
                "startDate": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "finishDate": finish.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        }
        print(url)
        print(data)
        response = requests.post(url, json=data, auth=self.auth)
        print(response)
        print(response.text)
        return response

    def create_pi(self, project: str, pi_name: str, start: datetime, finish: datetime) -> requests.Response:
        url = f"https://tfs.aas.com.sa/Medad/{project}/_apis/wit/classificationnodes/Iterations/?api-version=6.0"
        return self._post_iteration(url, pi_name, start, finish)

    def create_sprints(self, project: str, pi_name: str, start: datetime, finish: datetime) -> None:
        url = f"https://tfs.aas.com.sa/Medad/{project}/_apis/wit/classificationnodes/Iterations/{pi_name}?api-version=6.0"
        index = 1
        while index <= 6:
            if index == 6:
                name = f"IP iteration-{pi_name}"
            else:
                name = f"iteration {index}-{pi_name}"
            self._post_iteration(url, name, start, finish)
            index += 1
            if index == 2:
                start += timedelta(days=21)
                finish += timedelta(days=14)
            else:
                start += timedelta(days=14)
                finish += timedelta(days=14)


def main() -> None:
    username = os.environ.get("TFS_USERNAME", "ashabana")
    password = os.environ.get("TFS_PASSWORD", "Esraa@789321")

    builder = IterationBuilder(username, password)

    projects = [
        "Medad Artifact",
        "Medad Pass",
        "Medad Elearning Integration",
        "Medad TMP",
        "Medad MCS",
        "Medad SEP",
        "Medad BAB",
        "Medad Library Portal",
        "Medad LMS",
        "Medad ILS",
        "Medad IEP",
        "Medad DAR",
        "Medad core",
        "Medad Payment",
        "Medad Services",
        "Medad AI Gateway",
        "Medad Insights",
    ]
    projects.extend([
        "Medad discover",
        "Medad Edu Edge",
        "Medad Deposit",
        "Medad DevOps",
        "Architecture Team Space",
        "Medad Knowledge management",
        "Medad Releases",
        "Medad Customer Portal",
        "Enterprise AI",
        "UX Team Space",
    ])

    pi_name = "25-PI 3"
    pi_start = datetime(2025, 6, 1, 0, 0, 0)
    pi_finish = datetime(2025, 8, 28, 0, 0, 0)

    for project in projects:
        builder.create_pi(project, pi_name, pi_start, pi_finish)

    sprint_start = datetime(2025, 6, 1, 0, 0, 0)
    sprint_finish = datetime(2025, 6, 19, 0, 0, 0)
    for project in projects:
        builder.create_sprints(project, pi_name, sprint_start, sprint_finish)


if __name__ == "__main__":
    print(f"The random id using uuid1() is : {uuid.uuid1()}")
    main()
