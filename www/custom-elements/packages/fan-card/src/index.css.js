import { css } from "lit";

export const style = css`
  :host {
    font-size: var(--state-font-size, 1rem);
  }

  #attributes {
    grid-template-columns: min-content 1fr;
  }

  #attributes > label,
  #attributes > span {
    white-space: nowrap;
  }

  #attributes > label::after {
    content: ":";
  }

  #buttons {
    align-items: center;
    justify-content: center;
    grid-template-columns: repeat(auto-fit, 10rem);
  }

  #friendly_name {
    font-size: var(--state-font-size, 2rem);
    line-height: 2rem;
  }

  .full-row {
    grid-column: 1/-1;
  }
`;
