import { css, html } from "https://unpkg.com/lit?module";
import { BaseElement } from "../base-element/base-element.js";
import baseStyle from "../base-style.js";

class IFrameCard extends BaseElement {
  _defaultConfig = {};

  _requiredConfig = ["url"];

  render() {
    return html`<iframe frameborder="0" src="${this.config.url}"></iframe>`;
  }

  static get styles() {
    return [
      baseStyle,
      css`
        :host {
          display: flex;
        }

        iframe {
          flex: 1;
        }
      `,
    ];
  }
}
customElements.define("iframe-card", IFrameCard);
