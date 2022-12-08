import { css } from "lit";

export const baseStyle = css`
  :host {
    box-sizing: var(--box-sizing, border-box);
    display: flex;
    flex: 1;
    flex-direction: column;
  }

  ha-card {
    display: flex;
    flex: 1;
    flex-direction: column;
  }

  ha-card .entities {
    display: flex;
    flex: 1;
    flex-direction: column;
  }

  hr {
    border-color: var(--hr-border-color);
    height: max-content;
    margin-block-start: 0;
    margin-block-end: 0;
    width: 100%;
  }

  hui-button-card,
  hui-entities-card,
  hui-glance-card,
  hui-light-card {
    display: block;
  }

  .absolute {
    position: absolute;
    inset: 0;
  }

  .capitalize {
    text-transform: capitalize;
  }

  .center {
    align-items: center;
    display: flex;
    justify-content: center;
    line-height: 1rem;
  }

  .columns {
    grid-template-columns: repeat(auto-fit, minmax(512px, 1fr));
  }

  .contents {
    display: contents;
  }

  .flex.center {
    align-items: center;
    justify-content: center;
  }

  .flex {
    display: flex;
  }

  .full-height {
    height: 100%;
  }

  .gap {
    gap: var(--gap, 1rem);
  }

  .golden-ratio {
    aspect-ratio: 1.618;
  }

  .grid {
    display: grid;
  }

  .grow {
    flex-grow: 1;
  }

  .height-100 {
    height: 100%;
  }

  .none {
    display: none;
  }

  .padding {
    padding: var(--padding, 1rem);
  }

  .relative {
    position: relative;
  }

  .flex.space-between {
    justify-content: space-between;
  }

  .two-column {
    grid-template-columns: repeat(2, 1fr);
  }

  mini-graph-card {
    position: absolute;
    inset: 0;
  }
`;

const center = `
  display: flex;
  justify-content: center;
  align-items: center;
`;

export default baseStyle;
