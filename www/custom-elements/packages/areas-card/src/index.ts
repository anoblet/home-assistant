import { css, html } from "lit";
import { customElement, state } from "lit/decorators.js";
import "../../area-card/src/index";
import { BaseElement } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";

@customElement("areas-card")
export class AreasCard extends BaseElement {
  @state() __areas = [];
  @state() __currentArea: number;
  @state() path;

  static get styles() {
    return [
      baseStyle,
      css`
        li {
          display: flex;
          list-style-type: none;
        }

        ul {
          display: grid;
          flex: 1;
          gap: 1rem;
          grid-template-columns: repeat(auto-fit, minmax(25rem, 1fr));
          margin-block-start: 0;
          padding-inline-start: 0;
        }

        .area {
          border: 1px solid var(--primary-color);
          border-radius: 1rem;
          display: flex;
          flex: 1;
        }
      `,
    ];
  }

  render() {
    return html`
      <span>${this.path}</span>
      ${!this.__currentArea
        ? html`
            <ul>
              ${this.__areas.map(
                (area, index) => html`
                  <li>
                    <div
                      @click=${this.__setArea}
                      class="area center"
                      data-index=${index}
                    >
                      ${area.name}
                    </div>
                    <div></div>
                  </li>
                `
              )}
            </ul>
          `
        : html`<area-card .hass=${this.hass} id=${this.__currentArea}></area-card>`}
    `;
  }

  protected firstUpdated(
    _changedProperties: Map<string | number | symbol, unknown>
  ): void {
    super.firstUpdated(_changedProperties);

    this.path = this.__path;

    this.__getAreas();
  }

  async __getAreas() {
    this.__areas = (
      await this.hass.callWS({
        type: "config/area_registry/list",
      })
    ).sort((a, b) => a.name.localeCompare(b.name));

    console.log(this.__areas);
  }

  get __path() {
    return localStorage.getItem("areas-card-path");
  }

  set __path(path) {
    localStorage.setItem("areas-card-path", path);
  }

  async __setArea(event) {
    const area = this.__areas[event.currentTarget.dataset.index];
    this.__path = area.name;
    this.__currentArea = area.area_id;
  }
}
