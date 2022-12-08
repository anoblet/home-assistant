import { css, html } from "lit";
import { BaseElement } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";

class GridCard extends BaseElement {
  _defaultConfig = {
    style: {
    },
  };

  static get styles() {
    return [
      baseStyle,
      css`
        :host {
          display: grid;
        }
      `,
    ];
  }

  render() {
    return html`<slot></slot>`;
  }
}

customElements.define("grid-card", GridCard);
