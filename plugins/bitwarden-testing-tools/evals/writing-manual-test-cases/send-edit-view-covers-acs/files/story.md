# PM-39987: FE Share: Add item-type Send edit view in Send tab (expiry, deletion date, one-time toggle; item content read-only)

Create the Send tab detail/edit view for item-type Sends. Item content is read-only; only advanced options (expiry, deletion date, one-time toggle) are editable.

Scope:
- Display the shared item content in a read-only accordion (all shareable fields, no attachments/passkeys)
- Provide editable controls for expiry dropdown, deletion date picker, and one-time toggle
- Active links list with copy / edit / delete actions
- Save and delete buttons for updating or removing the Send

Acceptance Criteria:
- Given an item-type Send is open in the edit view, when the page loads, then the item content is displayed in a read-only accordion
- Given the user modifies the expiry dropdown or deletion date, when they click "Save", then the Send is updated server-side
- Given the one-time toggle is checked and saved, when the share link is accessed once, then it becomes inaccessible
- Given the user clicks "Delete", when confirmed, then the Send is deleted and the recipient link is invalidated
- Given the item content section, when the user attempts to edit a field, then the field is not editable or is visibly disabled
