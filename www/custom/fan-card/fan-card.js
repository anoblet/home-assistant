import { css, html, nothing } from "https://unpkg.com/lit?module";
import { BaseElement } from "../base-element/base-element.js";
import baseStyle from "../base-style.js";

class FanCard extends BaseElement {
  _defaultConfig = {
    show: {
      friendly_name: true,
    },
  };

  _requiredConfig = ["entity"];

  render() {
    const entity = this.hass.states[this.config.entity];
    return html`
      <div class="grid grid-gap padding" id="container">
        <div class="center flex padding" id="friendly_name">
          ${entity.attributes.friendly_name}
        </div>
        <div class="grid grid-gap padding" id="attributes">
          <label>Air Quality</label>
          <span class="capitalize">${entity.attributes.air_quality}</span>
          <div class="full-row graph">
            <slot name="quality_graph"></slot>
          </div>
          <label>Speed</label>
          <span class="capitalize">
            ${entity.state === "off"
              ? html`Off`
              : html`${entity.attributes.speed}`}
          </span>
          <div class="full-row">
            <slot name="speed_graph"></slot>
          </div>
          <label>Filter Life</label>
          <span class="capitilize">${entity.attributes.filter_life}%</span>
        </div>
        <buttons-card .config=${this.config} .hass=${this.hass}></buttons-card>
        ${this.cards ? this.cards.map((card) => html`${card}`) : nothing}
      </div>
    `;
  }

  static get styles() {
    return [
      baseStyle,
      css`
        :host {
          font-size: var(--state-font-size, 1rem);
        }

        #attributes {
          grid-template-columns: min-content auto;
        }

        #attributes > label,
        #attributes > span {
          white-space: nowrap;
        }

        #attributes > label::after {
          content: ":";
        }

        #container {
          padding: 2rem;
        }

        #friendly_name {
          font-size: var(--state-font-size, 2rem);
          line-height: 2rem;
        }

        .full-row {
          grid-column: 1/-1;
        }

        .graph {
          /* height: 10rem; */
        }
      `,
    ];
  }
}
customElements.define("fan-card", FanCard);
