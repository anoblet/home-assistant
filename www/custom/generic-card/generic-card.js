import { css, html } from "https://unpkg.com/lit?module";
import { BaseElement } from "../base-element/base-element.js";
import baseStyle from "../base-style.js";

class GenericCard extends BaseElement {
  _defaultConfig = {
    title: "",
  };

  static get styles() {
    return [
      baseStyle,
      css`
        :host {
          background-color: var(--card-background-color);
          display: block;
        }

        #title {
          font-size: 2rem;
        }
      `,
    ];
  }

  render() {
    return html`
      <div class="grid grid-gap padding">
        <div id="title">${this.config.title}</div>
        <div id="content">
          <slot></slot>
        </div>
        <div id="footer"></div>
      </div>
    `;
  }
}
customElements.define("generic-card", GenericCard);
