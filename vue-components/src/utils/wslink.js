class ReaderWriter {
  constructor(language, parent) {
    console.log("lang::new", language);
    this.language = language;
    this.parent = parent;
    this.callback = null;
    this.client = null;
    this.closeCallback = null;
    this.errorCallback = null;
  }

  listen(callback) {
    console.log("lang::listen");
    this.callback = callback;
  }

  onmessage(msg) {
    console.log("lang::onmessage", msg);
    try {
      const data = JSON.parse(msg);
      this.callback(data);
    } catch (err) {
      console.error("LangServer::onmessage", err);
    }
  }

  write(msg) {
    console.log("lang::write", msg);
    const content = JSON.stringify(msg);
    this.parent.trame.trigger("trame_code_lang_server", [
      this.language,
      "send",
      content,
    ]);
  }

  stop() {
    console.log("lang::stop");
    this?.client.stop();
  }

  onClose(fn) {
    this.closeCallback = fn;
  }

  onError(fn) {
    this.errorCallback = fn;
  }
}

export class WSLinkWebSocket {
  constructor(trame) {
    console.log("new WSLinkWebSocket", !!trame);
    this.trame = trame;
    this.isopen = false;
    this.languagesIO = {};

    this.trame.client
      .getConnection()
      .getSession()
      .subscribe("trame.code.lang.server", ([event]) => {
        if (event.type == "close") {
          console.log("closing", event);
          if (this.onclose) {
            this.closeConnections();
          }
        } else if (event.type == "message") {
          this.languagesIO[event.lang].onmessage(event.data);
        } else if (event.type == "open") {
          if (this.onopen) {
            this.isopen = true;
          }
        }
      });
  }

  createLanguageIO(name) {
    const langIO = new ReaderWriter(name, this);
    this.languagesIO[name] = langIO;
    return langIO;
  }

  closeConnections() {
    const langsIO = Object.values(this.languagesIO);
    for (let i = 0; i < langsIO.length; i++) {
      const lang = langsIO[i];
      lang.stop();
    }
  }
}
