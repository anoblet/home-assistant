import { css, html } from "https://unpkg.com/lit?module";
import { BaseElement } from "../base-element/base-element.js";
import baseStyle from "../base-style.js";

class HarmonyRemoteElement extends BaseElement {
  static get properties() {
    return {
      device: {},
    };
  }

  firstUpdated() {
    (async () => {
      const { device } = await import(`./devices/${this.config.device}.js`);
      this.device = device;
    })();
  }

  render() {
    return html`
      <div class="grid grid-gap" id="grid">
        ${this.device?.buttons.map(
          (button) =>
            html`
              <mwc-button
                @click=${this._onClick}
                data-command=${button.command}
                outlined
              >
                ${button.label}
              </mwc-button>
            `
        )}
      </div>
    `;
  }

  static get styles() {
    return [
      baseStyle,
      css`
        #grid {
          grid-template-columns: repeat(auto-fit, 10rem);
          justify-content: center;
          padding: 2rem;
        }
      `,
    ];
  }

  _onClick(e) {
    const command = e.target.dataset.command;

    command === "Activity"
      ? this.hass.callService("switch", "toggle", {
          entity_id: this.config.switch,
        })
      : this.hass.callService("remote", "send_command", {
          entity_id: this.config.entity_id,
          command: e.target.dataset.command,
          device: this.device.id,
        });
  }
}
customElements.define("harmony-remote", HarmonyRemoteElement);
