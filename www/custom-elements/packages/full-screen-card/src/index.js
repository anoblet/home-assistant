import { css, html } from "lit";
import { BaseElement } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";

class FullScreenCard extends BaseElement {
  _defaultConfig = {};

  static get styles() {
    return [
      baseStyle,
      css`
        :host {
          position: absolute;
          inset: 0;
        }
      `,
    ];
  }

  render() {
    return html`<slot></slot>`;
  }
}

customElements.define("full-screen-card", FullScreenCard);
