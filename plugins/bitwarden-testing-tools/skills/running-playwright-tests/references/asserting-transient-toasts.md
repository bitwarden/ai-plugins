# Asserting transient toasts

A toast can appear only after the action's request finishes and dismiss a few seconds later, so a read in a later command can miss it. Perform the action and read the toast in one `playwright-cli run-code` call that clicks, waits up to 30 seconds for the expected text, and returns it:

```
playwright-cli run-code "async page => { await page.locator('<selector>').click(); const toast = page.getByText('<expected toast text>').first(); await toast.waitFor({ timeout: 30000 }); return await toast.innerText(); }"
```

Use this call for a step that begins `Assert: toast from step <N>:` together with step N, for any other toast assertion that directly follows an action, and for a setup step that expects a toast. If the wait times out, the toast is absent and the assertion fails.

When the action causes a full page reload (the server-rendered Admin Portal — ASP.NET MVC), the new page fires the toast from an inline `document.ready` script, so the action's promise resolves before the toast renders and arming a wait alongside the action cannot catch it. For this post-back case, read the toast from the new page instead: assert its text from the inline `toastr.*("...")` call in the page source, or read the toast node on the new page's load.
