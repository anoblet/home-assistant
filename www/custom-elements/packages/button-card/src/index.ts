import { css, html } from 'lit';
import { customElement } from 'lit/decorators.js';
import { BaseElement } from '../../base-element/src/index';
import baseStyle from '../../base-style/src/index';

@customElement('button-card')
export class ButtonCard extends BaseElement {
  static get styles() {
    return [baseStyle, css``];
  }

  render() {
    return html`<slot></slot>`;
  }
}
