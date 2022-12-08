export const setProperties = (properties, element) => {
  properties.forEach((property) => {
    element.style.setProperty(`--${property[0]}`, property[1]);
  });
};

(() => {
  const theme = JSON.parse(localStorage.getItem("theme"));

  if (!theme || !theme.properties) return;

  setProperties(Object.entries(theme.properties), document.documentElement);
})();
