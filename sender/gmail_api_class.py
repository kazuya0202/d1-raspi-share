from __future__ import annotations

import base64
import os.path
from pathlib import Path
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any

from bs4 import BeautifulSoup
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


@dataclass(init=False, frozen=True)
class ResponseFlags(Enum):
    NO_INBOX = auto()
    SKIP_BY_ALREADY_SENT = auto()
    SKIP_BY_REGARDLESS = auto()
    WILL_SEND_START = auto()  # 発令
    WILL_SEND_END = auto()  # 解除
    INIT_STATUS = auto()
    EXIST_MESSAGES = auto()


@dataclass
class GmailRequest:
    SCOPES: list[str]
    prev_sent_timestamp: datetime = field(init=False)
    level: int = field(init=False, default=-1)
    response_flag: ResponseFlags = field(init=False, default=ResponseFlags.INIT_STATUS)

    creds: Any = field(init=False, default=None)
    service: Any = field(init=False)
    messages: Any = field(init=False)

    def __post_init__(self) -> None:
        # 初回実行時から2時間前（厳密には1時間前でOK）にセット
        # => 過去1時間前からgmailで送られたメッセージを無視しないため
        self.prev_sent_timestamp = datetime.today() - timedelta(hours=2)
        self.set_creds()

        # build API service
        self.service = build("gmail", "v1", credentials=self.creds)

        # regex
        self.vigilance_level_pattern = re.compile("レベル[0-9０-９]")
        # translate (replace)
        z_digit = "１２３４５６７８９０"
        h_digit = "1234567890"
        self.z2h_digit = str.maketrans(z_digit, h_digit)

        # オブジェクトをキーにできないため、valueでint型をキーとする
        self.response_pair = {
            ResponseFlags.NO_INBOX.value: "過去1時間で受信したメールがありません。",
            ResponseFlags.SKIP_BY_ALREADY_SENT.value: "すでに送信しているためスキップします。",
            ResponseFlags.SKIP_BY_REGARDLESS.value: "災害情報と関係のないメールのためスキップします。",
            ResponseFlags.WILL_SEND_START.value: "今から送信を行います。（警戒情報の発令）",
            ResponseFlags.WILL_SEND_END.value: "今から送信を行います。（警戒情報の解除）",
            ResponseFlags.INIT_STATUS.value: "APIからのレスポンスを受け取っていません。",
            ResponseFlags.EXIST_MESSAGES.value: "受信したメッセージがあります。",
        }

    def get_status(self) -> str:
        status_msg = self.response_pair[self.response_flag.value]
        if self.response_flag.value in [ResponseFlags.SKIP_BY_ALREADY_SENT.value]:
            status_msg = f"{status_msg} (timestamp: {self.prev_sent_timestamp})"
        return status_msg

    def _set_flag(self, flag: ResponseFlags) -> None:
        self.response_flag = flag

    def _set_level(self, level: int) -> None:
        self.level = level

    def fetch_messages(self):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        try:
            # Call the Gmail API
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            if not labels:
                print("No labels found.")
                return

            # request a list of all the messages
            # INBOX: 受信箱のみ（デバッグ中，下書きからも判定が存在してしまったため）
            result = (
                self.service.users()
                .messages()
                .list(userId="me", labelIds="INBOX", q="newer_than:1h")
                .execute()
            )
            self.messages = result.get("messages")
            # 一致するクエリから全てのメールを配列で返す
            if self.messages is None:
                self._set_flag(ResponseFlags.NO_INBOX)
            else:
                self._set_flag(ResponseFlags.EXIST_MESSAGES)
        except HttpError as e:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {e}")
        except RefreshError as e:
            print(f"An error occurred: {e}")

    def check_messages(self, keyword: str) -> None:
        # メールを一件ずつ見る
        for msg in self.messages:
            info = (
                self.service.users().messages().get(userId="me", id=msg["id"]).execute()
            )
            # Use try-except to avoid any Errors
            try:
                # Get value of 'payload' from dictionary 'txt'
                payload = info["payload"]
                headers = payload["headers"]

                subject = ""
                sender = ""
                date = ""
                # Look for Subject and Sender Email in the headers
                for d in headers:
                    if d["name"] == "Subject":
                        subject = d["value"]
                    if d["name"] == "From":
                        sender = d["value"]
                    if d["name"] == "Date":
                        date = d["value"]

                # The Body of the message is in Encrypted format. So, we have to decode it.
                # Get the data and decode it with base 64 decoder.
                parts = payload.get("parts")[0]
                data = parts["body"]["data"]
                data = data.replace("-", "+").replace("_", "/")
                decoded_data = base64.b64decode(data)

                # Now, the data obtained is in lxml. So, we will parse
                # it with BeautifulSoup library
                soup = BeautifulSoup(decoded_data, "lxml")
                # body = soup.body()
                body = soup.select("body")
                body_str = str(body)
                strip_body_str = (
                    body_str.replace(" ", "").replace("　", "").replace("¥n", "")
                )

                if keyword in subject or keyword in strip_body_str:
                    date_str_strip = date[date.find(",") + 1 : -5].strip()
                    date_datetime = datetime.strptime(
                        date_str_strip, "%d %b %Y %H:%M:%S"
                    )
                    if self.prev_sent_timestamp >= date_datetime:
                        self._set_flag(ResponseFlags.SKIP_BY_ALREADY_SENT)
                        return

                    self.prev_sent_timestamp = date_datetime  # 最新のものに更新
                    # print("update", date_datetime, self.prev_sent_timestamp)
                    find_list = self.vigilance_level_pattern.findall(strip_body_str)
                    if len(find_list) > 0:
                        level = int(str(find_list[0]).translate(self.z2h_digit)[-1])
                        self._set_level(level)
                        self._set_flag(ResponseFlags.WILL_SEND_START)

                        # 2通目以降も確認してしまう
                        # => 複数が土砂災害だった場合
                        #    最新のメールでprev_sentを更新して，古いメールと比較するからalreadyになってしまう
                        # => 土砂災害関連で最新（一番初めにここにきた）のメールでreturn
                        #    （ループの終了でもいいにはいいけど見づらい）
                        return

                    # 「土砂災害」のキーワードがある前提
                    elif "解除" in subject or "解除" in strip_body_str:
                        self._set_flag(ResponseFlags.WILL_SEND_END)
                        # 解除の場合も，一番初めにきた最新メールのみ見る
                        return

                else:
                    self._set_flag(ResponseFlags.SKIP_BY_REGARDLESS)

                # Printing the subject, sender's email and message
                # print("Subject: ", subject)
                # print("From: ", sender)
                # print("Message: ", body)
                # print("\n")
            except Exception as e:
                print(e)

    def set_creds(self) -> None:
        file_dir = Path(__file__).parent

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(file_dir / "token.json"):
            creds = Credentials.from_authorized_user_file(
                file_dir / "token.json", self.SCOPES
            )
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    file_dir / "credentials.json", self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(file_dir / "token.json", "w") as token:
                token.write(creds.to_json())

        self.creds = creds


if __name__ == "__main__":
    # 変数名は変更不可（ライブラリの方で参照されてるっぽいから、グローバルにアクセスできる必要がある）
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    gr = GmailRequest(SCOPES)
    keyword = "土砂災害"

    for _ in range(3):
        gr.fetch_messages()
        if gr.response_flag.value != ResponseFlags.NO_INBOX.value:
            gr.check_messages(keyword)

        print(gr.response_flag)
        print(gr.get_status())
        time.sleep(3)
