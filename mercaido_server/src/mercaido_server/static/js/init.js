// SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
//
// SPDX-License-Identifier: MIT

document.addEventListener("DOMContentLoaded", () => {
  const fabs = document.querySelectorAll(".fixed-action-btn");
  M.FloatingActionButton.init(fabs, {
    hoverEnabled: true,
  });

  const selects = document.querySelectorAll("select");
  M.FormSelect.init(selects, {
    // specify options here
  });

  const rightSidenavs = document.querySelectorAll("aside.sidenav.nav-right");
  M.Sidenav.init(rightSidenavs, {
    edge: "right",
  });

  const pwToggles = document.querySelectorAll(
    'i.suffix + input[type="password"]',
  );

  pwToggles.forEach((toggle) => {
    toggle.previousElementSibling.addEventListener("click", () => {
      const currentType = toggle.getAttribute("type");
      toggle.setAttribute(
        "type",
        currentType === "password" ? "text" : "password",
      );
      toggle.previousElementSibling.innerText =
        currentType === "password" ? "visibility" : "visibility_off";
    });
  });

  const collapsibles = document.querySelectorAll(".collapsible");
  M.Collapsible.init(collapsibles, {});

  const autocompletes = document.querySelectorAll(".autocomplete");

  autocompletes.forEach((autocomplete) => {
    const items = JSON.parse(autocomplete.dataset.options);
    const attributeValueInputId = autocomplete.id.substring(
      0,
      autocomplete.id.length - 5,
    );
    const attributeValueInput = document.querySelector(
      `#${attributeValueInputId}`,
    );
    M.Autocomplete.init(autocomplete, {
      minLength: 0,
      data: items,
      onAutocomplete: (entries) => {
        console.log(entries);
        if (entries.length > 0) {
          attributeValueInput.value = entries[0].id;
        }
      },
    });
  });
});
