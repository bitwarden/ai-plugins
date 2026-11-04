# Asserting transient toasts

A toast can appear only after the action's request finishes and dismiss a few seconds later, so a read in a later command can miss it. Perform the action, read the toast, and take the step's screenshot in one `playwright-cli run-code` call. It clicks, waits up to 30 seconds for the expected text, waits for the toast's fade-in to finish, takes the full scrollable view the same way the screenshot policy does, and returns the text:

```
playwright-cli run-code "async page => { await page.locator('<selector>').click(); const toast = page.getByText('<expected toast text>').first(); await toast.waitFor({ timeout: 30000 }); await page.waitForFunction(el => { let o = 1; for (let n = el; n; n = n.parentElement) o *= Number(getComputedStyle(n).opacity); return o === 1; }, await toast.elementHandle(), { timeout: 2000 }).catch(() => {}); const height = await page.evaluate(() => Math.min(8000, Math.max(innerHeight, document.documentElement.scrollHeight, ...[...document.querySelectorAll('*')].filter(e => /auto|scroll/.test(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight).map(e => Math.ceil(e.getBoundingClientRect().top + e.scrollHeight))))); const viewport = page.viewportSize(); await page.setViewportSize({ width: viewport.width, height }); await page.screenshot({ path: '<artifacts-output-dir>/screenshots/<name>.png', fullPage: true }); await page.setViewportSize(viewport); return await toast.innerText(); }"
```

Playwright counts a fully transparent element as visible, so the opacity wait keeps the screenshot from catching the toast mid-fade. The screenshot path is absolute and named per the screenshot policy after the toast assertion step, and it is that step's `screenshot`.

Use this call for a step that begins `Assert: toast from step <N>:` together with step N, for any other toast assertion that directly follows an action, and for a setup step that expects a toast. If the wait times out, the call stops before the screenshot: the toast is absent and the assertion fails, so take the step's screenshot of the page as it stands with the usual commands.

When the action causes a full page reload (the server-rendered Admin Portal — ASP.NET MVC), the new page fires the toast from an inline `document.ready` script, so the action's promise resolves before the toast renders and arming a wait alongside the action cannot catch it. For this post-back case, read the toast from the new page instead: assert its text from the inline `toastr.*("...")` call in the page source, or read the toast node on the new page's load.
