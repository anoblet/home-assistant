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

  firstUpdated() {
    this.config.style.map((property) => {
      for (const key in property) {
        this.style.setProperty(key, property[key]);
      }
    });
  }

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
