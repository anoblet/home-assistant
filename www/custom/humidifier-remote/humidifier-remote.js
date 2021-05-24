import { css, html } from "https://unpkg.com/lit?module";
import { BaseElement } from "../base-element/base-element.js";
import baseStyle from "../base-style.js";
import { buttons } from "./buttons.js";

class HumidifierRemoteElement extends BaseElement {
  render() {
    return html`
      ${buttons.map(
        (button) =>
          html`
            <mwc-button @click=${this._onClick} data-command=${button.command}>
              ${button.label}
            </mwc-button>
          `
      )}
    `;
  }

  static get styles() {
    return [baseStyle, css``];
  }

  _onClick(e) {}
}
customElements.define("humidifier-remote", HumidifierRemoteElement);
