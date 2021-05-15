import { css } from "https://unpkg.com/lit?module";

export default css`
  .capitalize {
    text-transform: capitalize;
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
    grid-gap: 1rem;
  }

  .padding {
    padding: var(--container-padding, 1rem);
  }

  .flex.space-between {
    justify-content: space-between;
  }
`;
