// Small client-side helpers for the SmartPark page.
document.querySelectorAll(".checkout-form").forEach(form => {
  form.addEventListener("submit", event => {
    const hours = Number(form.querySelector('input[name="hours"]').value);
    if (!Number.isFinite(hours) || hours < 1) {
      event.preventDefault();
      alert("Enter parking duration of at least 1 hour.");
    }
  });
});

const plateInput = document.getElementById("licenseNumber");
if (plateInput) {
  plateInput.addEventListener("input", () => {
    plateInput.value = plateInput.value.toUpperCase().replace(/\s+/g, "");
  });
}
