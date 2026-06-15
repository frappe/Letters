// Redirect the Letters workspace to the Letter Builder Vue dashboard.
// app_include_js injects this into every Desk page; it's lightweight —
// the redirect only fires when the route is exactly ["letters"].
$(document).on("page-change", function () {
  var route = frappe.get_route();
  if (route && route[0] === "letters") {
    frappe.set_route("letter-builder");
  }
});
