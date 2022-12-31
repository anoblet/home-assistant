export const applyStyle = (node, style) => {
  if ("adoptedStyleSheets" in document) {
    console.log(node);
    const sheets = node.shadowRoot.adoptedStyleSheets;
    node.shadowRoot.adoptedStyleSheets = [...sheets, style._styleSheet];
  } else {
    const styleNode = document.createElement("style");
    styleNode.textContent = style.cssText;
    node.shadowRoot.appendChild(styleNode);
  }
};
