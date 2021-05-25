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
          --padding: 2rem;

          background-color: var(--card-background-color);
          display: block;
        }

        #footer {
          display: contents;
        }

        #title {
          font-size: 2rem;
          text-align: center;
        }
      `,
    ];
  }

  render() {
    return html`
      <div class="grid grid-gap padding">
        <div id="title">${this.config.title}</div>
        <hr />
        <div id="content">
          <slot></slot>
        </div>
        <div id="footer"></div>
      </div>
    `;
  }
}
customElements.define("generic-card", GenericCard);
