import { css, html } from "https://unpkg.com/lit?module";
import { BaseElement } from "../base-element/base-element.js";
import baseStyle from "../base-style.js";

class ButtonsCard extends BaseElement {
  static get styles() {
    return [
      baseStyle,
      css`
        #container {
          padding: var(--padding, 2rem);
        }

        #buttons {
          align-items: center;
          justify-content: center;
          grid-template-columns: repeat(auto-fit, 10rem);
        }
      `,
    ];
  }

  render() {
    const entity = this.hass.states[this.config.entity];
    return html`
      <ha-card>
        <div id="container">
          ${entity
            ? html`
                <div class="grid grid-gap" id="buttons">
                  ${entity.attributes.speed_list.map(
                    (speed) => html`
                      <mwc-button
                        @click=${this._onClick}
                        data-speed=${speed}
                        outlined
                      >
                        ${speed}
                      </mwc-button>
                    `
                  )}
                </div>
              `
            : html`<div class="not-found">Entity not found.</div>`}
        </div>
      </ha-card>
    `;
  }

  _setSpeed(speed) {
    this.hass.callService("fan", "set_speed", {
      entity_id: this.hass.states[this.config.entity].entity_id,
      speed,
    });
  }

  _onClick(e) {
    this._setSpeed(e.target.dataset.speed);
  }
}
customElements.define("buttons-card", ButtonsCard);
