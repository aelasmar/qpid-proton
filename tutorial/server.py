#!/usr/bin/env python
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

from proton import Message
from proton_events import EventLoop, MessagingHandler

class Server(MessagingHandler):
    def __init__(self, host, address):
        super(Server, self).__init__()
        self.host = host
        self.address = address

    def on_start(self, event):
        self.conn = event.reactor.connect(self.host)
        self.receiver = self.conn.create_receiver(self.address)
        self.senders = {}
        self.relay = None

    def on_connection_opened(self, event):
        if event.connection.remote_offered_capabilities and 'ANONYMOUS-RELAY' in event.connection.remote_offered_capabilities:
            self.relay = self.conn.create_sender(None)

    def on_message(self, event):
        sender = self.relay
        if not sender:
            sender = self.senders.get(event.message.reply_to)
        if not sender:
            sender = self.conn.create_sender(event.message.reply_to)
            self.senders[event.message.reply_to] = sender
        sender.send_msg(Message(address=event.message.reply_to, body=event.message.body.upper()))

try:
    EventLoop(Server("localhost:5672", "examples")).run()
except KeyboardInterrupt: pass


