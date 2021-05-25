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
        :host {
          padding: 1rem;
        }

        #grid {
          grid-template-columns: repeat(auto-fit, minmax(7.5rem, 1fr));
        }
      `,
    ];
  }

  _onClick(e) {
    this.hass.callService("remote", "send_command", {
      entity_id: this.config.entity_id,
      command: e.target.dataset.command,
      device: this.device.id,
    });
  }
}
customElements.define("harmony-remote", HarmonyRemoteElement);
