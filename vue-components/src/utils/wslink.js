class FakeWS {
  constructor(language, parent) {
    this.language = language;
    this.parent = parent;
  }

  close(code, reason) {
    this.parent.trame.trigger("trame_code_lang_server", [
      this.language,
      "close",
      { code, reason },
    ]);
  }

  send(data) {
    this.parent.trame.trigger("trame_code_lang_server", [
      this.language,
      "send",
      data,
    ]);
  }
}

export class WSLinkWebSocket {
  constructor(trame) {
    this.trame = trame;
    this.isopen = false;
    this.languagesWs = {};

    this.trame.client
      .getConnection()
      .getSession()
      .subscribe("trame.code.lang.server", ([event]) => {
        if (event.type == "close") {
          if (this.onclose) {
            this.closeConnections({
              code: event.code,
              reason: event.reason,
              type: "close",
            });
          }
        } else if (event.type == "message") {
          this.languagesWs[event.lang].onmessage({ data: event.data });
        } else if (event.type == "open") {
          if (this.onopen) {
            this.isopen = true;
            this.onopen();
          }
        }
      });
  }

  createLanguageWS(name) {
    const langWs = new FakeWS(name, this);
    this.languagesWs[name] = langWs;
    return langWs;
  }

  connectToLangServer() {
    if (!this.isopen) {
      const wss = Object.values(this.languagesWs);
      for (let i = 0; i < wss.length; i++) {
        const ws = wss[i];
        ws.onopen();
      }
    }
  }

  closeConnections(event) {
    const wss = Object.values(this.languagesWs);
    for (let i = 0; i < wss.length; i++) {
      const ws = wss[i];
      ws.onclose(event);
    }
  }
}
