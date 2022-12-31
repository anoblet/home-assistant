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
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
        }
      `,
    ];
  }

  render() {
    return html`<slot></slot>`;
  }
}

customElements.define("full-screen-card", FullScreenCard);
