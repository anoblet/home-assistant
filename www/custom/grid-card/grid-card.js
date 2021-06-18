import { css, html } from "https://unpkg.com/lit?module";
import { BaseElement } from "../base-element/base-element.js";
import baseStyle from "../base-style.js";

class GridCard extends BaseElement {
  _defaultConfig = {
    style: {
      gridGap: "",
      gridTemplateColumns: "",
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
