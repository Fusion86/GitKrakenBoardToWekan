import click
import csv
from dataclasses import dataclass
from typing import Any, List
import requests


@dataclass
class GloBoardEntry:
    name: str
    column: str
    description: str
    labels: str
    # TODO: Assignees,Due Date,Milestone


def load_glo_csv(csv_file):
    entries: List[GloBoardEntry] = []

    with open(csv_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")

        # Row with the column names, which we ignore.
        _ = next(csv_reader)

        for row in csv_reader:
            labels = row[3].split(",") if len(row[3]) > 0 else []
            entry = GloBoardEntry(*row[0:3], labels)
            entries.append(entry)

    return entries


class Wekan:
    def __init__(self, api_url) -> None:
        self.api_url = api_url
        self._token = None

    def login(self, username, password):
        data = {"username": username, "password": password}
        res = requests.post(self.api_url + "/users/login", json=data)

        if res.ok:
            self._token = res.json()["token"]

        return res.ok

    def get_current_user(self):
        return self._api_req("GET", "/api/user")

    def new_board(
        self,
        title,
        owner,
        ownerIsAdmin=True,
        isActive=True,
        disableComments=False,
        onlyEnableComments=False,
        permission="private",
        color="belize",
    ):
        data = {
            "title": title,
            "owner": owner,
            "isAdmin": ownerIsAdmin,
            "isActive": isActive,
            "isNoComments": disableComments,
            "isCommentOnly": onlyEnableComments,
            "permission": permission,
            "color": color,
        }
        return self._api_req("POST", "/api/boards", data)

    def get_all_swimlanes(self, board_id: str):
        return self._api_req("GET", f"/api/boards/{board_id}/swimlanes")

    def get_board_lists(self, board_id: str):
        return self._api_req("GET", f"/api/boards/{board_id}/lists")

    def create_board_list(self, board_id: str, list_name: str):
        data = {"title": list_name}
        return self._api_req("POST", f"/api/boards/{board_id}/lists", data)

    def create_card(
        self,
        board_id: str,
        list_id: str,
        title: str,
        author_id: str,
        description: str,
        swimlane_id: int,
    ):
        data = {
            "authorId": author_id,
            "title": title,
            "description": description,
            "swimlaneId": swimlane_id,
        }
        return self._api_req(
            "POST", f"/api/boards/{board_id}/lists/{list_id}/cards", data
        )

    def create_label(self, board_id: str, name: str):
        data = {"label": {"color": "silver", "name": name}}
        label_id = self._api_req("PUT", f"/api/boards/{board_id}/labels", data)

        if len(label_id) == 0:
            raise Exception("Couldn't create label, does it already exist?")
        return label_id

    def set_card_labels(
        self, board_id: str, list_id: str, card_id: str, labels: List[str]
    ):
        data = {"labelIds": labels}
        return self._api_req(
            "PUT", f"/api/boards/{board_id}/lists/{list_id}/cards/{card_id}", data
        )

    def _api_req(self, method: str, path: str, json_data: Any = None):
        headers = {}

        if self._token is not None:
            headers["Authorization"] = "Bearer " + self._token

        res = requests.request(
            method, self.api_url + path, json=json_data, headers=headers
        )

        if not res.ok:
            raise Exception(f"Status code '{res.status_code}' is not ok.")

        data = res.json()

        if "error" in data:
            raise Exception(f"{data['message']}")

        return res.json()


@click.command()
@click.option("--url", required=True, help="Wekan instance url.")
@click.option(
    "-u",
    "--user",
    "username",
    required=True,
    help="User which will own the board and all the cards.",
)
@click.option("-p", "--pass", "password", required=True, help="User's password.")
@click.option(
    "-b", "--board", "board_name", required=True, help="The name for the board."
)
@click.option(
    "-f",
    "--file",
    "csv_file",
    required=True,
    help="Which GitKraken Boards CSV file to import.",
)
def cli(url, username, password, board_name, csv_file):
    """Shitty script to import your GitKraken boards into your own Wekan instance."""

    cards = load_glo_csv(csv_file)

    api = Wekan(url)
    api.login(username, password)
    user_id = api.get_current_user()["_id"]
    board_id = api.new_board(board_name, user_id)["_id"]

    # Use 'Default' swimlane
    swimlane_id = api.get_all_swimlanes(board_id)[0]["_id"]

    column_ids = {}
    label_ids = {}

    for card in cards:
        if card.column in column_ids:
            column_id = column_ids[card.column]
        else:
            print(f"Creating column '{card.column}'")
            column_id = api.create_board_list(board_id, card.column)["_id"]
            column_ids[card.column] = column_id

        print(f"Creating card: [{card.column}] {card.name}")
        card_id = api.create_card(
            board_id, column_id, card.name, user_id, card.description, swimlane_id
        )["_id"]

        label_ids_to_add = []

        for label in card.labels:
            if label in label_ids:
                label_id = label_ids[label]
            else:
                print(f"Creating label '{label}'")
                label_id = api.create_label(board_id, label)
                label_ids[label] = label_id
            label_ids_to_add.append(label_id)

        if len(label_ids_to_add) > 0:
            print(f"Adding labels '{','.join(card.labels)}' to card")
            api.set_card_labels(board_id, column_id, card_id, label_ids_to_add)


if __name__ == "__main__":
    cli()
