import { css, html } from "https://unpkg.com/lit?module";
import { BaseElement } from "../base-element/base-element.js";
import baseStyle from "../base-style.js";

class ButtonsCard extends BaseElement {
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

  static get styles() {
    return [
      baseStyle,
      css`
        #container {
          padding: var(--padding, 2rem);
        }

        #buttons {
          font-size: var(--font-size, 2rem);
          grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
        }
      `,
    ];
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error("You need to define an entity");
    }
    this.config = config;
  }

  // The height of your card. Home Assistant uses this to automatically
  // distribute all cards over the available columns.
  getCardSize() {
    return this.config.entities.length + 1;
  }

  _toggle() {
    this.hass.states[this.config.entity].state === "on"
      ? this._setSpeed("off")
      : this._setSpeed("auto");
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
