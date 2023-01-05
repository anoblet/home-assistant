// import "@material/mwc-button";
// import "@material/mwc-select";
// import "@material/mwc-textfield";
import { css, html } from "lit";
import { repeat } from "lit-html/directives/repeat.js";
import { customElement, property } from "lit/decorators.js";
import { BaseElement } from "../../base-element/src";
import baseStyle from "../../base-style/src";
import { themes } from "../themes";
import "./register-theme";
import { setProperties } from "./register-theme";

@customElement("custom-theme-card")
export class CustomThemeCard extends BaseElement {
  @property({ type: Object }) theme: any;

  static get styles() {
    return [baseStyle, css``];
  }

  constructor() {
    super();

    this.theme = this.loadTheme();

    this.theme = this.theme || themes[0];
  }

  render() {
    return html`
      <div class="padding">
        <div class="gap grid">
          <mwc-select @selected=${this.onSelected}>
            ${repeat(
              themes,
              (theme: any) => html`
                <mwc-list-item>${theme.name}</mwc-list-item>
              `
            )}
          </mwc-select>
          <hr />
          <div class="gap grid two-column">
            ${repeat(
              Object.entries(this.theme.properties),
              (property: any, index) => html`
                <mwc-textfield
                  data-index=${index}
                  label="Name"
                  name="name"
                  outlined
                  value=${property[0]}
                  @change=${this.change}
                ></mwc-textfield>
                <mwc-textfield
                  data-index=${index}
                  label="Value"
                  name="value"
                  outlined
                  value="${property[1]}"
                  @change=${this.change}
                ></mwc-textfield>
              `
            )}
          </div>
          <div class="columns gap grid">
            <mwc-button
              label="Add Property"
              @click=${this.add}
              outlined
            ></mwc-button>
            <mwc-button label="Save" @click=${this.save} outlined></mwc-button>
          </div>
        </div>
      </div>
    `;
  }

  updated(changedProperties) {
    console.log("updated");

    super.updated(changedProperties);

    if (changedProperties.has("theme")) {
      setProperties(
        Object.entries(this.theme.properties),
        document.documentElement
      );
    }
  }

  add() {
    const theme = { ...this.theme };

    console.log(this.theme);

    this.theme.properties.push({ name: "", value: "" });

    this.requestUpdate("theme", theme);
  }

  apply() {
    setProperties(this.theme.properties, document.documentElement);
  }

  change(event) {
    const theme = { ...this.theme };

    this.theme.properties[event.target.dataset.index][event.target.name] =
      event.target.value;

    this.requestUpdate("theme", theme);
  }

  loadTheme() {
    const theme = localStorage.getItem("theme");

    if (theme) return JSON.parse(theme);
  }

  onSelected(event: any) {
    console.log("selected");

    const theme = this.theme;

    this.theme = { ...themes[event.detail.index] };

    // this.requestUpdate("theme", theme);
  }

  save() {
    setProperties(this.theme.properties, document.documentElement);

    localStorage.setItem("theme", JSON.stringify(this.theme));
  }
}
