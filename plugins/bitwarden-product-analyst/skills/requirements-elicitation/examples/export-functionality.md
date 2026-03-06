# Example: Export Functionality

**Context**: Feature request to "add export functionality"

**Requirements Elicitation Process**:

1. **Functional Requirements** (extract):
   - System shall allow users to export vault data
   - [QUESTION: What data? All items, selected items, specific vaults?]
   - [QUESTION: What formats? JSON, CSV, encrypted export?]

2. **Non-Functional Requirements** (identify):
   - **Performance**: Export operation shall complete within 30 seconds for vaults with <10,000 items
   - [QUESTION: What's the max vault size to support?]
   - **Usability**: Export progress shall be visible to user
   - [QUESTION: Should this be cancellable?]

3. **Security Requirements** (apply Bitwarden principles):
   - **Data Classification**: This is Vault Data export (P05: Controlled Access)
   - **User Consent**: Explicit user confirmation required (data exporting nullifies guarantees)
   - **Format Security**:
     - Unencrypted export → Warning about data leaking risk
     - Encrypted export → Key derivation and storage requirements
   - [QUESTION: Should we limit export frequency or add audit logging?]

4. **Constraints** (identify):
   - **Technical**: Must work across all clients (web, desktop, mobile, CLI)
   - **Compatibility**: Export format must be importable by all Bitwarden clients
   - **Storage**: Large exports may need temporary disk space (how much?)

5. **Acceptance Criteria** (define):
   - User can trigger export from vault menu
   - User receives clear warning about security implications
   - User can select export format
   - Export completes successfully with all selected data
   - Exported file can be imported back without data loss
   - User can cancel in-progress export

6. **Open Questions** (document):
   - What data fields to include in each format?
   - Size limits for export?
   - Audit trail requirements?
   - Mobile-specific considerations (storage permissions, file sharing)?
