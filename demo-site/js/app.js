(function () {
  function wireTrackingButtons() {
    document.querySelectorAll("[data-track-event]").forEach(function (button) {
      button.addEventListener("click", function () {
        const eventName = button.getAttribute("data-track-event");
        const sourceType = button.getAttribute("data-source") || "js";
        const payload = {
          element_id: button.id || null,
          label: button.innerText,
          page: window.location.pathname
        };

        if (sourceType === "image") {
          window.myPixel.pixel(eventName);
        } else {
          window.myPixel.track(eventName, payload);
        }
      });
    });
  }

  window.addEventListener("DOMContentLoaded", wireTrackingButtons);
})();
