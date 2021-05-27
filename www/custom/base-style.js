import { css } from "https://unpkg.com/lit?module";

export const baseStyle = css`
  :host {
    display: block;
  }

  hr {
    width: 100%;
  }

  .capitalize {
    text-transform: capitalize;
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

  .grid {
    display: grid;
  }

  .grid-gap {
    grid-gap: var(--padding, 1rem);
  }

  .none {
    display: none;
  }

  .padding {
    padding: var(--padding, 1rem);
  }

  .flex.space-between {
    justify-content: space-between;
  }
`;

export default baseStyle;
