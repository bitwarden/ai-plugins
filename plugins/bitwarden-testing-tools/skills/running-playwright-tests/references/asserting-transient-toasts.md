# Asserting transient toasts

Toasts can auto-dismiss in well under a second. To capture toast text reliably, read it from the live DOM: use `playwright-cli eval` to read the toast region's text right after the action, or `playwright-cli run-code` to wait for the toast region and return its text (arm the wait together with the triggering action so a short-lived toast is caught as it renders).

When the action causes a full page reload (the server-rendered Admin Portal — ASP.NET MVC), the new page fires the toast from an inline `document.ready` script, so the action's promise resolves before the toast renders and arming a wait alongside the action cannot catch it. For this post-back case, read the toast from the new page instead: assert its text from the inline `toastr.*("...")` call in the page source, or read the toast node on the new page's load.
