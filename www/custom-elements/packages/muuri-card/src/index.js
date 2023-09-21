import { css, html } from "lit";
import { BaseElement } from "../../base-element/src/index";
// import "muuri";

class MuuriCard extends BaseElement {
  _defaultConfig = {
    style: {
    },
  };

  static get styles() {
    return [
      css`
        :host {
          display: block;
        }

        :host[hidden] {
          display: none;
        }

        .muuri {
          position: relative;
        }
      `,
    ];
  }

  render() {
    return html`
      <div class="muuri"><slot></slot></div>
    `;
  }

  firstUpdated() {
    // console.log(muuri);

    // this._muuri = new Muuri(this.shadowRoot.querySelector(".muuri"));
  }
}

customElements.define("muuri-card", MuuriCard);
